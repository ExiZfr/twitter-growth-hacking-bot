# -*- coding: utf-8 -*-
"""
Module de gestion des proxies SOCKS5 avec rotation.
Parse le format spécifique: socks5://ip:port:user:pass
"""

import random
import re
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class ProxyConfig:
    """Configuration d'un proxy parsé."""
    server: str           # Format: socks5://ip:port
    username: str
    password: str
    
    def to_playwright_format(self) -> dict:
        """Retourne le format attendu par Playwright."""
        return {
            "server": self.server,
            "username": self.username,
            "password": self.password
        }
    
    def __str__(self) -> str:
        return f"{self.server} (user: {self.username[:4]}...)"


def parse_proxy(proxy_string: str) -> Optional[ProxyConfig]:
    """
    Parse une chaîne de proxy au format: socks5://ip:port:user:pass
    
    Args:
        proxy_string: Chaîne du proxy à parser
        
    Returns:
        ProxyConfig si le parsing réussit, None sinon
    """
    try:
        # Pattern pour: socks5://ip:port:user:pass
        # On sait que le format est IP:PORT:USER:PASS après le préfixe
        if not proxy_string.startswith("socks5://"):
            logger.warning(f"Proxy invalide (doit commencer par socks5://): {proxy_string}")
            return None
        
        # Retirer le préfixe socks5://
        remaining = proxy_string[len("socks5://"):]
        
        # Split par ":" - on a IP:PORT:USER:PASS
        parts = remaining.split(":")
        
        if len(parts) != 4:
            logger.warning(f"Proxy invalide (format attendu ip:port:user:pass): {proxy_string}")
            return None
        
        ip, port, username, password = parts
        
        # Valider le port
        if not port.isdigit():
            logger.warning(f"Port invalide: {port}")
            return None
        
        server = f"socks5://{ip}:{port}"
        
        return ProxyConfig(
            server=server,
            username=username,
            password=password
        )
        
    except Exception as e:
        logger.error(f"Erreur parsing proxy '{proxy_string}': {e}")
        return None


class ProxyRotator:
    """
    Gestionnaire de rotation de proxies.
    Sélectionne aléatoirement un proxy parmi la liste disponible.
    """
    
    def __init__(self, proxy_strings: list[str]):
        """
        Initialise le rotateur avec une liste de chaînes de proxy.
        
        Args:
            proxy_strings: Liste des proxies au format socks5://ip:port:user:pass
        """
        self.proxies: list[ProxyConfig] = []
        self._current_index = 0
        
        for proxy_str in proxy_strings:
            parsed = parse_proxy(proxy_str)
            if parsed:
                self.proxies.append(parsed)
                logger.info(f"Proxy chargé: {parsed}")
            else:
                logger.warning(f"Proxy ignoré (parsing échoué): {proxy_str}")
        
        if not self.proxies:
            logger.warning("Aucun proxy valide chargé! Le bot utilisera une connexion directe.")
    
    def get_random(self) -> Optional[ProxyConfig]:
        """Retourne un proxy aléatoire."""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_next(self) -> Optional[ProxyConfig]:
        """Retourne le prochain proxy en rotation séquentielle."""
        if not self.proxies:
            return None
        proxy = self.proxies[self._current_index]
        self._current_index = (self._current_index + 1) % len(self.proxies)
        return proxy
    
    def has_proxies(self) -> bool:
        """Vérifie si des proxies sont disponibles."""
        return len(self.proxies) > 0
    
    def count(self) -> int:
        """Retourne le nombre de proxies disponibles."""
        return len(self.proxies)


# Test du module si exécuté directement
if __name__ == "__main__":
    from config import PROXIES
    
    print("=== Test du module proxies ===\n")
    
    rotator = ProxyRotator(PROXIES)
    
    print(f"\nProxies chargés: {rotator.count()}")
    
    for i in range(3):
        proxy = rotator.get_random()
        if proxy:
            print(f"\nProxy aléatoire #{i+1}:")
            print(f"  Server: {proxy.server}")
            print(f"  Username: {proxy.username}")
            print(f"  Password: {proxy.password[:4]}...")
            print(f"  Playwright format: {proxy.to_playwright_format()}")
