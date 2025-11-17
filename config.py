import os
from dotenv import load_dotenv

# File ini sengaja dikosongkan.
# Kunci API sekarang dikelola melalui Streamlit Secrets.

# Muat variabel dari file .env
load_dotenv()

# API Keys Configuration
# Prioritaskan variabel lingkungan, jika tidak ada, gunakan nilai hardcoded sebagai fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "sk-_4expCn9n0sz-jKw_11a7B1ZjxlE4yGXcL1jaCRF9EczwIKz")  # Ganti dengan API key Gemini Anda

# (Opsional) Jika Anda menggunakan proxy atau endpoint custom
# URL Lengkap ke endpoint proxy Gemini
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://krsbeknjypkg.sg-members-1.clawcloudrun.com/proxy/gemini/v1beta/openai")
