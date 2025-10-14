import json
import re
from typing import Dict, Optional
from openai import OpenAI

class SentimentAnalyzer:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = 'models/gemini-2.5-flash'
        self.client = None
        if self.api_key and self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _create_sentiment_prompt(self, content: str, context: str) -> str:
        return f"""
        Analisis sentimen dari artikel berita berikut berdasarkan konteks yang diberikan.
        
        KONTEKS: {context}
        
        ARTIKEL:
        {content[:3000]}
        
        Berikan analisis sentimen dalam format JSON dengan struktur berikut:
        {{
            "sentiment": "positif/negatif/netral",
            "confidence": "tinggi/sedang/rendah",
            "reasoning": "penjelasan singkat mengapa sentimen tersebut dipilih berdasarkan konteks"
        }}
        
        Fokus analisis hanya pada konteks yang diberikan. Jika konteks tidak ditemukan dalam artikel, berikan sentimen "tidak terkait".
        Pastikan output HANYA berupa JSON yang valid.
        """

    def _parse_sentiment_response(self, response_text: str) -> Dict:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"sentiment": "netral", "confidence": "rendah", "reasoning": "Respons bukan JSON yang valid."}

    def analyze_sentiment(self, content: str, context: str) -> Optional[Dict]:
        if not self.client:
            print("OpenAI client tidak diinisialisasi. Periksa API Key atau Base URL.")
            return {"sentiment": "error", "confidence": "rendah", "reasoning": "OpenAI client not initialized."}

        prompt = self._create_sentiment_prompt(content, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=120
            )
            
            if response.choices:
                message_content = response.choices[0].message.content
                return self._parse_sentiment_response(message_content)
            
            return {"sentiment": "gagal", "confidence": "rendah", "reasoning": "Struktur respons tidak valid."}

        except Exception as e:
            print(f"Error saat menghubungi proxy OpenAI: {e}")
            return {"sentiment": "error", "confidence": "rendah", "reasoning": str(e)}
