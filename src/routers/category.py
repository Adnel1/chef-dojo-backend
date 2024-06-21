from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import User_Category
from pydantic import BaseModel

router = APIRouter()

# Pydantic models
class CategoryCreate(BaseModel):
    category_name: str

class Category(BaseModel):
    user_id: int
    category_id: int
    category_name: str

    class Config:
        orm_mode = True

# Create category for a user
@router.post("/categories/{user_id}", response_model=Category)
async def create_category(user_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    if category.category_name is None:
        raise HTTPException(status_code=400, detail="Please fill out the required fields")
    
    user_category = User_Category(user_id=user_id, category_name=category.category_name)
    db.add(user_category)
    db.commit()
    db.refresh(user_category)

    return user_category

# Get category from a user
@router.get("/categories/{user_id}", response_model=List[Category])
async def get_categories(user_id: int, db: Session = Depends(get_db)):
    user_categories = db.query(User_Category).filter_by(user_id=user_id).all()

    if not user_categories:
        raise HTTPException(status_code=404, detail="There are no categories for this user")
    
    return user_categories

# Delete user category
@router.delete("/categories/{user_id}/{category_id}")
async def delete_category(user_id: int, category_id: int, db: Session = Depends(get_db)):
    user_category = db.query(User_Category).filter_by(user_id=user_id, category_id=category_id).first()

    if user_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(user_category)
    db.commit()

    return {"msg": "Category deleted successfully"}
