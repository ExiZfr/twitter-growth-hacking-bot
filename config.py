# -*- coding: utf-8 -*-
"""
Configuration centralisée pour le X Reply Bot.
Toutes les valeurs sensibles doivent être définies via variables d'environnement ou fichier .env
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# =========================================
# IDENTIFIANTS TWITTER/X
# =========================================
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")  # Pour la vérification 2FA si nécessaire

# =========================================
# OPENAI API
# =========================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-5-mini"  # Modèle spécifique avec accès privé
MAX_RESPONSE_TOKENS = 1200     # Augmenté pour éviter 'finish_reason: length'

# =========================================
# TELEGRAM NOTIFICATIONS
# =========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# =========================================
# PROXIES SOCKS5 RESIDENTIELS
# Format: socks5://ip:port:user:pass
# =========================================
PROXIES = [
    "socks5://141.145.199.102:45001:gKZ6946d524403d0:PLexGD7npg8rN6EmYV",
    "socks5://141.145.214.15:45001:i0n694702d67c84c:PaIBMEGWbN9ridwpVw",
]

# =========================================
# CRITÈRES DE FILTRAGE DES TWEETS
# =========================================
MIN_LIKES = 100                    # Minimum de likes requis
MAX_TWEET_AGE_HOURS = 6            # Âge maximum du tweet en heures
LANGUAGE_FILTER = "en"             # Filtrer uniquement les tweets anglais
MIN_RETWEETS = 0                   # Minimum de retweets (optionnel)

# =========================================
# COMPORTEMENT HUMAIN
# =========================================
SCROLL_DELAY_MIN = 2.0             # Délai minimum entre scrolls (secondes)
SCROLL_DELAY_MAX = 8.0             # Délai maximum entre scrolls
REPLY_DELAY_MIN = 43               # Délai minimum entre réponses (secondes) - 43s
REPLY_DELAY_MAX = 216              # Délai maximum entre réponses (secondes) - 3min36s
CYCLE_DELAY_MIN = 1                # Délai minimum entre cycles (secondes) - Cycles rapides
CYCLE_DELAY_MAX = 5                # Délai maximum entre cycles (secondes) - Cycles rapides
MAX_REPLIES_PER_CYCLE = 15         # Maximum de réponses par cycle

# =========================================
# COMPORTEMENT ORGANIQUE (ANTI-DÉTECTION)
# =========================================
REFRESH_INTERVAL_MIN = 240         # Refresh page toutes les 4 minutes minimum
REFRESH_INTERVAL_MAX = 720         # Refresh page toutes les 12 minutes maximum
RANDOM_LIKE_CHANCE = 0.15          # 15% de chance de liker un tweet random
RANDOM_RT_CHANCE = 0.05            # 5% de chance de RT un tweet random
RANDOM_BOOKMARK_CHANCE = 0.10      # 10% de chance de bookmark un tweet random

# =========================================
# USER-AGENTS POUR ROTATION
# =========================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# =========================================
# CONFIGURATION DU NAVIGATEUR
# =========================================
HEADLESS = True                    # Mode sans interface graphique
BROWSER_TIMEOUT = 60000            # Timeout en millisecondes
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# =========================================
# LOGGING
# =========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "bot.log"

# =========================================
# PERSONA IA - System Prompt
# =========================================
AI_SYSTEM_PROMPT = """You are a regular Twitter user, NOT an AI assistant. You respond with a natural, human tone in English.

STRICT RULES:
- SHORT responses (1-2 sentences maximum, never more)
- Sarcastic, edgy, or strong opinionated tone depending on context
- Use natural English internet slang/idioms
- NEVER use a "helpful assistant" or robotic tone
- No excessive emojis (max 1 if relevant)
- You can be critical, provocative, or just give your blunt opinion
- Avoid platitudes and generic responses
- NEVER start with "I think that" or similar formulas

APPROPRIATE TONE EXAMPLES:
- "Groundbreaking discovery right here 🙄"
- "Imagine actually believing this"
- "Absolute peak fiction"
- "The PR team is sweating right now"
- "Too real."
"""
