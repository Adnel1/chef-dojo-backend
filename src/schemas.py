from pydantic import BaseModel
from typing import Optional

class UserRecipeBase(BaseModel):
    recipe_name: str
    description: Optional[str] = None
    ingredients: str
    directions: str

    class Config:
        orm_mode = True

class UserRecipeCreate(UserRecipeBase):
    pass

class UserRecipe(UserRecipeBase):
    recipe_id: int
    user_id: int
    category_id: int

    class Config:
        orm_mode = True

class UserCategoryBase(BaseModel):
    user_id: int
    category_name: str

    class Config:
        orm_mode = True

class UserCategory(UserCategoryBase):
    category_id: int