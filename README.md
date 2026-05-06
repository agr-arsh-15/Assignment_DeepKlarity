# Recipe Extractor

A full-stack web application that accepts a recipe blog URL, scrapes its content using BeautifulSoup, extracts structured recipe data using Groq (via LangChain), and stores everything in PostgreSQL.

---

## Project Structure

```
recipe-extractor/
├── backend/
│   ├── main.py           # FastAPI app — all routes
│   ├── database.py       # SQLAlchemy DB connection
│   ├── models.py         # Recipe table model
│   ├── scraper.py        # BeautifulSoup scraper
│   ├── llm_service.py    # LangChain + Groq integration
│   ├── requirements.txt  # Python dependencies
│   └── .env              # API keys and DB URL (fill this in)
├── frontend/
│   └── index.html        # Complete single-file frontend (no build required)
├── prompts/
│   └── prompt_templates.md  # LangChain prompt templates with design notes
├── sample_data/
│   ├── sample_urls.md                    # Test URLs used
│   ├── grilled_cheese_output.json
│   ├── chicken_tikka_output.json
│   ├── german_chocolate_cake_output.json
│   ├── homemade_pizza_output.json
│   └── lasagna_output.json
└── README.md
```

---

## Prerequisites

- Python 3.10 or higher
- Docker installed and running
- A free Groq API key → https://console.groq.com/keys

---

## Setup Instructions

### Step 1 — Start PostgreSQL with Docker

```bash
docker run --name recipe-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=recipe_db \
  -p 5432:5432 \
  -d postgres
```

> Replace `your_password` with a password of your choice. Keep it consistent with your `.env` file.

### Step 2 — Configure Environment Variables

Edit `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/recipe_db
```

> Replace `your_password` with the same password used in Step 1.

### Step 3 — Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4 — Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

The database tables are created automatically on first startup.

### Step 5 — Open the Frontend

Simply open `frontend/index.html` in your browser. No build step needed.

---

## API Endpoints

| Method | Endpoint        | Description                                   |
|--------|-----------------|-----------------------------------------------|
| GET    | `/`             | Health check — confirms API is running        |
| POST   | `/extract`      | Scrape URL, extract recipe with Groq, save it |
| GET    | `/recipes`      | Return all saved recipes (history tab)        |
| GET    | `/recipes/{id}` | Return a single recipe by ID (details modal)  |

### POST `/extract` — Request Body
```json
{ "url": "https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/" }
```

---

## Interactive API Docs

FastAPI auto-generates documentation. With the backend running, open:
- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

---

## Testing Steps

1. Start the backend with `uvicorn main:app --reload`
2. Open `frontend/index.html` in your browser
3. Paste a recipe URL from `sample_data/sample_urls.md` into the input field
4. Click **Extract Recipe** — wait 15–30 seconds for scraping + Groq response
5. View the structured output (ingredients, nutrition, substitutions, shopping list, related recipes)
6. Switch to the **Saved Recipes** tab to see the history table
7. Click **Details** on any row to open the modal

### Tested URLs

| URL | Expected Difficulty |
|-----|---------------------|
| https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/ | easy |
| https://www.allrecipes.com/recipe/228293/curry-stand-chicken-tikka-masala-sauce/ | medium |
| https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/ | hard |
| https://www.allrecipes.com/recipe/7016/homemade-pizza/ | medium |
| https://www.allrecipes.com/recipe/17869/german-chocolate-cake/ | hard |

---

## Error Handling

| Scenario | API Response |
|----------|--------------|
| Invalid or unreachable URL | 400 — Failed to scrape URL |
| Page has no recipe content | 422 — Page has too little content |
| Groq returns malformed JSON | 500 — LLM extraction failed |
| Recipe ID not found | 404 — Recipe not found |

---

## Technical Stack

| Component  | Technology                            |
|------------|---------------------------------------|
| Backend    | FastAPI + Uvicorn                     |
| Database   | PostgreSQL via SQLAlchemy ORM (Docker)|
| Frontend   | Plain HTML + CSS + Vanilla JavaScript |
| LLM        | Groq (free tier)                      |
| LLM Bridge | LangChain (LLMChain + PromptTemplate) |
| Scraping   | requests + BeautifulSoup4             |