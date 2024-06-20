from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter
from sqlalchemy.orm import Session
import models
from database import get_db
from dotenv import load_dotenv
import os

router = APIRouter()

@router.post("/user")
async def create_user(request: Request, db: Session = Depends(get_db)):
    request_json = await request.json()
    email = request_json.get("email")
    password = request_json.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        raise HTTPException(status_code=404, detail="User already found with this email")

    db_user = models.User(email=email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"email": db_user.email, "message": "User created successfully"}

@router.get('/users')
def get_all_users(db: Session = Depends(get_db)):
    try:
        users = db.query(models.User).all()
        serialized_users = [user.serialize() for user in users]
        return {"users": serialized_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
