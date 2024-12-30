from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Depends
from langchain.schema import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from models.bot import Chatbot
from uuid import uuid4
import os

import json
from dotenv import load_dotenv
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional

load_dotenv() 

app = FastAPI()

# Database setup 
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

# Define User model

# Define Chatbot model

SQLModel.metadata.create_all(engine)

# Dependency to get DB session
def get_session():
    with Session(engine) as session:
        yield session

# Initialize LLM and memory
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
memory = ConversationBufferWindowMemory(k=5)

# Function to create a persona-based prompt
def create_prompt(persona_settings, user_query):
    template = """
    You are {persona_name}, {description}.
    Your personality is {personality}, and your tone is {tone}.
    Respond to the user query below:

    User: {user_query}
    """
    prompt = PromptTemplate(
        input_variables=["persona_name", "description", "personality", "tone", "user_query"],
        template=template,
    )
    return prompt.format(
        persona_name=persona_settings["name"],
        description=persona_settings["description"],
        personality=persona_settings["personality"],
        tone=persona_settings["tone"],
        user_query=user_query,
    )

# AI Router
ai_router = APIRouter(prefix="/ai")

@ai_router.post("/upload_file/{name}/{description}/{tone}/{personality}")
async def upload_file(name: str, description: str, tone: str, personality: str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    chatbot_id = str(uuid4())

    try:
        # Save the uploaded file content to the database
        content = await file.read()
        text = content.decode("utf-8")

        # Save chatbot metadata in the database
        chatbot = Chatbot(
            id=chatbot_id,
            name=name,
            description=description,
            tone=tone,
            personality=personality,
            index_file_path=text  # Save the text content directly in the database
        )
        session.add(chatbot)
        session.commit()

        return {"message": "Chatbot created successfully", "chatbot_id": chatbot_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the uploaded file: {str(e)}")
@ai_router.post("/ask/{chatbot_id}")
async def ask_question(chatbot_id: str, question: str, session: Session = Depends(get_session)):
    # Fetch the chatbot from the database
    chatbot = session.exec(select(Chatbot).where(Chatbot.id == chatbot_id)).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # Create a persona-based prompt
    persona_settings = {
        "name": chatbot.name,
        "description": chatbot.description,
        "personality": chatbot.personality,
        "tone": chatbot.tone,
    }
    prompt = create_prompt(persona_settings, question)

    # Process the text stored in the database directly
    text = chatbot.index_file_path
    document = Document(page_content=text)

    # Configure embeddings and text splitter
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    # Create the index using the Document object
    index_creator = VectorstoreIndexCreator(embedding=embedding, text_splitter=text_splitter)
    index = index_creator.from_documents([document])

    # Query the index
    response = index.query(prompt , llm=llm)

    return {"response": response}
# Endpoint to get a list of all chatbots
@ai_router.get("/chatbots")
async def get_all_chatbots(session: Session = Depends(get_session)):
    chatbots = session.exec(select(Chatbot)).all()
    return {"chatbots": chatbots}

# Endpoint to update a chatbot
@ai_router.put("/chatbots/{chatbot_id}")
async def update_chatbot(chatbot_id: str, name: str, description: str, tone: str, personality: str, session: Session = Depends(get_session)):
    chatbot = session.exec(select(Chatbot).where(Chatbot.id == chatbot_id)).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    chatbot.name = name
    chatbot.description = description
    chatbot.tone = tone
    chatbot.personality = personality

    session.add(chatbot)
    session.commit()

    return {"message": "Chatbot updated successfully"}

# Endpoint to delete a chatbot
@ai_router.delete("/chatbots/{chatbot_id}")
async def delete_chatbot(chatbot_id: str, session: Session = Depends(get_session)):
    chatbot = session.exec(select(Chatbot).where(Chatbot.id == chatbot_id)).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    session.delete(chatbot)
    session.commit()

    return {"message": "Chatbot deleted successfully"}

app.include_router(ai_router)
