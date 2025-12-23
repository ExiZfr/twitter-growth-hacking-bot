# -*- coding: utf-8 -*-
"""
Module de génération de réponses par l'IA (gpt-5-mini) et postage.
"""

from openai import OpenAI
from loguru import logger
from playwright.async_api import Page, ElementHandle
import asyncio

import config
import utils
from scroller import Tweet


class AIResponder:
    """Gère la génération de réponses via OpenAI et l'interaction pour poster."""
    
    def __init__(self):
        # Utilisation du client synchrone pour éviter les problèmes de loop asyncio/httpx
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL

    async def generate_reply(self, tweet_content: str) -> str:
        """Génère une réponse avec GPT-5-mini."""
        if not tweet_content:
            return ""
            
        logger.info(f"Génération de réponse pour le tweet: {tweet_content[:50]}...")
        
        try:
            # Pour gpt-5-mini (type o1), on passe tout en 'user'
            full_prompt = f"{config.AI_SYSTEM_PROMPT}\n\nTweet to reply to: \"{tweet_content}\"\n\nRemember: Be short, human-like, and blunt. English only."
            
            # Exécution dans un thread séparé pour ne pas bloquer la loop principale
            # et éviter les crashs liés au client asynchrone
            def call_openai():
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    max_completion_tokens=config.MAX_RESPONSE_TOKENS
                )

            # Utilisation de to_thread pour rendre l'appel async-friendly
            response = await asyncio.to_thread(call_openai)
            
            # Debug
            logger.info(f"OpenAI Finish Reason: {response.choices[0].finish_reason}")
            
            reply_text = response.choices[0].message.content
            if not reply_text:
                reply_text = ""
            
            reply_text = reply_text.strip().strip('"').strip("'")
            
            # Supprimer les tirets longs (—) qui font pas humain
            reply_text = reply_text.replace("—", "-").replace("–", "-")
            
            logger.info(f"Réponse générée: {reply_text}")
            return reply_text
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération OpenAI: {e}")
            return ""

    async def post_reply(self, page: Page, tweet: Tweet, reply_text: str) -> bool:
        """Clique sur répondre, tape la réponse et valide."""
        if not reply_text:
            return False
            
        logger.info(f"Posting reply to: {tweet.url}")
        
        try:
            # 1. Cliquer sur le bouton Répondre (Reply)
            reply_button = await tweet.element.query_selector("button[data-testid='reply']")
            if not reply_button:
                logger.error("Bouton 'reply' non trouvé sur le tweet")
                return False
                
            await utils.human_mouse_move(page, reply_button)
            await reply_button.click()
            await utils.random_delay(1.5, 3)
            
            # 2. Taper la réponse
            # Sélecteur pour la zone de texte de réponse (DraftEditor)
            # On utilise .first() car Twitter affiche 2 textareas (timeline + modal)
            editor = page.locator("div[data-testid='tweetTextarea_0']").first
            await editor.wait_for(state="visible", timeout=5000)
            
            # Cliquer pour focus puis taper
            await editor.click()
            await utils.random_delay(0.5, 1)
            await page.keyboard.type(reply_text, delay=50)
            await utils.random_delay(1, 2)
            
            # 3. Cliquer sur "Post" ou "Reply"
            # Le bouton a souvent data-testid="tweetButtonInline"
            post_button = await page.query_selector("button[data-testid='tweetButton']")
            if not post_button:
                # Fallback sur un autre testid possible dans la popup
                post_button = await page.query_selector("button[data-testid='tweetButtonInline']")
            
            if post_button:
                await utils.human_mouse_move(page, post_button)
                await post_button.click()
                logger.info("Réponse postée avec succès!")
                await utils.random_delay(2, 4)
                return True
            else:
                logger.error("Bouton Post non trouvé")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du postage de la réponse: {e}")
            return False
