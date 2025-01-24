# from fastapi import BackgroundTasks , FastAPI
# from pydantic import BaseModel
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlmodel import Field, SQLModel, Session, create_engine, select
from routes.auth import auth_router
from routes.order import order_router
from routes.meta import meta_router
from db import create_db_and_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()
    print("Table created")
    try:
        yield
    finally:
        print("Lifespan context ended")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(meta_router)

@app.get("/")
def read_root():
    return {"Welcome to ": "Multi CHATbOT CREATIOR"}



# class EmailSchema(BaseModel):
#     email: str
#     subject: str
#     message: str
# app = FastAPI()
# def send_email(email: str, subject: str, message: str):
#     sender_email = "raibadar37218@gmail.com"
#     receiver_email = email
#     password = "aqojinprzpqfhlxk"

#     msg = MIMEMultipart()
#     msg["From"] = sender_email
#     msg["To"] = receiver_email
#     msg["Subject"] = subject

#     msg.attach(MIMEText(message, "plain"))

#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, msg.as_string())
#     except Exception as e:
#         print(f"Error: {e}")

# @app.post("/send-email/")
# async def send_email_endpoint(email: EmailSchema, background_tasks: BackgroundTasks):
#     background_tasks.add_task(send_email, email.email, email.subject, email.message)
#     return {"message": "Email has been sent"}