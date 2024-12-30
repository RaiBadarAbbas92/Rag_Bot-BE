from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Depends
import os
from routes.auth import auth_router
from routes.chat import ai_router

app = FastAPI()
app.include_router(auth_router) 
app.include_router(ai_router)  
 
@app.get("/") 
def read_root():
    return {"Welcome to ": "Multi CHATbOT CREATIOR"}  