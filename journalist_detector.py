from newspaper import Article
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict

class JournalistDetector:
    def __init__(self):
        pass

    def detect_journalist(self, article_data: Dict, content: str) -> Optional[str]:
        # Method 1: Use pre-extracted author from scraper if available
        if article_data and article_data.get('author'):
            return article_data['author']

        # Method 2: Using newspaper3k
        journalist = None
        if article_data and article_data.get('url'):
            journalist = self._detect_with_newspaper3k(article_data['url'])
        
        if not journalist:
            # Method 3: Using BeautifulSoup patterns on content
            journalist = self._detect_with_patterns(content)
        
        return journalist if journalist else "Tidak ditemukan"

    def _detect_with_newspaper3k(self, url: str) -> Optional[str]:
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if hasattr(article, 'authors') and article.authors:
                return ', '.join(article.authors)
            
        except Exception as e:
            print(f"Error with newspaper3k: {str(e)}")
        
        return None

    def _detect_with_patterns(self, content: str) -> Optional[str]:
        # Common patterns for journalist names
        patterns = [
            r'(?:Oleh|By|Penulis|Reporter|Wartawan)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-–—]\s*(?:Reporter|Wartawan|Jurnalis)',
            r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-–—]\s*[A-Z][a-z]+',
            r'(?:Ditulis oleh|Written by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                # Return the first match that looks like a name
                for match in matches:
                    if len(match.split()) >= 2:  # At least first and last name
                        return match.strip()
        
        return None
