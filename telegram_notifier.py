# -*- coding: utf-8 -*-
"""
Module de notification Telegram.
Envoie des alertes quand le bot poste une réponse.
"""

import httpx
from loguru import logger
import config
import utils

class TelegramNotifier:
    """Envoie des notifications vers un canal/chat Telegram."""
    
    def __init__(self):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.enabled = bool(self.token and self.chat_id)

    async def send_notification(self, tweet_url: str, reply_content: str):
        """
        Envoie un message formaté sur Telegram.
        """
        if not self.enabled:
            logger.warning("Notification Telegram désactivée (Token ou Chat ID manquant)")
            return False

        message = (
            "🐦 *New X Reply Posted!*\n\n"
            f"🔗 *Target Tweet:* {tweet_url}\n"
            f"💬 *Your Reply:* {reply_content}\n"
            f"⏰ *Time:* {utils.format_timestamp()}"
        )
        
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, json=payload)
                if response.status_code == 200:
                    logger.info("Notification Telegram envoyée avec succès")
                    return True
                else:
                    logger.error(f"Erreur Telegram ({response.status_code}): {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification Telegram : {e}")

    async def send_status(self, cycle_count: int, tweets_found: int, replies_posted: int, next_run_seconds: int):
        """Envoie un statut de cycle sur Telegram."""
        try:
            message = (
                f"🔄 **Cycle #{cycle_count} Démarré**\n\n"
                f"📊 **Stats précédent:**\n"
                f"- Tweets trouvés: {tweets_found}\n"
                f"- Réponses postées: {replies_posted}\n\n"
                f"⏱️ **Prochain cycle:** dans ~{next_run_seconds}s\n"
                f"✅ **Bot Actif & Connecté**"
            )
            
            data = {
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json=data,
                    timeout=10.0
                )
                logger.info("✓ Notification de statut envoyée")
                    
        except Exception as e:
            logger.error(f"Erreur envoi statut: {e}")

    async def send_log(self, message: str):
        """Envoie un log d'activité en temps réel sur Telegram."""
        try:
            data = {
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json=data,
                    timeout=5.0
                )
                    
        except Exception as e:
            # Silent fail pour ne pas polluer les logs
            pass

# Test rapide si exécuté directement
if __name__ == "__main__":
    import asyncio
    async def test():
        notifier = TelegramNotifier()
        await notifier.send_notification("https://x.com/test/status/123", "Ceci est un test.")
    
    if config.TELEGRAM_BOT_TOKEN:
        asyncio.run(test())
