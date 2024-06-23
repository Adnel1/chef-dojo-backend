from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter
from sqlalchemy.orm import Session
from ..models import User
from ..database import get_db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY is not set in the environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(identity: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": identity, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Sign up user
@router.post("/signup")
async def create_user(request: Request, db: Session = Depends(get_db)):
    request_json = await request.json()
    email = request_json.get("email")
    password = request_json.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists with this email")

    hashed_password = pwd_context.hash(password)
    db_user = User(email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"email": db_user.email, "message": "User created successfully"}

# Create a route to authenticate your users and return JWTs.
@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        email = form_data.username
        password = form_data.password

        print("Received email:", email)  # Log received email
        print("Received password:", password)  # Log received password

        user = db.query(User).filter(User.email == email).first()
        print("Queried user:", user)  # Log queried user
        
        if not user:
            print("User not found")
            raise HTTPException(status_code=401, detail="Bad email or password")
        
        if not pwd_context.verify(password, user.password):
            print("Password verification failed")
            raise HTTPException(status_code=401, detail="Bad email or password")
        
        access_token = create_access_token(identity=email)
        print("Created access token:", access_token)  # Log created access token
        return {"access_token": access_token, "user_id": user.id}
    except Exception as e:
        print(f"Error occurred: {e}")  # Log any exception
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get all users
@router.get('/users')
async def get_all_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        serialized_users = [user.serialize() for user in users]
        return {"users": serialized_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Initialize FastAPI app and include router
app = FastAPI()
app.include_router(router)
