from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Depends
import os
from sqlmodel import Field, SQLModel, Session, create_engine, select
from routes.auth import auth_router
from routes.chat import ai_router
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



app.include_router(auth_router) 
app.include_router(ai_router)  
 
@app.get("/") 
def read_root():
    return {"Welcome to ": "Multi CHATbOT CREATIOR"}  