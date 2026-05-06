import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.2,
)

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

def extract_recipe(page_text: str, url: str) -> dict:
    prompt = RECIPE_EXTRACTION_PROMPT
    chain = prompt | llm | StrOutputParser()
    raw_output = chain.invoke({"page_text": page_text, "url": url})

    # Strip accidental markdown fences
    raw_output = re.sub(r"```(?:json)?", "", raw_output).strip().rstrip("`").strip()

    try:
        recipe_data = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise Exception(f"LLM returned invalid JSON: {str(e)}\nRaw: {raw_output[:300]}")

    recipe_data["url"] = url
    return recipe_data