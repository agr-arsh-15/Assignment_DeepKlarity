import os
import json
import re
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

RECIPE_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["page_text", "url"],
    template="""
You are a recipe extraction assistant. Read the scraped text from a recipe blog and return a structured JSON object.

SCRAPED PAGE TEXT:
{page_text}

SOURCE URL: {url}

INSTRUCTIONS:
- Extract all recipe information directly from the text. Do NOT invent information.
- If a field is not found, use null or empty list/object.
- For nutrition_estimate: provide reasonable approximations based on the ingredients.
- For substitutions: suggest 3 practical ingredient swaps for this specific recipe.
- For shopping_list: group ingredients by category (dairy, produce, pantry, bakery, meat, spices, etc.)
- For related_recipes: suggest 3 recipes that pair well with this dish.
- difficulty must be one of: "easy", "medium", "hard"
- servings must be an integer
- Return ONLY valid JSON. No markdown, no explanation, no code fences.

REQUIRED JSON FORMAT:
{{
  "title": "string",
  "cuisine": "string",
  "prep_time": "string",
  "cook_time": "string",
  "total_time": "string",
  "servings": integer,
  "difficulty": "easy|medium|hard",
  "ingredients": [
    {{"quantity": "string", "unit": "string", "item": "string"}}
  ],
  "instructions": ["step 1", "step 2"],
  "nutrition_estimate": {{
    "calories": integer,
    "protein": "string",
    "carbs": "string",
    "fat": "string"
  }},
  "substitutions": ["sub 1", "sub 2", "sub 3"],
  "shopping_list": {{
    "category": ["item1", "item2"]
  }},
  "related_recipes": ["recipe 1", "recipe 2", "recipe 3"]
}}
"""
)


def get_llm_instance():
    """
    Dynamically initializes an LLM instance based on available environment variables.
    Supports Groq, OpenAI, Google Gemini, and Ollama.
    """
    provider = os.getenv("LLM_PROVIDER", "").lower()

    # 1. Groq (Default)
    groq_key = os.getenv("GROQ_API_KEY")
    if provider == "groq" or (not provider and groq_key and not groq_key.startswith("your_")):
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=0.2,
        )

    # 2. OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if provider == "openai" or (not provider and openai_key and not openai_key.startswith("your_")):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_key,
            temperature=0.2,
        )

    # 3. Google Gemini
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if provider in ("gemini", "google") or (not provider and gemini_key and not gemini_key.startswith("your_")):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_key,
            temperature=0.2,
        )

    # 4. Ollama (Local zero-key model)
    if provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model="llama3",
            temperature=0.2,
        )

    # Check for placeholder key error handling
    if groq_key and groq_key.startswith("your_"):
        raise ValueError(
            "Please configure your API key in backend/.env!\n"
            "Replace 'your_groq_api_key_here' with your actual Groq key from https://console.groq.com/keys "
            "or provide an OPENAI_API_KEY / GEMINI_API_KEY."
        )

    raise ValueError(
        "No valid LLM API key detected. Please configure GROQ_API_KEY, OPENAI_API_KEY, "
        "or GEMINI_API_KEY in your backend/.env file."
    )


def extract_recipe(page_text: str, url: str) -> dict:
    """
    Extract structured recipe JSON from scraped text using the configured LLM.
    """
    llm = get_llm_instance()
    chain = RECIPE_EXTRACTION_PROMPT | llm | StrOutputParser()
    raw_output = chain.invoke({"page_text": page_text, "url": url})

    # Strip accidental markdown fences
    raw_output = re.sub(r"```(?:json)?", "", raw_output).strip().rstrip("`").strip()

    try:
        recipe_data = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise Exception(f"LLM returned invalid JSON: {str(e)}\nRaw output: {raw_output[:300]}")

    recipe_data["url"] = url
    return recipe_data