from typing import Dict, Optional
from openai import OpenAI


class ArticleSummarizer:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = 'models/gemini-2.5-flash'
        self.client = None
        if self.api_key and GEMINI_BASE_URL:
            self.client = OpenAI(api_key=self.api_key, base_url=GEMINI_BASE_URL)

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        if self.api_key and GEMINI_BASE_URL:
            self.client = OpenAI(api_key=self.api_key, base_url=GEMINI_BASE_URL)

    def _create_summary_prompt(self, content: str, config: Dict) -> str:
        summary_type = config.get('summary_type', 'Ringkas')
        max_length = config.get('max_length', 150)
        language = config.get('language', 'Bahasa Indonesia')
        focus_aspect = config.get('focus_aspect', '')
        
        content = content[:4000]
        
        lang_instruction = {
            "English": "Respond in English.",
            "Bahasa Indonesia": "Respond in Bahasa Indonesia."
        }.get(language, "Use the same language as the original article.")
        
        type_instructions = {
            'Ringkas': f"Create a concise summary in approximately {max_length} words that captures the main points.",
            'Detail': f"Create a detailed summary in approximately {max_length} words that includes important details and context.",
            'Poin-poin Utama': f"Create a bullet-point summary with the main points, keeping it under {max_length} words total.",
            'Custom': config.get('custom_instruction', f"Create a summary in approximately {max_length} words.")
        }
        type_instruction = type_instructions.get(summary_type, type_instructions['Ringkas'])
        
        focus_instruction = f"\nFocus specifically on: {focus_aspect}" if focus_aspect else ""
        
        return f"""
        Summarize the following article according to these requirements:
        
        REQUIREMENTS:
        - {type_instruction}
        - {lang_instruction}
        - Maximum {max_length} words
        {focus_instruction}
        
        ARTICLE:
        {content}
        
        Please provide only the summary text without any additional formatting or explanations.
        """

    def _parse_summary_response(self, response_text: str) -> Dict:
        summary = response_text.strip()
        word_count = len(summary.split())
        return {"summary": summary, "word_count": word_count}

    def summarize_article(self, content: str, config: Dict) -> Optional[Dict]:
        if not self.client:
            print("OpenAI client tidak diinisialisasi. Periksa API Key atau Base URL.")
            return {"summary": "Gagal: OpenAI client not initialized.", "word_count": 0}

        prompt = self._create_summary_prompt(content, config)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                timeout=120
            )
            
            if response.choices:
                message_content = response.choices[0].message.content
                return self._parse_summary_response(message_content)
            
            return {"summary": "Gagal membuat ringkasan: Struktur respons tidak valid.", "word_count": 0}

        except Exception as e:
            print(f"Error saat menghubungi proxy OpenAI: {e}")
            return {"summary": f"Gagal membuat ringkasan: {e}", "word_count": 0}
