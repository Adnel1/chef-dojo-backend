from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter
from sqlalchemy.orm import Session
from ..models import User
from ..database import get_db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

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
    email = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.email == email).first()
    
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Bad email or password")
    
    access_token = create_access_token(identity=email)
    return {"access_token": access_token, "user_id": user.id}

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