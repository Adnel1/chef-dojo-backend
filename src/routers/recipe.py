from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User_Category, User_Recipe
from ..schemas import UserRecipe, UserRecipeCreate

router = APIRouter()

@router.post('/recipes/{user_id}/{category_id}', response_model=UserRecipe, status_code=status.HTTP_201_CREATED)
def create_recipe(user_id: int, category_id: int, recipe: UserRecipeCreate, db: Session = Depends(get_db)):
    # Check if the category_id exists in the user_category table
    category = db.query(User_Category).filter_by(category_id=category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category does not exist")

    # Create a new User_Recipe instance
    user_recipe = User_Recipe(
        user_id=user_id,
        category_id=category_id,
        recipe_name=recipe.recipe_name,
        description=recipe.description,
        ingredients=recipe.ingredients,
        directions=recipe.directions
    )

    # Add the new recipe instance to the database session and commit the changes
    db.add(user_recipe)
    db.commit()
    db.refresh(user_recipe)

    return user_recipe

@router.get('/recipes/{user_id}/{category_id}', response_model=List[UserRecipe])
def get_recipes_by_category(user_id: int, category_id: int, db: Session = Depends(get_db)):
    # Query the User_Recipe table to get recipes for the specified user and category
    recipes = db.query(User_Recipe).filter_by(user_id=user_id, category_id=category_id).all()
    
    # Check if any recipes are found
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found for this user and category")
    
    return recipes

@router.get('/recipes/{recipe_id}', response_model=UserRecipe)
def get_recipe_by_id(recipe_id: int, db: Session = Depends(get_db)):
    # Query the User_Recipe table to get the recipe with the specified ID
    recipe = db.query(User_Recipe).filter_by(recipe_id=recipe_id).first()

    # Check if the recipe is found
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

@router.delete('/recipes/{recipe_id}', response_model=dict)
def delete_recipe_by_id(recipe_id: int, db: Session = Depends(get_db)):
    # Query the User_Recipe table to get the recipe with the specified ID
    recipe = db.query(User_Recipe).filter_by(recipe_id=recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(recipe)
    db.commit()

    return {"msg": "Recipe deleted successfully"}
