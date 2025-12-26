# -*- coding: utf-8 -*-
"""
Orchestrateur principal du X Reply Bot.
Gère les cycles de scan et de réponse.
"""

import asyncio
import sys
import signal
import random
from loguru import logger

import config
import utils
from scroller import TimelineScroller
from responder import AIResponder
from telegram_notifier import TelegramNotifier

# Configuration des logs
logger.remove()  # Supprimer le handler par défaut
logger.add("bot.log", rotation="10 MB", retention="7 days", level=config.LOG_LEVEL)
logger.add(lambda msg: print(msg, end=""), level=config.LOG_LEVEL)

# Handler Telegram pour TOUS les logs en temps réel
telegram_notifier_instance = TelegramNotifier()

def telegram_log_sink(message):
    """Envoie TOUS les logs (INFO+) à Telegram en temps réel."""
    record = message.record
    level = record["level"].name
    
    # Filtrer seulement INFO et supérieur
    if record["level"].no < 20:  # < INFO
        return
    
    # Formater le message
    log_msg = record["message"]
    context = f"{record['name']}:{record['function']}"
    
    # Icône selon le niveau
    icon = {
        "INFO": "ℹ️",
        "WARNING": "⚠️", 
        "ERROR": "🚨",
        "CRITICAL": "💥"
    }.get(level, "📝")
    
    telegram_msg = f"{icon} **{level}**\n`{context}`\n{log_msg[:200]}"
    
    # Envoyer de manière asynchrone (sans bloquer)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(telegram_notifier_instance.send_log(telegram_msg))
        else:
            asyncio.run(telegram_notifier_instance.send_log(telegram_msg))
    except:
        pass

# Ajouter le handler Telegram pour TOUS les logs INFO+
logger.add(telegram_log_sink, level="INFO")

class XReplyBot:
    """Bot Twitter/X autonome."""
    
    def __init__(self):
        self.scroller = TimelineScroller()
        self.responder = AIResponder()
        self.notifier = TelegramNotifier()
        self.is_running = False

    async def run_cycle(self):
        """Exécute un cycle complet: Scan -> Reply -> Notify."""
        next_wait = utils.random.randint(config.CYCLE_DELAY_MIN, config.CYCLE_DELAY_MAX)
        
        # Stats du cycle précédent stockés dans self si besoin, ici on initialise à 0 pour l'exemple
        # (Pour une vraie persistance il faudrait stocker les stats dans la classe)
        if not hasattr(self, 'cycle_count'): self.cycle_count = 0
        self.cycle_count += 1
        
        # Notification de statut de cycle
        # Note: Les stats "vrais" (tweets_found, replies_posted) seraient idéalement ceux du cycle précédent
        # Ici on envoie une notif de démarrage
        await self.notifier.send_status(
            cycle_count=self.cycle_count,
            tweets_found=getattr(self, 'last_tweets_found', 0),
            replies_posted=getattr(self, 'last_replies_posted', 0),
            next_run_seconds=next_wait
        )
        
        logger.info("--- Début d'un nouveau cycle ---")
        
        tweets_found_count = 0
        replies_posted_count = 0
        
        try:
            # 1. Récupérer des tweets qualifiés
            await self.notifier.send_log("🔍 **Début du scroll...**")
            tweets = await self.scroller.get_qualified_tweets()
            
            if not tweets:
                await self.notifier.send_log("❌ **Aucun tweet qualifié trouvé**")
                logger.info("Aucun tweet qualifié trouvé dans ce cycle.")
                return

            await self.notifier.send_log(f"✅ **{len(tweets)} tweets qualifiés**\n⏳ Début du traitement...")
            logger.info(f"{len(tweets)} tweets qualifiés trouvés. Traitement...")
            
            # Traiter chaque tweet qualifié
            for tweet in tweets:
                try:
                    # Générer une réponse avec l'IA
                    reply = await self.responder.generate_reply(tweet.content, tweet.is_following)
                    
                    if not reply:
                        logger.warning(f"Impossible de générer une réponse pour: {tweet.url}")
                        continue
                    
                    # Délai aléatoire pour éviter la détection
                    await utils.random_delay(config.REPLY_DELAY_MIN, config.REPLY_DELAY_MAX)
                    
                    # Poster la réponse
                    success = await self.responder.post_reply(self.scroller.page, tweet, reply)
                    
                    if success:
                        replies_posted_count += 1
                        # 4. Notifier Telegram
                        await self.notifier.send_notification(tweet.url, reply)
                        # Délai entre les réponses pour paraître humain
                        wait_time = random.randint(config.REPLY_DELAY_MIN, config.REPLY_DELAY_MAX)
                        await self.notifier.send_log(f"⏳ **Attente {wait_time}s** avant prochain tweet...")
                        await asyncio.sleep(wait_time)
                    else:
                        await self.notifier.send_log(f"⚠️ **Échec du post**\n{tweet.url}")
                else:
                    await self.notifier.send_log(f"⚠️ **Pas de réponse générée**\n{tweet.url}")
                    logger.warning(f"Saut du tweet {tweet.url} (IA n'a pas généré de réponse)")

            # Sauvegarder les stats pour le prochain cycle
            self.last_tweets_found = len(tweets) if tweets else 0
            self.last_replies_posted = replies_posted_count

        except Exception as e:
            error_msg = str(e)
            
            # Vérifier si c'est une erreur de connexion browser
            if "Connection closed" in error_msg or "Target closed" in error_msg or "Browser has been closed" in error_msg:
                await self.notifier.send_log(f"⚠️ **Navigateur fermé**\nRedémarrage...")
                logger.warning(f"Navigateur fermé, redémarrage: {e}")
                
                # Essayer de redémarrer le navigateur
                try:
                    await self.scroller.close()
                    await self.scroller.start()
                    await self.scroller.login()
                    await self.notifier.send_log("✅ **Navigateur redémarré**")
                except Exception as restart_error:
                    await self.notifier.send_log(f"🚨 **Échec redémarrage**\n`{str(restart_error)[:150]}`")
                    logger.error(f"Impossible de redémarrer: {restart_error}")
            else:
                # Autre type d'erreur
                await self.notifier.send_log(f"🚨 **ERREUR CYCLE**\n`{error_msg[:200]}`")
                logger.exception(f"Erreur critique lors du cycle: {e}")

    async def start(self):
        """Démarre le bot."""
        self.is_running = True
        utils.setup_logger(config.LOG_LEVEL, config.LOG_FILE)
        
        logger.info("Démarrage du X Reply Bot...")
        
        try:
            # Initialiser le navigateur
            await self.scroller.start()
            
            # Connexion
            connected = await self.scroller.login()
            if not connected:
                logger.error("Impossible de se connecter à Twitter. Arrêt.")
                return

            while self.is_running:
                # Calculer le temps d'attente AVANT le cycle pour l'utiliser dans la notif
                # Mais ici on le calcule DANS run_cycle pour notification, donc on doit l'extraire
                # Pour simplifier, on va recalculer un délai ici ou modifier run_cycle pour retourner le délai
                # La modif précédente a déjà calculé next_run_minutes dans run_cycle pour la notif
                # Donc on va juste appeler run_cycle qui gère la notif
                
                await self.run_cycle()
                
                # Attendre avant le prochain cycle
                wait_time = utils.random.randint(config.CYCLE_DELAY_MIN, config.CYCLE_DELAY_MAX)
                logger.info(f"Cycle terminé. Prochain cycle dans {wait_time/60:.1f} minutes.")
                await asyncio.sleep(wait_time)

        except asyncio.CancelledError:
            logger.info("Tâche annulée.")
        finally:
            await self.scroller.close()
            logger.info("Bot arrêté proprement.")

    def stop(self):
        """Arrête la boucle principale."""
        self.is_running = False


async def main():
    bot = XReplyBot()
    
    # Gestion du signal d'arrêt (CTRL+C)
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, bot.stop)
        except NotImplementedError:
            # Pour Windows (add_signal_handler n'est pas implémenté)
            pass

    try:
        await bot.start()
    except KeyboardInterrupt:
        bot.stop()
        logger.info("Interruption détectée...")


if __name__ == "__main__":
    asyncio.run(main())
