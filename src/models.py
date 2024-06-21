from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

# Every table in the database will have its corresponding model

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False)
    # Make sure to hash the password before saving it
    password = Column(String(80), unique=False, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password
        }

    def __repr__(self):
        return '<User %r>' % self.email
    
class User_Category(Base):
    __tablename__ = "user_category"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(90), nullable=False)
    recipes = relationship('User_Recipe', backref='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User_Category {self.category_id}>'
    
    def serialize(self):
        return {
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category_name
        }
    
class User_Recipe(Base):
    __tablename__ = "user_recipe"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("user_category.category_id"), nullable=False)
    recipe_id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_name = Column(String, nullable=False)
    description = Column(String(240), nullable=True)
    ingredients = Column(String, nullable=False)
    directions = Column(String, nullable=False)

    def __repr__(self):
        return f'<User_Recipe {self.recipe_id}>'
   
    def serialize(self):
        return {
            "user_id": self.user_id,
            "category_id": self.category_id,
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "description": self.description,
            "ingredients": self.ingredients,
            "directions": self.directions,
        }