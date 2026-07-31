# 🍳 Recipe Extractor & Smart Meal Planner

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/Groq-Supported-F55036?style=for-the-badge" alt="Groq" />
  <img src="https://img.shields.io/badge/OpenAI-Supported-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Gemini-Supported-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Gemini" />
  <img src="https://img.shields.io/badge/PostgreSQL-Supported-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQLite-Supported-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT" />
</p>

A full-stack, AI-powered web application that turns any recipe blog URL into structured data. It scrapes web pages, uses Large Language Models (Groq, OpenAI, Google Gemini, or Ollama) via LangChain to extract recipe components, generates nutritional approximations, categorizes ingredients for shopping, and stores everything in PostgreSQL or SQLite.

---

## ✨ Features

- 🌐 **Web Scraping with SSRF Protection**: Extracts clean content from recipe blogs while blocking internal/private IP targets.
- 🤖 **Bring Your Own LLM**: Native plug-and-play support for **Groq** (free tier), **OpenAI (GPT-4o-mini)**, **Google Gemini**, or local **Ollama** models.
- 🥗 **Structured Data Extraction**:
  - Exact ingredient quantities, units, and item names.
  - Step-by-step cooking instructions.
  - Nutritional estimates (Calories, Protein, Carbs, Fat).
  - Practical ingredient substitution recommendations.
  - Smart category-grouped shopping lists (Produce, Dairy, Pantry, Meat, Spices, Bakery).
  - Related recipe pairings.
- 💾 **Dual Database Engine**: Works with PostgreSQL (production) or auto-falls back to zero-config SQLite.
- 🎨 **Modern Dark Glassmorphism UI**: Beautiful, single-file frontend with interactive tabs, history modal, shopping list toggles, and micro-animations.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[User / Web Browser] -->|Pastes Recipe URL| B[Frontend HTML/JS]
    B -->|POST /extract| C[FastAPI Backend]
    C -->|Validate URL & SSRF Check| D[Scraper Module BeautifulSoup4]
    D -->|Scraped HTML Text| E[LangChain Engine]
    E -->|Bring Your Own Key| F{LLM Provider}
    F -->|Default| G[Groq LLaMA 3.3-70B]
    F -->|Option| H[OpenAI GPT-4o-mini]
    F -->|Option| I[Google Gemini 1.5-Flash]
    F -->|Option| J[Local Ollama LLaMA3]
    E -->|Structured Recipe JSON| C
    C -->|Store Recipe| K[(PostgreSQL / SQLite)]
    C -->|Return Response| B
```

---

## 🔑 Bring Your Own LLM (API Key Setup)

This repository is designed so **anyone can clone it, paste their own API key into `.env`, and start extracting recipes immediately**.

### 1. Copy Environment Template
In your terminal, navigate to the `backend/` folder and copy `.env.example` to `.env`:

```bash
cd backend
cp .env.example .env
```

### 2. Add Your Preferred API Key

Open `backend/.env` in any text editor and fill in **one** of the following keys:

| Provider | Get Key | `.env` Setting Example |
|---|---|---|
| **Groq (Recommended - Free & Fast)** | [console.groq.com/keys](https://console.groq.com/keys) | `GROQ_API_KEY=gsk_your_actual_key_here` |
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | `OPENAI_API_KEY=sk-proj-your_actual_key_here` |
| **Google Gemini** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | `GEMINI_API_KEY=AIzaSy_your_actual_key_here` |
| **Ollama (Local / No Key)** | Install [Ollama](https://ollama.com) & run `ollama run llama3` | `LLM_PROVIDER=ollama` |

> 🔒 **Security Guarantee**: The `.env` file is included in `.gitignore` and will **never** be committed to Git. Your API key remains 100% private to your local machine.

---

## ⚡ Quickstart Guide

### Method 1: Instant Zero-Config Mode (SQLite)

No Docker or PostgreSQL required!

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/recipe-extractor.git
cd recipe-extractor/backend

# 2. Create virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Create your .env file and add your API key
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY

# 4. Start the FastAPI server
uvicorn main:app --reload --port 8000
```

Open `frontend/index.html` directly in your browser.

---

### Method 2: Full-Stack Docker & PostgreSQL

```bash
# 1. Start PostgreSQL container
docker run --name recipe-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=recipe_db \
  -p 5432:5432 \
  -d postgres

# 2. Configure backend environment
cd backend
cp .env.example .env
# Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recipe_db
# Set your API key (GROQ_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY)

# 3. Install dependencies & start server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open `frontend/index.html` in your browser.

---

## 📂 Project Structure

```
recipe-extractor/
├── backend/
│   ├── main.py              # FastAPI router & endpoint definitions
│   ├── database.py          # SQLAlchemy ORM + SQLite fallback engine
│   ├── models.py            # Recipe database schema
│   ├── scraper.py           # BeautifulSoup4 scraper + SSRF security
│   ├── llm_service.py       # LangChain multi-provider LLM bridge
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment template for clone users
│   └── .env                 # Local secrets (git-ignored)
├── frontend/
│   ├── index.html           # Modern dark UI (HTML + CSS + Vanilla JS)
│   ├── favicon.ico          # Application favicon
│   └── favicon.png          # High-res favicon PNG
├── prompts/
│   └── prompt_templates.md  # LLM prompt specification and design rationale
├── sample_data/
│   ├── sample_urls.md       # Pre-tested recipe URLs for verification
│   └── *_output.json        # Pre-extracted JSON samples
├── .gitignore               # Strict git exclusion rules
├── LICENSE                  # Open-source MIT License
└── README.md                # Project documentation
```

---

## 📡 REST API Reference

### 1. Health Check
`GET /`
```json
{
  "message": "Recipe Extractor API is running",
  "docs": "/docs",
  "version": "1.0.0"
}
```

### 2. Extract Recipe
`POST /extract`

**Request Body:**
```json
{
  "url": "https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "url": "https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/",
  "title": "Grilled Cheese Sandwich",
  "cuisine": "American",
  "prep_time": "5 mins",
  "cook_time": "10 mins",
  "total_time": "15 mins",
  "servings": 2,
  "difficulty": "easy",
  "ingredients": [
    { "quantity": "4", "unit": "slices", "item": "white bread" },
    { "quantity": "3", "unit": "tbsp", "item": "butter, divided" },
    { "quantity": "2", "unit": "slices", "item": "Cheddar cheese" }
  ],
  "instructions": [
    "Butter one side of a slice of bread.",
    "Place bread butter-side down onto hot skillet; add 1 slice of cheese.",
    "Butter a second slice of bread on one side and place butter-side up on top of cheese.",
    "Grill until lightly browned and flip; continue cooking until cheese is melted."
  ],
  "nutrition_estimate": {
    "calories": 400,
    "protein": "12g",
    "carbs": "30g",
    "fat": "26g"
  },
  "substitutions": [
    "Swap Cheddar for Swiss or Gruyère for a deeper flavor",
    "Use sourdough bread instead of white bread",
    "Add sliced tomato or bacon"
  ],
  "shopping_list": {
    "bakery": ["white bread"],
    "dairy": ["butter", "Cheddar cheese"]
  },
  "related_recipes": [
    "Tomato Soup",
    "Garlic Butter Toast",
    "Classic BLT Sandwich"
  ],
  "created_at": "2026-07-31T22:50:00.000Z"
}
```

### 3. Get All Recipes
`GET /recipes` — Returns history array of stored recipes.

### 4. Get Single Recipe
`GET /recipes/{id}` — Returns detail object for modal view.

---

## 🔒 Security & Privacy Features

- 🛑 **SSRF Prevention**: `scraper.py` parses URLs and blocks local loopback IPs (`127.0.0.1`, `localhost`), metadata addresses (`169.254.169.254`), private networks (`10.x.x.x`, `192.168.x.x`, `172.16.x.x`), and non-HTTP protocols.
- 🔑 **Zero Key Leakage**: Personal keys are never saved in source code. All secrets are loaded from `.env` which is strictly ignored by Git.
- 🛡️ **Clean Input Handling**: Validates payload structures using Pydantic schemas.

---

## 🧪 Sample Tested URLs

Test the extractor with these verified blog posts:

| Recipe | URL | Expected Difficulty |
|---|---|---|
| **Grilled Cheese** | `https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/` | Easy |
| **Chicken Tikka** | `https://www.allrecipes.com/recipe/228293/curry-stand-chicken-tikka-masala-sauce/` | Medium |
| **Beef Lasagna** | `https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/` | Hard |
| **Homemade Pizza** | `https://www.simplyrecipes.com/recipes/homemade_pizza/` | Medium |

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](file:///Users/arshagrawal15/recipe-extractor/LICENSE) file for details.