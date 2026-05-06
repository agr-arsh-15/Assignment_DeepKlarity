from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx

from database import get_db, engine
import models
import scraper
import llm_service

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Extractor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractRequest(BaseModel):
    url: str

class MealPlanRequest(BaseModel):
    recipe_ids: list[int]

@app.get("/")
def root():
    return {"message": "Recipe Extractor API is running"}

@app.post("/extract")
def extract_recipe(request: ExtractRequest, db: Session = Depends(get_db)):
    """
    Main endpoint:
    1. Scrape the recipe blog URL
    2. Send scraped text to Gemini LLM
    3. Store result in PostgreSQL
    4. Return structured JSON
    """
    url = request.url.strip()

    existing = db.query(models.Recipe).filter(models.Recipe.url == url).first()
    if existing:
        return existing.to_dict()

    try:
        page_text = scraper.scrape_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

    if not page_text or len(page_text) < 100:
        raise HTTPException(status_code=422, detail="Page has too little content. It may not be a recipe page.")

    try:
        recipe_data = llm_service.extract_recipe(page_text, url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {str(e)}")

    try:
        db_recipe = models.Recipe.from_dict(recipe_data)
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/recipes")
def get_all_recipes(db: Session = Depends(get_db)):
    """Return all previously extracted recipes for history tab."""
    recipes = db.query(models.Recipe).order_by(models.Recipe.created_at.desc()).all()
    return [r.to_dict() for r in recipes]


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Return a single recipe by ID for the details modal."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe.to_dict()
