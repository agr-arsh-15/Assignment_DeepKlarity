from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db, engine
import models
import scraper
import llm_service

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recipe Extractor API",
    description="Extract structured recipe metadata from any recipe blog URL using AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {
        "message": "Recipe Extractor API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.post("/extract")
def extract_recipe(request: ExtractRequest, db: Session = Depends(get_db)):
    """
    Extract structured recipe data from a URL:
    1. Scrape plain text from the URL
    2. Extract structured JSON using configured LLM (Groq / OpenAI / Gemini / Ollama)
    3. Persist output in database (PostgreSQL / SQLite)
    4. Return structured JSON
    """
    url = request.url.strip()

    # Check if URL was already extracted
    existing = db.query(models.Recipe).filter(models.Recipe.url == url).first()
    if existing:
        return existing.to_dict()

    # Step 1: Scrape URL with SSRF protection
    try:
        page_text = scraper.scrape_url(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

    if not page_text or len(page_text) < 100:
        raise HTTPException(
            status_code=422,
            detail="Page content is too brief or invalid. It may not be a recipe blog post."
        )

    # Step 2: LLM extraction
    try:
        recipe_data = llm_service.extract_recipe(page_text, url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {str(e)}")

    # Step 3: Database persistence
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
    """Return all previously extracted recipes ordered by recency."""
    recipes = db.query(models.Recipe).order_by(models.Recipe.created_at.desc()).all()
    return [r.to_dict() for r in recipes]


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Return a single recipe by its database ID."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe.to_dict()
