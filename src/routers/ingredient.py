from fastapi import FastAPI, HTTPException, Request, APIRouter
import os
import requests
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Define a Pydantic model for the search query
class SearchQuery(BaseModel):
    query: str

# Define a Pydantic model for the flattened food response
class FlattenedFood(BaseModel):
    name: str
    id: int
    carbohydrates_unit: str = None
    carbohydrates_value: float = None
    fat_unit: str = None
    fat_value: float = None
    protein_unit: str = None
    protein_value: float = None
    calories_unit: str = None
    calories_value: float = None
    sugars_unit: str = None
    sugars_value: float = None
    fiber_unit: str = None
    fiber_value: float = None
    sodium_unit: str = None
    sodium_value: float = None
    cholesterol_unit: str = None
    cholesterol_value: float = None

# Endpoint for ingredient search feature
@router.post('/search', response_model=List[FlattenedFood])
async def search(query: SearchQuery, request: Request):
    # Define a dictionary to map original nutrient names to custom property names
    custom_property_names = {
        "Carbohydrate, by difference": "carbohydrates",
        "Total lipid (fat)": "fat",
        "Protein": "protein",
        "Energy": "calories",
        "Sugars, total including NLEA": "sugars",
        "Fiber, total dietary": "fiber",
        "Sodium, Na": "sodium",
        "Cholesterol": "cholesterol"
    }

    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    payload = {
        "query": query.query
    }

    # Prepare the request headers
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": os.environ["API_KEY"],
    }

    try:
        response = requests.post(search_url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        # Flatten the payload to only include desired fields and filter duplicates
        if 'foods' in response_data:
            flattened_foods = []
            seen_names = set()
            
            for food in response_data['foods']:
                name = food.get("description")
                if name not in seen_names:
                    seen_names.add(name)
                    flattened_food = {
                        "name": name,
                        "id": food.get("fdcId")
                    }

                    for foodNutrient in food["foodNutrients"]:
                        nutrient_name = foodNutrient["nutrientName"]
                        if nutrient_name in custom_property_names:
                            custom_property_name = custom_property_names[nutrient_name]
                            flattened_food[f"{custom_property_name}_unit"] = foodNutrient["unitName"]
                            flattened_food[f"{custom_property_name}_value"] = foodNutrient["value"]

                    flattened_foods.append(flattened_food)
            
            return flattened_foods
    
    except requests.RequestException as e:
        print(f"Error fetching data from USDA API: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data from API.")

# Initialize FastAPI app and include router
app = FastAPI()
app.include_router(router)
