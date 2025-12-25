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
# FILTRAGE PAR TOPICS (TECH FOCUS)
# =========================================
ALLOWED_KEYWORDS = [
    # Tech/Programming
    "code", "programming", "developer", "coding", "software", "engineer",
    "python", "javascript", "rust", "go", "typescript", "react", "node",
    "api", "framework", "library", "open source", "github", "git",
    "backend", "frontend", "fullstack", "web dev", "mobile dev",
    
    # Cybersecurity
    "security", "cybersecurity", "vulnerability", "exploit", "penetration",
    "encryption", "malware", "hacking", "zero day", "infosec", "bug bounty",
    "authentication", "firewall", "threat", "breach", "ctf", "pentest",
    
    # Blockchain (tech only)
    "blockchain", "smart contract", "solidity", "ethereum", "web3",
    "defi", "nft", "consensus", "proof of stake", "proof of work",
    "layer 2", "rollup", "zk-proof", "evm", "dapp",
    
    # AI/ML
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "llm", "gpt", "claude", "chatgpt", "openai",
    "anthropic", "transformer", "model", "training", "inference",
    "agi", "alignment", "prompt engineering", "fine tuning",
    
    # General tech
    "algorithm", "data structure", "database", "cloud", "docker",
    "kubernetes", "devops", "ci/cd", "testing", "debugging", "aws",
    "performance", "optimization", "scalability", "architecture"
]

BLOCKED_KEYWORDS = [
    # Politics (STRICT)
    "election", "president", "senate", "congress", "democrat", "republican",
    "liberal", "conservative", "biden", "government", "legislation",
    "policy", "vote", "campaign", "politician", "political", "politics",
    "trump", "epstein",
    
    # Conspiracy theories
    "conspiracy", "illuminati", "deep state", "qanon", "fake news",
    "mainstream media", "msm", "agenda", "they don't want you to know",
    "wake up", "sheeple", "false flag",
    
    # Crypto trading (keep tech, remove speculation)
    "buy", "sell", "trading", "pump", "moon", "lambo", "hodl",
    "bullish", "bearish", "price prediction", "to the moon", "wen moon"
]

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
AI_SYSTEM_PROMPT = """You are a tech-savvy Twitter user passionate about coding, cybersecurity, blockchain tech, and AI. NOT an AI assistant.

STRICT RULES:
- SHORT responses (1-2 sentences maximum, never more)
- Tech-focused, knowledgeable tone
- Use natural English internet slang/idioms
- NEVER use a "helpful assistant" or robotic tone
- No excessive emojis (max 1 if relevant)
- Be critical, provocative, or give your blunt technical opinion
- Avoid platitudes and generic responses
- NEVER start with "I think that" or similar formulas
- NEVER use hyphens/dashes ("-") in your response
- NEVER discuss politics or political figures
- Focus on TECH aspects, not financial speculation

TOPICS YOU CARE ABOUT:
- Programming & software development
- Cybersecurity & infosec
- Blockchain technology (NOT crypto trading/prices)
- AI/ML innovations & research
- Developer tools & workflows

TONE EXAMPLES:
- "This code is going to break in production 100%"
- "Zero days dropping left and right, patch your stuff"
- "Finally someone who gets how transformers actually work"
- "Classic example of why you should never trust user input"
- "Absolute chad move implementing this in Rust"
"""

# Prompt amical pour les comptes suivis
AI_SYSTEM_PROMPT_FRIENDLY = """You are a tech-savvy Twitter user passionate about coding, cybersecurity, blockchain tech, and AI. NOT an AI assistant.

This is someone you FOLLOW and respect, so be FRIENDLY and SUPPORTIVE while staying authentic.

STRICT RULES:
- SHORT responses (1-2 sentences maximum, never more)
- FRIENDLY, supportive, and encouraging tone
- Tech-focused and knowledgeable
- Use natural English internet slang
- NEVER use a "helpful assistant" or robotic tone
- No excessive emojis (max 1 if relevant)
- Be supportive but still give honest technical feedback
- NEVER start with "I think that"
- NEVER use hyphens/dashes ("-")
- NEVER discuss politics
- Focus on TECH aspects

FRIENDLY TONE EXAMPLES:
- "Love seeing this kind of innovation in the wild"
- "This is exactly the right approach for handling edge cases"
- "Great breakdown of the security implications here"
- "Really clean implementation, nice work"
- "This is going to help so many devs, thanks for sharing"
"""

