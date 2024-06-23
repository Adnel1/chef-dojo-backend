import os
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine, SessionLocal, get_db
from .routers import user, category

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Allow CORS for all origins (you can restrict this as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify specific origins here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(category.router)

@app.get("/")
def index():
    return "Server is running!"

db_dependency = Annotated[Session, Depends(get_db)]
