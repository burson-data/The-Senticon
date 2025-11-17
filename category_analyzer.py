import json
from typing import Dict, Optional, List
from openai import OpenAI

class CategoryAnalyzer:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = 'models/gemini-2.5-flash'
        self.client = None
        if self.api_key and self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _create_category_prompt(self, content: str, categories_with_desc: List[str]) -> str:
        category_lines = []
        for item in categories_with_desc:
            parts = item.split(':', 1)
            if len(parts) == 2:
                name, desc = parts[0].strip(), parts[1].strip()
                category_lines.append(f"- {name}: {desc}")
            else:
                category_lines.append(f"- {item.strip()}")
        
        category_list = "\n".join(category_lines)

        return f"""
        Analyze the following text (which may be a full article or just a title) and classify it into ONE of the most relevant categories from the list provided. Use the descriptions to help you decide.

        CATEGORY LIST:
        {category_list}
        - Lain-lain (use this if no other category is a good fit)

        TEXT TO ANALYZE:
        {content[:3000]}

        Your task is to respond with a JSON object containing the single most relevant category name. Do not add any explanation.
        The JSON structure must be:
        {{
            "category": "Nama Kategori"
        }}
        """

    def analyze_category(self, content: str, categories_with_desc: List[str]) -> str:
        if not self.client:
            print("OpenAI client not initialized. Check API Key or Base URL.")
            return "Error: Client not initialized"

        if not categories_with_desc:
            return "Tidak ada kategori"

        prompt = self._create_category_prompt(content, categories_with_desc)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=90
            )
            
            if response.choices:
                response_text = response.choices[0].message.content
                try:
                    data = json.loads(response_text)
                    category = data.get("category", "Gagal parsing JSON").strip()
                    
                    # Extract just the names for validation
                    valid_category_names = [cat.split(':', 1)[0].strip() for cat in categories_with_desc] + ["Lain-lain"]
                    
                    if category in valid_category_names:
                        return category
                    else:
                        print(f"Warning: Model returned a category not in the list: '{category}'")
                        return category # Return the model's output anyway
                except json.JSONDecodeError:
                    return "Gagal parsing JSON"

            return "Gagal analisis"

        except Exception as e:
            error_message = f"Error analisis AI: {str(e)}"
            print(f"Error contacting OpenAI proxy for categorization: {e}")
            return error_message
