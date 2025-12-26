# -*- coding: utf-8 -*-
"""
Module de génération de réponses par l'IA (gpt-5-mini) et postage.
"""

from openai import OpenAI
from loguru import logger
from playwright.async_api import Page
import asyncio

import config
import utils


class AIResponder:
    """Gère la génération de réponses via OpenAI et l'interaction pour poster."""
    
    def __init__(self):
        # Utilisation du client synchrone pour éviter les problèmes de loop asyncio/httpx
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL

    async def generate_reply(self, tweet_content: str, is_following: bool = False) -> str:
        """Génère une réponse avec GPT-5-mini."""
        if not tweet_content:
            return ""
        
        follow_label = " [FOLLOWING]" if is_following else ""
        logger.info(f"Génération de réponse pour le tweet{follow_label}: {tweet_content[:50]}...")
        
        try:
            # Choisir le prompt selon si l'auteur est suivi
            system_prompt = config.AI_SYSTEM_PROMPT_FRIENDLY if is_following else config.AI_SYSTEM_PROMPT
            tone_reminder = "Be friendly and supportive" if is_following else "Be short, human-like, and blunt"
            
            # Pour gpt-5-mini (type o1), on passe tout en 'user'
            full_prompt = f"{system_prompt}\n\nTweet to reply to: \"{tweet_content}\"\n\nRemember: {tone_reminder}. English only."
            
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

    async def post_reply(self, page: Page, tweet_url: str, reply_text: str) -> bool:
        """
        Navigate to tweet page and post reply with retry logic.
        This approach is more reliable than replying from timeline (stale elements).
        """
        if not reply_text:
            return False
        
        max_attempts = 3
        original_url = page.url
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"Posting reply to: {tweet_url} (attempt {attempt + 1}/{max_attempts})")
                
                # 1. Navigate to the tweet page
                await page.goto(tweet_url, wait_until="domcontentloaded")
                await utils.random_delay(2, 4)
                
                # 2. Find and click on the reply text area
                # On tweet page, the reply box is at the bottom
                reply_box = page.locator("div[data-testid='tweetTextarea_0']").first
                await reply_box.wait_for(state="visible", timeout=10000)
                
                await utils.human_mouse_move(page, await reply_box.element_handle())
                await reply_box.click()
                await utils.random_delay(0.5, 1.5)
                
                # 3. Type the reply with human-like delays
                await page.keyboard.type(reply_text, delay=50)
                await utils.random_delay(1, 2)
                
                # 4. Click the reply/post button
                # Try multiple selectors for reliability
                post_button = page.locator("button[data-testid='tweetButton']").first
                
                try:
                    await post_button.wait_for(state="visible", timeout=5000)
                except:
                    # Fallback selector
                    post_button = page.locator("button[data-testid='tweetButtonInline']").first
                    await post_button.wait_for(state="visible", timeout=5000)
                
                await utils.human_mouse_move(page, await post_button.element_handle())
                await post_button.click()
                
                # 5. Wait and verify post success
                await utils.random_delay(3, 5)
                
                # Check for error toasts or rate limit messages
                error_toast = await page.query_selector("[data-testid='toast']")
                if error_toast:
                    toast_text = await error_toast.text_content()
                    if toast_text and ("limit" in toast_text.lower() or "error" in toast_text.lower()):
                        logger.warning(f"Twitter error detected: {toast_text}")
                        raise Exception(f"Twitter error: {toast_text}")
                
                logger.info("Réponse postée avec succès!")
                
                # 6. Return to home timeline
                await page.goto("https://x.com/home", wait_until="domcontentloaded")
                await utils.random_delay(2, 3)
                
                return True
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
                
                if attempt < max_attempts - 1:
                    # Wait before retry
                    await utils.random_delay(3, 6)
                    
                    # Try to recover by going back to home
                    try:
                        await page.goto("https://x.com/home", wait_until="domcontentloaded")
                        await utils.random_delay(2, 3)
                    except:
                        pass
                else:
                    logger.error(f"All {max_attempts} attempts failed for {tweet_url}")
        
        # Return to home even on failure
        try:
            await page.goto("https://x.com/home", wait_until="domcontentloaded")
        except:
            pass
            
        return False
