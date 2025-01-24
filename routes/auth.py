from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status , Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from schemas.user import UserCreate, UserResponse, Token
from models.user import User
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from db import get_session
from sqlmodel import select
import pandas as pd
from fastapi.responses import StreamingResponse
import io
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
auth_router = APIRouter(prefix = "/auth")
 
# Signup Endpoint
@auth_router.post("/signup", response_model=UserResponse)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    user_exists = session.exec(select(User).where(User.email == user_create.email)).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create user
    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        name=user_create.name,
        country=user_create.country,
        phone_no=user_create.phone_no,
        address=user_create.address
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Send confirmation email
    sender_email = "raibadar37218@gmail.com"
    receiver_email = user_create.email
    password = "aqojinprzpqfhlxk"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to Funded Horizon"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Hello {user_create.name},\n\nThank you for signing up at Funded Horizon"
    part = MIMEText(text, "plain")
    message.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

    return new_user

# Login Endpoint
#NOTE: You have to tell the frontend developer that he has to send the email in the key of username and should ask from the user the email but put it against the username key in the header.
@auth_router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)], session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Token Refresh Endpoint
@auth_router.post("/token/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": str(current_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


    # Get All Users Endpoint
@auth_router.get("/users", response_model=List[UserResponse])
def get_all_users(session: Session = Depends(get_session)):
        users = session.exec(select(User)).all()
        return users


    # Get Current User Details Endpoint
@auth_router.get("/user/me", response_model=UserResponse)
def get_current_user_details(current_user: User = Depends(get_current_user)):
        return current_user