from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def index():
    return {"name": "First Data"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/user")
async def create_user(request: Request, db: Session = Depends(get_db)):
    # Parse the JSON request body
    request_json = await request.json()
    email = request_json.get("email")
    password = request_json.get("password")

    # Validate email and password
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Check if the user already exists
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        raise HTTPException(status_code=404, detail="User already found with this email")

    # Create the user and commit to the database
    db_user = models.User(email=email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Optional: refresh to get the new user ID

    return {"email": db_user.email, "message": "User created successfully"}

#Get all users
@app.get('/users')
def get_all_users(db: Session = Depends(get_db)):

    try:
        users = db.query(models.User).all()
        serialized_users = [user.serialize() for user in users] 
        return {"users": serialized_users}, 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")