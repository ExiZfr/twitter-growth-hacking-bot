# -*- coding: utf-8 -*-
"""
Module de scraping de la Timeline Twitter/X.
Utilise Playwright pour simuler un utilisateur humain.
"""

import asyncio
import random
import time
import os
import json
from typing import List, Optional, Dict
from loguru import logger
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle

import config
import utils
from proxies import ProxyRotator, ProxyConfig


class Tweet:
    """Représente un tweet extrait de la timeline."""
    def __init__(self, element: ElementHandle, content: str, url: str, likes: int, time_text: str, is_following: bool = False):
        self.element = element
        self.content = content
        self.url = url
        self.likes = likes
        self.time_text = time_text
        self.age_hours = utils.parse_tweet_age(time_text)
        self.is_following = is_following  # True si l'auteur est suivi

    def __str__(self):
        follow_status = " [FOLLOWING]" if self.is_following else ""
        return f"Tweet(likes={self.likes}, age={self.age_hours}h{follow_status}, url={self.url})"


def is_tech_related(content: str) -> bool:
    """
    Vérifie si le contenu est lié aux topics tech autorisés.
    Bloque les tweets politiques, conspirations, et crypto trading.
    """
    content_lower = content.lower()
    
    # D'abord vérifier les mots-clés bloqués (politique, conspiration, etc.)
    for keyword in config.BLOCKED_KEYWORDS:
        if keyword.lower() in content_lower:
            logger.debug(f"❌ Tweet bloqué (mot-clé interdit: {keyword})")
            return False
    
    # Ensuite vérifier la présence de mots-clés tech autorisés
    for keyword in config.ALLOWED_KEYWORDS:
        if keyword.lower() in content_lower:
            logger.debug(f"✅ Tweet accepté (mot-clé tech: {keyword})")
            return True
    
    # Par défaut, rejeter si aucun mot-clé tech trouvé
    logger.debug("⚠️ Tweet rejeté (aucun mot-clé tech trouvé)")
    return False


class TimelineScroller:
    """Gère la navigation et l'extraction des tweets de la Timeline."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.proxy_rotator = ProxyRotator(config.PROXIES)
        self.seen_tweet_ids = set()
        self.last_refresh_time = time.time()
        self.next_refresh_interval = random.randint(config.REFRESH_INTERVAL_MIN, config.REFRESH_INTERVAL_MAX)

    async def start(self):
        """Initialise Playwright et le navigateur avec un proxy."""
        self.playwright = await async_playwright().start()
        
        # Utiliser le tunnel HTTP local (Gost) au lieu de SOCKS5 direct
        # Gost gère l'authentification SOCKS5 pour nous
        proxy_settings = {
            "server": "http://127.0.0.1:1080"
            # Pas d'username/password, Gost s'en occupe
        }
        
        user_agent = utils.get_random_user_agent(config.USER_AGENTS)
        
        logger.info(f"Lancement du navigateur (Proxy: HTTP tunnel local, UA: {user_agent[:50]}...)")

        
        self.browser = await self.playwright.chromium.launch(
            headless=config.HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": config.VIEWPORT_WIDTH, "height": config.VIEWPORT_HEIGHT},
            proxy=proxy_settings
        )
        
        await self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(config.BROWSER_TIMEOUT)

    async def login(self) -> bool:
        """Charge les cookies pré-authentifiés au lieu du login manuel."""
        try:
            logger.info("Chargement des cookies d'authentification...")
            
            # Charger les cookies depuis le fichier
            
            cookie_file = os.path.join(os.path.dirname(__file__), "cookies.json")
            
            if not os.path.exists(cookie_file):
                logger.error(f"Fichier cookies.json introuvable : {cookie_file}")
                return False
            
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
            
            # Ajouter les cookies au contexte
            await self.context.add_cookies(cookies)
            logger.info(f"{len(cookies)} cookies chargés avec succès")
            
            # Naviguer vers la page d'accueil pour vérifier la session
            await self.page.goto("https://x.com/home", wait_until="domcontentloaded")
            await utils.random_delay(2, 4)
            
            # Vérifier si on est bien connecté (présence du bouton de tweet)
            try:
                await self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                logger.info(" Authentification réussie via cookies!")
                return True
            except:
                logger.warning("Session peut-être expirée, mais on continue...")
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des cookies: {e}")
            return False

    async def maybe_refresh_page(self):
        """Vérifie si un refresh est nécessaire et l'effectue."""
        elapsed = time.time() - self.last_refresh_time
        if elapsed >= self.next_refresh_interval:
            logger.info(f"Refresh de la page (après {elapsed/60:.1f} min)")
            await self.page.reload()
            await utils.random_delay(3, 6)
            self.last_refresh_time = time.time()
            self.next_refresh_interval = random.randint(config.REFRESH_INTERVAL_MIN, config.REFRESH_INTERVAL_MAX)
            logger.info(f"Prochain refresh dans {self.next_refresh_interval/60:.1f} min")

    async def perform_random_action(self, tweet_cell: ElementHandle):
        """Effectue des actions aléatoires sur un tweet (like, RT, bookmark)."""
        try:
            # Random Like
            if random.random() < config.RANDOM_LIKE_CHANCE:
                like_btn = await tweet_cell.query_selector("button[data-testid='like']")
                if like_btn:
                    await utils.human_mouse_move(self.page, like_btn)
                    await like_btn.click()
                    logger.info("👍 Action aléatoire: Like")
                    await utils.random_delay(0.5, 1.5)
            
            # Random Retweet
            if random.random() < config.RANDOM_RT_CHANCE:
                rt_btn = await tweet_cell.query_selector("button[data-testid='retweet']")
                if rt_btn:
                    await utils.human_mouse_move(self.page, rt_btn)
                    await rt_btn.click()
                    await utils.random_delay(0.5, 1)
                    # Confirmer le RT (cliquer sur "Repost")
                    confirm_btn = await self.page.query_selector("[data-testid='retweetConfirm']")
                    if confirm_btn:
                        await confirm_btn.click()
                        logger.info("🔄 Action aléatoire: Retweet")
                    await utils.random_delay(0.5, 1.5)
            
            # Random Bookmark
            if random.random() < config.RANDOM_BOOKMARK_CHANCE:
                bookmark_btn = await tweet_cell.query_selector("button[data-testid='bookmark']")
                if bookmark_btn:
                    await utils.human_mouse_move(self.page, bookmark_btn)
                    await bookmark_btn.click()
                    logger.info("🔖 Action aléatoire: Bookmark")
                    await utils.random_delay(0.5, 1.5)
                    
        except Exception as e:
            logger.debug(f"Erreur action aléatoire: {e}")

    async def infinite_scroll_and_scan(self) -> List[Tweet]:
        """
        Scrolle la timeline de façon continue et naturelle.
        Effectue des actions aléatoires et retourne les tweets qualifiés.
        """
        qualified_tweets = []
        
        logger.info("Démarrage du scroll infini avec actions organiques...")
        
        # S'assurer d'être sur la home
        if "home" not in self.page.url:
            await self.page.goto("https://x.com/home")
            await utils.random_delay(3, 5)

        # Nombre de scrolls aléatoire pour ce cycle (réduit pour cycles rapides)
        scroll_count = random.randint(3, 8)
        
        for i in range(scroll_count):
            # Vérifier si refresh nécessaire
            await self.maybe_refresh_page()
            
            # Scroll avec intensité variable
            intensity = random.choice(["light", "medium", "medium", "heavy"])
            await utils.random_scroll(self.page, "down", intensity)
            
            # Mouvement de souris aléatoire occasionnel
            if random.random() < 0.3:
                await utils.random_mouse_movement(self.page)
            
            # Délai naturel entre scrolls
            await utils.random_delay(config.SCROLL_DELAY_MIN, config.SCROLL_DELAY_MAX)
            
            # Extraire les tweets visibles
            tweet_cells = await self.page.query_selector_all("article[data-testid='tweet']")
            
            for cell in tweet_cells:
                try:
                    # Effectuer des actions aléatoires sur certains tweets
                    await self.perform_random_action(cell)
                    
                    # Vérifier la langue
                    lang_el = await cell.query_selector("div[lang]")
                    if not lang_el:
                        continue
                    
                    lang = await lang_el.get_attribute("lang")
                    if config.LANGUAGE_FILTER and lang != config.LANGUAGE_FILTER:
                        continue
                        
                    content = await lang_el.inner_text()
                    
                    # FILTRAGE TECH: Vérifier que le contenu est tech-related
                    if not is_tech_related(content):
                        continue
                    
                    # Extraire les likes
                    like_el = await cell.query_selector("button[data-testid='like']")
                    if not like_el:
                        continue
                    aria_label = await like_el.get_attribute("aria-label") or ""
                    likes = utils.parse_engagement_count(aria_label.split(" ")[0])
                    
                    # Extraire l'âge
                    time_el = await cell.query_selector("time")
                    if not time_el:
                        continue
                    time_text = await time_el.inner_text()
                    age_hours = utils.parse_tweet_age(time_text)
                    
                    # Extraire l'URL
                    link_el = await cell.query_selector("a[href*='/status/']")
                    if not link_el:
                        continue
                    tweet_url = "https://x.com" + await link_el.get_attribute("href")
                    tweet_id = tweet_url.split("/")[-1]
                    
                    # Détecter si l'auteur est suivi
                    is_following = False
                    try:
                        # Chercher le bouton Following dans le tweet
                        following_btn = await cell.query_selector("button[data-testid$='unfollow']")
                        if following_btn:
                            is_following = True
                    except:
                        pass
                    
                    # Vérifier les critères pour réponse
                    if (likes >= config.MIN_LIKES and 
                        age_hours <= config.MAX_TWEET_AGE_HOURS and 
                        tweet_id not in self.seen_tweet_ids):
                        
                        follow_label = " [FOLLOWING]" if is_following else ""
                        logger.info(f"Tweet qualifié trouvé: {tweet_url} ({likes} likes, {age_hours}h){follow_label}")
                        
                        tweet_obj = Tweet(cell, content, tweet_url, likes, time_text, is_following)
                        qualified_tweets.append(tweet_obj)
                        self.seen_tweet_ids.add(tweet_id)
                        
                        if len(qualified_tweets) >= config.MAX_REPLIES_PER_CYCLE:
                            return qualified_tweets
                            
                except Exception as e:
                    logger.debug(f"Erreur lors de l'extraction d'un tweet: {e}")
                    continue
        
        return qualified_tweets

    async def get_qualified_tweets(self) -> List[Tweet]:
        """Wrapper pour la compatibilité - utilise le scroll infini."""
        return await self.infinite_scroll_and_scan()

    async def close(self):
        """Ferme le navigateur et Playwright."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Navigateur fermé.")

