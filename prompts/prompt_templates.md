## 1. Recipe Extraction Prompt
**Used in:** `llm_service.py` → `extract_recipe()`
**Purpose:** Extracts structured recipe data, generates nutrition estimate, substitutions, shopping list, and related recipes from raw scraped text.

```
You are a recipe extraction assistant. Your job is to read scraped text from a recipe blog page and return a structured JSON object.

SCRAPED PAGE TEXT:
{page_text}

SOURCE URL: {url}

INSTRUCTIONS:
- Extract all recipe information directly from the text above. Do NOT hallucinate or invent information.
- If a field is not found in the text, use null or an empty list/object.
- For nutrition_estimate: provide reasonable approximations based on the ingredients listed.
- For substitutions: suggest 3 practical ingredient swaps relevant to this specific recipe.
- For shopping_list: group all ingredients by category (dairy, produce, pantry, bakery, meat, seafood, spices, etc.)
- For related_recipes: suggest 3 recipes that pair well with or are similar to this dish.
- difficulty should be one of: "easy", "medium", "hard"
- servings must be an integer (e.g., 4)
- Return ONLY valid JSON. No markdown, no explanation, no code fences.

REQUIRED JSON FORMAT:
{
  "title": "string",
  "cuisine": "string",
  "prep_time": "string",
  "cook_time": "string",
  "total_time": "string",
  "servings": integer,
  "difficulty": "easy|medium|hard",
  "ingredients": [
    {"quantity": "string", "unit": "string", "item": "string"}
  ],
  "instructions": ["step 1", "step 2", "..."],
  "nutrition_estimate": {
    "calories": integer,
    "protein": "string",
    "carbs": "string",
    "fat": "string"
  },
  "substitutions": ["substitution 1", "substitution 2", "substitution 3"],
  "shopping_list": {
    "category_name": ["item1", "item2"]
  },
  "related_recipes": ["recipe 1", "recipe 2", "recipe 3"]
}
```

### Design Decisions
- Temperature set to **0.2** to prioritise factual extraction over creativity.
- Page text is limited to **8000 characters** before sending to avoid token overflow.
- The instruction "Do NOT hallucinate" anchors the model to only use content found in the scraped text.
- JSON-only output format makes parsing reliable; a regex strip removes accidental markdown fences.

