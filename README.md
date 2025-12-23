# X Reply Bot 🐦

Bot autonome Twitter/X utilisant l'IA (GPT-5-mini) pour générer des réponses engageantes sur les tweets viraux.

## ✨ Fonctionnalités

- 🔄 **Scan continu** de la timeline Twitter
- 🧠 **Réponses IA** via GPT-5-mini (sarcastiques, naturelles, courtes)
- 🎭 **Comportement humain** simulé (délais aléatoires, mouvements souris, frappe progressive)
- 🔒 **Proxies SOCKS5** rotatifs pour l'anonymat
- 📱 **Notifications Telegram** en temps réel
- 🎯 **Filtrage intelligent** : tweets viraux (>100 likes), récents (<6h), anglais uniquement

## � Structure du projet

```
├── main.py              # Orchestrateur principal
├── config.py            # Configuration centralisée
├── scroller.py          # Navigation et scraping timeline
├── responder.py         # Génération IA et postage
├── utils.py             # Fonctions comportement humain
├── proxies.py           # Gestion rotation proxies
├── telegram_notifier.py # Notifications Telegram
├── requirements.txt     # Dépendances Python
├── .env.example         # Template variables d'environnement
└── README.md
```

## 🚀 Installation

### 1. Cloner le repo
```bash
git clone https://github.com/YOUR_USERNAME/x-reply-bot.git
cd x-reply-bot
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate   # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

### 4. Configuration
Créer un fichier `.env` :
```env
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email@example.com
OPENAI_API_KEY=sk-your-openai-key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
LOG_LEVEL=INFO
```

### 5. Cookies de session (optionnel)
Pour éviter la connexion manuelle, créer `cookies.json` avec les cookies de session Twitter.

## ▶️ Lancement

```bash
python main.py
```

### Avec PM2 (recommandé pour VPS)
```bash
npm install -g pm2
pm2 start main.py --name x-bot --interpreter ./venv/bin/python3
pm2 save
```

## ⚙️ Configuration avancée

Modifier `config.py` pour ajuster :
- `MIN_LIKES` : Minimum de likes requis (défaut: 100)
- `MAX_TWEET_AGE_HOURS` : Âge max des tweets (défaut: 6h)
- `REPLY_DELAY_MIN/MAX` : Délais entre réponses (43s-3m36s)
- `AI_SYSTEM_PROMPT` : Personnalité du bot

## 🛡️ Sécurité

- Rotation de proxies résidentiels SOCKS5
- User-Agents rotatifs
- Masquage traces automatisation
- Délais humanisés

## 📜 License

MIT
