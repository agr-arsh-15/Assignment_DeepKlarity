from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, unique=True, index=True, nullable=False)
    title = Column(String(500))
    cuisine = Column(String(200))
    prep_time = Column(String(100))
    cook_time = Column(String(100))
    total_time = Column(String(100))
    servings = Column(Integer)
    difficulty = Column(String(50))

    ingredients = Column(JSON)         
    instructions = Column(JSON)         
    nutrition_estimate = Column(JSON)  
    substitutions = Column(JSON)        
    shopping_list = Column(JSON)        
    related_recipes = Column(JSON)      

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Create a Recipe model instance from the LLM-returned dictionary."""
        return cls(
            url=data.get("url", ""),
            title=data.get("title", ""),
            cuisine=data.get("cuisine", ""),
            prep_time=data.get("prep_time", ""),
            cook_time=data.get("cook_time", ""),
            total_time=data.get("total_time", ""),
            servings=data.get("servings"),
            difficulty=data.get("difficulty", ""),
            ingredients=data.get("ingredients", []),
            instructions=data.get("instructions", []),
            nutrition_estimate=data.get("nutrition_estimate", {}),
            substitutions=data.get("substitutions", []),
            shopping_list=data.get("shopping_list", {}),
            related_recipes=data.get("related_recipes", []),
        )

    def to_dict(self) -> dict:
        """Serialize the model to a JSON-safe dictionary for API responses."""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "cuisine": self.cuisine,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "total_time": self.total_time,
            "servings": self.servings,
            "difficulty": self.difficulty,
            "ingredients": self.ingredients or [],
            "instructions": self.instructions or [],
            "nutrition_estimate": self.nutrition_estimate or {},
            "substitutions": self.substitutions or [],
            "shopping_list": self.shopping_list or {},
            "related_recipes": self.related_recipes or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
