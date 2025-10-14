import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from typing import Dict, Optional, List
import time
import random
import urllib.parse
from urllib.robotparser import RobotFileParser
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth
import pandas as pd
import os
from datetime import datetime

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Enhanced User-Agents dengan lebih banyak variasi
        self.user_agents = [
            # Real Browser User Agents (Updated 2024)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
            
            # Mobile User Agents
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            
            # Indonesian Browser Patterns
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (Indonesia)',
            'Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36',
            
            # Search Engine Bots (Fallback)
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
            
            # Social Media Crawlers
            'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
            'Twitterbot/1.0',
            'LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com/)',
            
            # News Aggregators
            'Mozilla/5.0 (compatible; NewsBot/1.0; +http://www.example.com/newsbot)',
            'Mozilla/5.0 (compatible; FeedFetcher-Google; +http://www.google.com/feedfetcher.html)'
        ]
        
        # Indonesian news site specific patterns - UPDATED WITH KUMPARAN
        self.indonesian_selectors = {
            'detik.com': {
                'title': [
                    '.detail__title', 
                    'h1.title', 
                    '.itp_bodycontent h1',
                    '.detail-title',
                    '[data-module="DetailTitle"] h1'
                ],
                'content': [
                    '.detail__body-text', 
                    '.itp_bodycontent', 
                    '.detail-content',
                    '.detail__body',
                    '[data-module="DetailText"]'
                ]
            },
            'kompas.com': {
                'title': [
                    '.read__title', 
                    'h1.read-page--header-title', 
                    '.artikel__title',
                    '.read__header__title',
                    '.article__title h1'
                ],
                'content': [
                    '.read__content', 
                    '.read-page--content-body', 
                    '.artikel__content',
                    '.read__content p',
                    '.article__content'
                ]
            },
            'tempo.co': {
                'title': [
                    '.title-artikel', 
                    'h1.margin-bottom-20', 
                    '.detail-title',
                    '.artikel-single h1',
                    '.detail-news h1'
                ],
                'content': [
                    '.detail-content', 
                    '.artikel-content', 
                    '.detail-in',
                    '.artikel-single .content',
                    '.detail-news .content'
                ]
            },
            'cnn.com': {
                'title': [
                    '.headline__text', 
                    'h1.pg-headline', 
                    '.ArticleHeader-headline',
                    '.article-header h1',
                    '.headline'
                ],
                'content': [
                    '.zn-body__paragraph', 
                    '.ArticleBody-articleBody', 
                    '.l-container',
                    '.article-body',
                    '.story-body'
                ]
            },
            'cnnindonesia.com': {
                'title': [
                    '.detail-title h1',
                    '.article-title',
                    'h1.title',
                    '.content-title h1'
                ],
                'content': [
                    '.detail-text',
                    '.article-content',
                    '.content-text',
                    '.detail-content'
                ]
            },
            'liputan6.com': {
                'title': [
                    '.read-page--header--title h1',
                    '.article-header-title',
                    '.read-page-title',
                    'h1.title'
                ],
                'content': [
                    '.read-page--content-body',
                    '.article-content-body',
                    '.read-page-content',
                    '.article-text'
                ]
            },
            # KUMPARAN SELECTORS - BARU DITAMBAHKAN
            'kumparan.com': {
                'title': [
                    '.Headline__Title',
                    '.Article__Title',
                    'h1[data-cy="headline"]',
                    '.StoryHeadline__Title',
                    '.DetailStory__Title',
                    'h1.kumHeadline',
                    '.story-headline h1',
                    '.article-headline h1',
                    '.post-title h1',
                    '[class*="Headline"] h1',
                    '[class*="Title"] h1'
                ],
                'content': [
                    '.Story__Content',
                    '.Article__Content',
                    '.StoryContent__Wrapper',
                    '.DetailStory__Content',
                    '.story-content',
                    '.article-content',
                    '.post-content',
                    '.kumContent',
                    '.story-body',
                    '[data-cy="story-content"]',
                    '[class*="Story"] [class*="Content"]',
                    '[class*="Article"] [class*="Content"]',
                    '.content-wrapper .content',
                    '.story-wrapper .story',
                    '.article-wrapper .article'
                ]
            },
            'tribunnews.com': {
                'title': [
                    '.side-article .txt-article h1',
                    '.article h1',
                    '.content h1',
                    '.main-content h1'
                ],
                'content': [
                    '.side-article .txt-article',
                    '.article .content',
                    '.main-content .content',
                    '.article-content'
                ]
            },
            'okezone.com': {
                'title': [
                    '.title h1',
                    '.content-title h1',
                    '.article-title h1'
                ],
                'content': [
                    '.content .description',
                    '.article-content',
                    '.content-text'
                ]
            },
            'antaranews.com': {
                'title': [
                    '.post-content h1',
                    '.article-heading h1',
                    '.content-title h1'
                ],
                'content': [
                    '.post-content .content',
                    '.article-content',
                    '.post-body'
                ]
            },
            'suara.com': {
                'title': [
                    '.content-head h1',
                    '.article-title h1',
                    '.post-title h1'
                ],
                'content': [
                    '.content-text',
                    '.article-body',
                    '.post-content'
                ]
            }
        }
        
        # Load external selectors and merge them
        external_selectors = self._load_selectors_from_csv('selectors.csv')
        self.indonesian_selectors.update(external_selectors)

        # Set initial session
        self._setup_session()

    def _load_selectors_from_csv(self, file_path: str) -> Dict:
        """Loads selectors from a CSV file and formats them."""
        if not os.path.exists(file_path):
            print(f"⚠️ Selector file not found: {file_path}")
            return {}

        try:
            df = pd.read_csv(file_path)
            df.rename(columns={
                'Media': 'domain',
                'Judul': 'title',
                'Reporter': 'author',
                'Isi': 'content'
            }, inplace=True)

            selectors = {}
            for _, row in df.iterrows():
                domain = row['domain']
                if pd.isna(domain):
                    continue

                if domain not in selectors:
                    selectors[domain] = {'title': [], 'content': [], 'author': []}
                
                if pd.notna(row.get('title')) and row.get('title').strip():
                    selectors[domain]['title'].append(row['title'])
                if pd.notna(row.get('content')) and row.get('content').strip():
                    selectors[domain]['content'].append(row['content'])
                if pd.notna(row.get('author')) and row.get('author').strip():
                    selectors[domain]['author'].append(row['author'])

            print(f"✅ Successfully loaded selectors for {len(selectors)} domains from {file_path}")
            return selectors
        except Exception as e:
            print(f"❌ Error loading selector file {file_path}: {e}")
            return {}

    def _setup_session(self):
        """Setup session with better configuration"""
        self.session.headers.clear()
        
        # Rotate user agent
        user_agent = random.choice(self.user_agents)
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Charset': 'UTF-8,*;q=0.7',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        })
        
        # Add random referer sometimes
        if random.random() < 0.4:
            referers = [
                'https://www.google.com/',
                'https://www.google.co.id/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                'https://www.facebook.com/',
                'https://twitter.com/'
            ]
            self.session.headers['Referer'] = random.choice(referers)

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            domain = urllib.parse.urlparse(url).netloc.lower()
            # Handle subdomains - extract main domain
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                # For domains like m.kumparan.com, www.kumparan.com -> kumparan.com
                if domain_parts[-2] in ['kumparan', 'detik', 'kompas', 'tempo', 'tribunnews', 'okezone', 'antara', 'suara', 'liputan6', 'cnnindonesia']:
                    return f"{domain_parts[-2]}.{domain_parts[-1]}"
            return domain
        except:
            return ''

    def _is_valid_content(self, content: str) -> bool:
        """Check if content is valid and meaningful"""
        if not content or len(content.strip()) < 100:
            return False
        
        # Check for common error patterns
        error_patterns = [
            'access denied', '403 forbidden', '404 not found', '500 internal server',
            'blocked', 'captcha', 'robot', 'bot detected', 'please enable javascript',
            'subscription required', 'paywall', 'premium content', 'login required',
            'halaman tidak ditemukan', 'akses ditolak', 'konten tidak tersedia'
        ]
        
        content_lower = content.lower()
        for pattern in error_patterns:
            if pattern in content_lower:
                return False
        
        # Check if content has meaningful sentences
        sentences = re.split(r'[.!?]+', content)
        meaningful_sentences = [s for s in sentences if len(s.strip()) > 20]
        
        return len(meaningful_sentences) >= 3

    def get_title_newspaper3k(self, url: str) -> Optional[str]:
        """Get title using newspaper3k with enhanced error handling"""
        try:
            self._setup_session()
            
            article = Article(url)
            article.download()
            article.parse()
            
            if article.title and len(article.title.strip()) > 5:
                return article.title.strip()
            
        except Exception as e:
            print(f"📰 Newspaper3k title failed for {url}: {str(e)}")
        
        # Fallback to manual extraction
        return self._get_title_manual(url)

    def _get_title_manual(self, url: str) -> Optional[str]:
        """Enhanced title extraction with site-specific selectors"""
        try:
            response = self._make_request(url)
            if not response:
                return "Gagal mengambil judul"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            domain = self._get_domain(url)
            
            print(f"🔍 Extracting title from domain: {domain}")
            
            # Try site-specific selectors first
            if domain in self.indonesian_selectors:
                print(f"📋 Using site-specific selectors for {domain}")
                selectors = self.indonesian_selectors[domain]['title']
                for selector in selectors:
                    try:
                        element = soup.select_one(selector)
                        if element and element.get_text(strip=True):
                            title = element.get_text(strip=True)
                            if len(title) > 5 and len(title) < 200:
                                print(f"✅ Title found with selector '{selector}': {title[:50]}...")
                                return title
                    except Exception as e:
                        print(f"⚠️ Error with selector '{selector}': {e}")
                        continue
            
            # Generic selectors
            title_selectors = [
                'h1.entry-title', 'h1.post-title', 'h1.article-title',
                'h1[class*="title"]', 'h1[class*="headline"]', 'h1[class*="Title"]',
                '.entry-title h1', '.post-title h1', '.article-title h1',
                '[property="og:title"]', '[name="twitter:title"]',
                'title', 'h1', '.title', '.headline', '.Title'
            ]
            
            print(f"🔄 Trying generic selectors...")
            for selector in title_selectors:
                try:
                    if selector.startswith('['):
                        element = soup.select_one(selector)
                        if element:
                            title = element.get('content') or element.get_text(strip=True)
                            if title and 5 < len(title) < 200:
                                print(f"✅ Title found with generic selector '{selector}': {title[:50]}...")
                                return title
                    else:
                        element = soup.select_one(selector)
                        if element:
                            title = element.get_text(strip=True)
                            if title and 5 < len(title) < 200:
                                print(f"✅ Title found with generic selector '{selector}': {title[:50]}...")
                                return title
                except Exception as e:
                    continue
            
            return "Gagal mengambil judul"
            
        except Exception as e:
            print(f"❌ Manual title extraction failed: {str(e)}")
            return "Gagal mengambil judul"

    def _make_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Make HTTP request with multiple retry strategies"""
        
        strategies = [
            # Strategy 1: Standard browser request
            {'headers': self._get_browser_headers(), 'timeout': timeout},
            
            # Strategy 2: Mobile browser
            {'headers': self._get_mobile_headers(), 'timeout': timeout},
            
            # Strategy 3: Simple bot
            {'headers': self._get_bot_headers(), 'timeout': timeout},
            
            # Strategy 4: Minimal headers
            {'headers': self._get_minimal_headers(), 'timeout': timeout//2}
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                print(f"🔄 Trying strategy {i+1}: {strategy['headers']['User-Agent'][:50]}...")
                
                # Add small delay between attempts
                if i > 0:
                    time.sleep(random.uniform(1, 3))
                
                response = requests.get(url, **strategy, allow_redirects=True, verify=False)
                
                # Check if response is valid
                if response.status_code == 200 and len(response.content) > 1000:
                    print(f"✅ Strategy {i+1} successful: {len(response.content)} bytes")
                    return response
                elif response.status_code in [301, 302, 303, 307, 308]:
                    print(f"🔄 Redirect detected, following...")
                    continue
                else:
                    print(f"⚠️ Strategy {i+1} failed: Status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Strategy {i+1} timeout")
                continue
            except requests.exceptions.ConnectionError:
                print(f"🌐 Strategy {i+1} connection error")
                continue
            except Exception as e:
                print(f"❌ Strategy {i+1} error: {str(e)}")
                continue
        
        print(f"❌ All strategies failed for {url}")
        return None

    def _get_browser_headers(self) -> Dict[str, str]:
        """Get realistic browser headers"""
        return {
            'User-Agent': random.choice([ua for ua in self.user_agents if 'bot' not in ua.lower()]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }

    def _get_mobile_headers(self) -> Dict[str, str]:
        """Get mobile browser headers"""
        mobile_agents = [ua for ua in self.user_agents if any(mobile in ua for mobile in ['Mobile', 'Android', 'iPhone', 'iPad'])]
        return {
            'User-Agent': random.choice(mobile_agents) if mobile_agents else self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def _get_bot_headers(self) -> Dict[str, str]:
        """Get search engine bot headers"""
        bot_agents = [ua for ua in self.user_agents if 'bot' in ua.lower()]
        return {
            'User-Agent': random.choice(bot_agents) if bot_agents else 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate'
        }

    def _get_minimal_headers(self) -> Dict[str, str]:
        """Get minimal headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,*/*',
            'Accept-Language': 'id,en'
        }

    async def _scrape_with_playwright_async(self, url: str, timeout: int = 45000) -> Optional[str]:
        """Scrape using Playwright to handle JavaScript rendering."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Apply stealth measures
                await stealth(page)
                
                print(f"🚀 Launching Playwright for {url[:60]}...")
                await page.goto(url, timeout=timeout, wait_until='networkidle')
                
                # Wait for potential dynamic content
                await page.wait_for_timeout(5000) 
                
                content = await page.content()
                await browser.close()
                
                if content and len(content) > 500:
                    print(f"✅ Playwright successfully fetched {len(content)} bytes.")
                    return content
                else:
                    print("⚠️ Playwright fetched content but it seems empty.")
                    return None
        except Exception as e:
            print(f"❌ Playwright failed for {url}: {str(e)}")
            return None

    async def scrape_article(self, url: str, timeout: int = 30, basic_only: bool = False) -> Optional[Dict]:
        """
        Enhanced scraping with a hybrid approach:
        1. Newspaper3k (fast)
        2. Manual requests-based scraping (medium)
        3. Playwright headless browser (robust)
        """
        try:
            print(f"🌐 Starting scrape: {url[:60]}...")
            
            # Add random delay
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # --- Method 1: Try newspaper3k first ---
            article_data = self._scrape_with_newspaper3k(url)
            if article_data and self._is_valid_content(article_data.get('content', '')):
                print(f"✅ Newspaper3k success: {len(article_data.get('content', ''))} chars")
                return article_data
            
            # --- Method 2: Enhanced manual scraping (requests) ---
            print("🔄 Newspaper3k failed. Trying enhanced manual scraping...")
            article_data = self._scrape_with_enhanced_manual(url, timeout, basic_only)
            if article_data and self._is_valid_content(article_data.get('content', '')):
                print(f"✅ Manual scraping success: {len(article_data.get('content', ''))} chars")
                return article_data

            # --- Method 3: Playwright as a final fallback ---
            print("🔄 Manual scraping failed. Trying Playwright...")
            html_content = await self._scrape_with_playwright_async(url, timeout * 1000)
            
            if html_content:
                soup = BeautifulSoup(html_content, 'lxml')
                domain = self._get_domain(url)
                self._clean_soup(soup)
                
                content = self._extract_content_enhanced(soup, domain)
                
                if self._is_valid_content(content):
                    title = self._extract_title_from_soup(soup, domain)
                    publish_date = self._extract_publish_date_from_soup(soup, domain)
                    print(f"✅ Playwright success: {len(content)} chars")
                    return {
                        'content': content,
                        'title': title,
                        'publish_date': publish_date,
                        'url': url,
                        'method': 'playwright'
                    }

            print(f"❌ All methods failed for {url}")
            return None
            
        except Exception as e:
            print(f"❌ Critical error scraping {url}: {str(e)}")
            return None

    def _scrape_with_newspaper3k(self, url: str) -> Optional[Dict]:
        """Enhanced newspaper3k with better error handling"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            content = article.text.strip() if article.text else ""
            title = article.title.strip() if article.title else ""
            
            if self._is_valid_content(content):
                return {
                    'content': content,
                    'title': title,
                    'url': url,
                    'method': 'newspaper3k',
                    'publish_date': str(article.publish_date) if article.publish_date else ''
                }
            
        except Exception as e:
            print(f"📰 Newspaper3k detailed error: {str(e)}")
        
        return None

    def _scrape_with_enhanced_manual(self, url: str, timeout: int, basic_only: bool) -> Optional[Dict]:
        """Enhanced manual scraping with site-specific selectors"""
        try:
            response = self._make_request(url, timeout)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            domain = self._get_domain(url)
            
            print(f"🔍 Processing domain: {domain}")
            
            # Remove unwanted elements first
            self._clean_soup(soup)
            
            # Extract content using site-specific selectors
            content = self._extract_content_enhanced(soup, domain)
            
            if basic_only:
                return {'content': content, 'url': url, 'method': 'manual_basic'}
            
            # Extract title
            title = self._extract_title_from_soup(soup, domain)
            
            # Extract author
            author = self._extract_author_from_soup(soup, domain)
            
            # Extract publish date
            publish_date = self._extract_publish_date_from_soup(soup, domain)

            return {
                'content': content,
                'title': title,
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'method': 'manual_enhanced'
            }
            
        except Exception as e:
            print(f"🔧 Enhanced manual scraping error: {str(e)}")
            return None

    def _scrape_simple(self, url: str, timeout: int) -> Optional[Dict]:
        """Simple last-resort scraping"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=timeout//2, verify=False)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Simple content extraction
            content = ""
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 30:
                    content += text + " "
            
            if len(content.strip()) > 100:
                return {
                    'content': content.strip(),
                    'title': soup.title.get_text(strip=True) if soup.title else "No title",
                    'url': url,
                    'method': 'simple'
                }
            
        except Exception as e:
            print(f"🔧 Simple scraping error: {str(e)}")
        
        return None

    def _clean_soup(self, soup: BeautifulSoup):
        """Remove unwanted elements from soup"""
        unwanted_elements = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            'advertisement', 'ads', 'menu', 'sidebar', 'noscript',
            'iframe', 'form', 'button', 'input'
        ]
        
        for element_name in unwanted_elements:
            for element in soup.find_all(element_name):
                element.decompose()
        
        # Remove by class/id patterns
        unwanted_patterns = [
            'ad', 'ads', 'advertisement', 'promo', 'banner',
            'social', 'share', 'comment', 'related', 'sidebar',
            'navigation', 'menu', 'breadcrumb', 'tag', 'category'
        ]
        
        for pattern in unwanted_patterns:
            for element in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                element.decompose()
            for element in soup.find_all(attrs={'id': re.compile(pattern, re.I)}):
                element.decompose()

    def _extract_content_enhanced(self, soup: BeautifulSoup, domain: str) -> str:
        """Enhanced content extraction with site-specific selectors"""
        
        print(f"🎯 Extracting content for domain: {domain}")
        
        # Try site-specific selectors first
        if domain in self.indonesian_selectors:
            print(f"📋 Using site-specific content selectors for {domain}")
            selectors = self.indonesian_selectors[domain]['content']
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        content = element.get_text(separator=' ', strip=True)
                        if len(content) > 200:
                            print(f"✅ Content found with selector '{selector}': {len(content)} chars")
                            return self._clean_content(content)
                except Exception as e:
                    print(f"⚠️ Error with content selector '{selector}': {e}")
                    continue
        
        # Generic high-priority selectors
        priority_selectors = [
            'article .content', 'article .body', 'article .text',
            '.article-content', '.post-content', '.entry-content',
            '.article-body', '.post-body', '.content-body',
            '.detail-content', '.news-content', '.story-content',
            '.Story__Content', '.Article__Content',  # Kumparan fallback
            '.StoryContent__Wrapper', '.DetailStory__Content'  # Kumparan fallback
        ]
        
        print(f"🔄 Trying priority selectors...")
        for selector in priority_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    content = element.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        print(f"✅ Content found with priority selector '{selector}': {len(content)} chars")
                        return self._clean_content(content)
            except Exception as e:
                continue
        
        # Fallback to article tag or main content
        print(f"🔄 Trying fallback selectors...")
        for tag in ['article', 'main', '.content']:
            try:
                elements = soup.select(tag) if tag.startswith('.') else soup.find_all(tag)
                for element in elements:
                    content = element.get_text(separator=' ', strip=True)
                    if len(content) > 200:
                        print(f"✅ Content found with fallback selector '{tag}': {len(content)} chars")
                        return self._clean_content(content)
            except Exception as e:
                continue
        
        # Last resort: paragraph extraction
        print(f"🔄 Trying paragraph extraction...")
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 30 and not self._is_unwanted_paragraph(text):
                paragraphs.append(text)
        
        if paragraphs:
            content = ' '.join(paragraphs)
            print(f"✅ Content found with paragraph extraction: {len(content)} chars")
            return self._clean_content(content)
        
        print(f"❌ No content found for {domain}")
        return ""

    def _extract_title_from_soup(self, soup: BeautifulSoup, domain: str) -> str:
        """Extract title from soup with site-specific selectors"""
        
        print(f"🎯 Extracting title for domain: {domain}")
        
        # Try site-specific selectors first
        if domain in self.indonesian_selectors:
            print(f"📋 Using site-specific title selectors for {domain}")
            selectors = self.indonesian_selectors[domain]['title']
            for selector in selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        title = element.get_text(strip=True)
                        if 5 < len(title) < 200:
                            print(f"✅ Title found with selector '{selector}': {title[:50]}...")
                            return title
                except Exception as e:
                    print(f"⚠️ Error with title selector '{selector}': {e}")
                    continue
        
        # Generic selectors
        print(f"🔄 Trying generic title selectors...")
        title_selectors = ['h1', '.title', '.headline', '.Title', 'title']
        for selector in title_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if 5 < len(title) < 200:
                        print(f"✅ Title found with generic selector '{selector}': {title[:50]}...")
                        return title
            except Exception as e:
                continue
        
        return "No title found"

    def _extract_publish_date_from_soup(self, soup: BeautifulSoup, domain: str) -> Optional[str]:
        """Extract publish date from soup with various strategies."""
        print(f"🎯 Extracting publish date for domain: {domain}")

        # Strategy 1: Meta tags
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="pubdate"]',
            'meta[name="date"]',
            'meta[property="og:article:published_time"]',
            'meta[name="parsely-pub-date"]'
        ]
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element and element.get('content'):
                date_str = element.get('content').strip()
                if date_str:
                    print(f"✅ Date found with meta selector '{selector}': {date_str}")
                    return date_str

        # Strategy 2: Time tag
        time_element = soup.find('time')
        if time_element and time_element.get('datetime'):
            date_str = time_element.get('datetime').strip()
            if date_str:
                print(f"✅ Date found with <time> tag: {date_str}")
                return date_str
        elif time_element and time_element.get_text():
             date_str = time_element.get_text().strip()
             if date_str:
                print(f"✅ Date found with <time> tag text: {date_str}")
                return date_str

        # Strategy 3: JSON-LD script
        try:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'datePublished' in data:
                        print(f"✅ Date found in JSON-LD: {data['datePublished']}")
                        return data['datePublished']
                    if 'uploadDate' in data: # For video objects
                        print(f"✅ Date found in JSON-LD: {data['uploadDate']}")
                        return data['uploadDate']
        except Exception:
            pass # Ignore JSON parsing errors

        # Strategy 4: Site-specific selectors (if available)
        # This can be expanded in selectors.csv if needed
        if domain in self.indonesian_selectors and 'publish_date' in self.indonesian_selectors[domain]:
            selectors = self.indonesian_selectors[domain]['publish_date']
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    date_str = element.get_text(strip=True)
                    if date_str:
                        print(f"✅ Date found with specific selector '{selector}': {date_str}")
                        return date_str
        
        print("🔄 No specific date found, returning None.")
        return None

    def _extract_author_from_soup(self, soup: BeautifulSoup, domain: str) -> str:
        """Extract author from soup with site-specific selectors"""
        
        print(f"🎯 Extracting author for domain: {domain}")
        
        # Try site-specific selectors first
        if domain in self.indonesian_selectors and 'author' in self.indonesian_selectors[domain]:
            print(f"📋 Using site-specific author selectors for {domain}")
            selectors = self.indonesian_selectors[domain]['author']
            for selector in selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        author = element.get_text(strip=True)
                        if author:
                            print(f"✅ Author found with selector '{selector}': {author[:50]}...")
                            return author
                except Exception as e:
                    print(f"⚠️ Error with author selector '{selector}': {e}")
                    continue
        
        return None

    def _is_unwanted_paragraph(self, text: str) -> bool:
        """Check if paragraph contains unwanted content"""
        unwanted_patterns = [
            'baca juga', 'lihat juga', 'follow', 'subscribe', 'advertisement',
            'copyright', '©', 'all rights reserved', 'terms of service',
            'privacy policy', 'cookie policy', 'loading', 'please wait',
            'daftarkan email', 'berlangganan', 'subscribe newsletter',
            'ikuti kami', 'follow us', 'share artikel', 'bagikan artikel'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in unwanted_patterns)

    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        if not content:
            return ""
        
        # Remove extra whitespaces
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n+', '\n', content)
        
        # Remove Indonesian news artifacts
        artifacts = [
            r'Baca juga:.*?(?=\w)', r'Lihat juga:.*?(?=\w)',
            r'ADVERTISEMENT.*?(?=\w)', r'CONTINUE READING.*?(?=\w)',
            r'Loading\.\.\.', r'Tunggu sebentar\.\.\.', r'Mohon tunggu\.\.\.',
            r'Copyright.*', r'©.*', r'All rights reserved.*',
            r'Daftarkan email.*?(?=\w)', r'Berlangganan.*?(?=\w)',
            r'Follow.*?(?=\w)', r'Share.*?(?=\w)', r'Bagikan.*?(?=\w)',
            r'Ikuti kami.*?(?=\w)', r'Subscribe.*?(?=\w)'
        ]
        
        for artifact in artifacts:
            content = re.sub(artifact, '', content, flags=re.IGNORECASE)
        
        return content.strip()

    def get_user_agent_stats(self):
        """Get statistics about available user agents"""
        bot_count = sum(1 for ua in self.user_agents if 'bot' in ua.lower())
        browser_count = len(self.user_agents) - bot_count
        
        return {
            'total': len(self.user_agents),
            'bots': bot_count,
            'browsers': browser_count,
            'supported_sites': len(self.indonesian_selectors),
            'current': self.session.headers.get('User-Agent', 'Not set')[:60] + '...'
        }

    def test_url_accessibility(self, url: str) -> Dict[str, any]:
        """Test if URL is accessible and return diagnostics"""
        results = {
            'url': url,
            'domain': self._get_domain(url),
            'has_specific_selectors': False,
            'accessible': False,
            'status_code': None,
            'content_length': 0,
            'method_used': None,
            'error': None
        }
        
        # Check if we have specific selectors for this domain
        domain = self._get_domain(url)
        results['has_specific_selectors'] = domain in self.indonesian_selectors
        
        try:
            response = self._make_request(url, timeout=15)
            if response:
                results.update({
                    'accessible': True,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'method_used': 'http_request'
                })
            else:
                results['error'] = 'No successful request method'
                
        except Exception as e:
            results['error'] = str(e)
        
        return results

    def get_supported_sites(self) -> Dict[str, List[str]]:
        """Get list of supported sites with their selectors"""
        supported = {}
        for domain, selectors in self.indonesian_selectors.items():
            supported[domain] = {
                'title_selectors': len(selectors['title']),
                'content_selectors': len(selectors['content']),
                'example_title_selector': selectors['title'][0] if selectors['title'] else None,
                'example_content_selector': selectors['content'][0] if selectors['content'] else None
            }
        return supported
