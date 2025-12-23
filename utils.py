# -*- coding: utf-8 -*-
"""
Utilitaires pour le comportement humain et le logging.
Fournit des fonctions pour simuler un comportement naturel.
"""

import asyncio
import random
import sys
from datetime import datetime
from loguru import logger
from playwright.async_api import Page, Locator


def setup_logger(log_level: str = "INFO", log_file: str = "bot.log"):
    """
    Configure le logger avec rotation de fichiers.
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
        log_file: Chemin du fichier de log
    """
    # Supprimer le handler par défaut
    logger.remove()
    
    # Format personnalisé
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Handler console
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # Handler fichier avec rotation
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    return logger


async def random_delay(min_seconds: float, max_seconds: float):
    """
    Attend un délai aléatoire entre min et max secondes.
    
    Args:
        min_seconds: Délai minimum
        max_seconds: Délai maximum
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Délai aléatoire: {delay:.2f}s")
    await asyncio.sleep(delay)


async def human_typing(page: Page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
    """
    Tape du texte caractère par caractère avec des délais variables.
    Simule une frappe humaine naturelle.
    
    Args:
        page: Page Playwright
        selector: Sélecteur CSS de l'élément
        text: Texte à taper
        min_delay: Délai minimum entre caractères
        max_delay: Délai maximum entre caractères
    """
    element = page.locator(selector)
    await element.click()
    
    for char in text:
        await element.type(char, delay=random.uniform(min_delay * 1000, max_delay * 1000))
        
        # Pause occasionnelle plus longue (simulation de réflexion)
        if random.random() < 0.05:  # 5% de chance
            await asyncio.sleep(random.uniform(0.3, 0.8))


async def human_mouse_move(page: Page, target: Locator, steps: int = 10):
    """
    Déplace la souris vers un élément avec un mouvement naturel.
    
    Args:
        page: Page Playwright
        target: Élément cible (Locator)
        steps: Nombre d'étapes intermédiaires
    """
    try:
        # Obtenir la position de l'élément
        box = await target.bounding_box()
        if not box:
            return
        
        # Point central avec léger offset aléatoire
        target_x = box["x"] + box["width"] / 2 + random.randint(-10, 10)
        target_y = box["y"] + box["height"] / 2 + random.randint(-5, 5)
        
        # Mouvement vers la cible
        await page.mouse.move(target_x, target_y, steps=steps)
        
        # Petit délai avant action
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
    except Exception as e:
        logger.debug(f"Mouvement souris échoué: {e}")


async def random_scroll(page: Page, direction: str = "down", intensity: str = "medium"):
    """
    Effectue un scroll aléatoire avec comportement humain.
    
    Args:
        page: Page Playwright
        direction: "up" ou "down"
        intensity: "light", "medium", "heavy"
    """
    intensities = {
        "light": (100, 300),
        "medium": (300, 600),
        "heavy": (600, 1000)
    }
    
    min_scroll, max_scroll = intensities.get(intensity, intensities["medium"])
    scroll_amount = random.randint(min_scroll, max_scroll)
    
    if direction == "up":
        scroll_amount = -scroll_amount
    
    # Scroll avec comportement naturel (pas instantané)
    await page.mouse.wheel(0, scroll_amount)
    
    # Petit délai après scroll
    await asyncio.sleep(random.uniform(0.3, 0.8))
    
    logger.debug(f"Scroll {direction} de {abs(scroll_amount)}px")


async def simulate_reading(page: Page, min_time: float = 1.0, max_time: float = 4.0):
    """
    Simule le temps de lecture d'un contenu.
    
    Args:
        page: Page Playwright
        min_time: Temps minimum de lecture
        max_time: Temps maximum de lecture
    """
    reading_time = random.uniform(min_time, max_time)
    logger.debug(f"Simulation lecture: {reading_time:.2f}s")
    
    # Parfois faire un petit scroll pendant la lecture
    if random.random() < 0.3:  # 30% de chance
        await asyncio.sleep(reading_time / 2)
        await random_scroll(page, "down", "light")
        await asyncio.sleep(reading_time / 2)
    else:
        await asyncio.sleep(reading_time)


async def random_mouse_movement(page: Page):
    """
    Effectue un mouvement de souris aléatoire sur la page.
    Simule un utilisateur qui bouge sa souris naturellement.
    """
    try:
        viewport = page.viewport_size
        if not viewport:
            return
            
        # Position aléatoire dans la zone visible
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        
        # Mouvement avec étapes pour un effet naturel
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        
    except Exception as e:
        logger.debug(f"Mouvement souris aléatoire échoué: {e}")


def get_random_user_agent(user_agents: list[str]) -> str:
    """
    Retourne un User-Agent aléatoire de la liste.
    
    Args:
        user_agents: Liste des User-Agents disponibles
        
    Returns:
        User-Agent sélectionné
    """
    return random.choice(user_agents)


def parse_tweet_age(time_text: str) -> int:
    """
    Parse l'âge d'un tweet depuis le texte affiché par Twitter.
    
    Args:
        time_text: Texte du temps (ex: "2h", "30m", "5s", "Dec 22")
        
    Returns:
        Âge en heures (approximatif), ou 999 si non parsable
    """
    try:
        time_text = time_text.lower().strip()
        
        if 's' in time_text and time_text.replace('s', '').isdigit():
            return 0  # Secondes = moins d'une heure
            
        if 'm' in time_text and time_text.replace('m', '').isdigit():
            minutes = int(time_text.replace('m', ''))
            return minutes // 60 if minutes >= 60 else 0
            
        if 'h' in time_text and time_text.replace('h', '').isdigit():
            return int(time_text.replace('h', ''))
            
        # Si c'est une date (plus d'un jour), retourner une grande valeur
        return 999
        
    except Exception:
        return 999


def parse_engagement_count(count_text: str) -> int:
    """
    Parse le nombre d'engagements depuis le texte Twitter.
    
    Args:
        count_text: Texte du compteur (ex: "1.2K", "500", "2.5M")
        
    Returns:
        Nombre entier
    """
    try:
        count_text = count_text.strip().upper()
        
        if not count_text or count_text == "":
            return 0
            
        if 'K' in count_text:
            return int(float(count_text.replace('K', '')) * 1000)
            
        if 'M' in count_text:
            return int(float(count_text.replace('M', '')) * 1000000)
            
        # Retirer les virgules et espaces
        count_text = count_text.replace(',', '').replace(' ', '')
        
        return int(count_text)
        
    except Exception:
        return 0


def format_timestamp() -> str:
    """Retourne l'horodatage actuel formaté."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Test du module si exécuté directement
if __name__ == "__main__":
    print("=== Test du module utils ===\n")
    
    # Test parsing engagement
    test_counts = ["500", "1.2K", "2.5M", "1,234", ""]
    for count in test_counts:
        print(f"  '{count}' -> {parse_engagement_count(count)}")
    
    print("\nTest parsing âge tweet:")
    test_ages = ["30s", "45m", "2h", "12h", "Dec 22"]
    for age in test_ages:
        print(f"  '{age}' -> {parse_tweet_age(age)}h")
