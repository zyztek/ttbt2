# Gestor de proxies para el framework TTBT1
# Permite la selección y desactivación de proxies.
# Todos los comentarios están en español.

import random

class ProxyManager:
    def __init__(self, proxies):
        """
        Inicializa el gestor de proxies.
        :param proxies: Lista de proxies.
        """
        self.proxies = proxies or []
        self.active_proxies = set(self.proxies)

    def get_random_active_proxy(self):
        """
        Devuelve un proxy activo aleatorio o None si no hay disponibles.
        """
        if not self.active_proxies:
            return None
        return random.choice(list(self.active_proxies))

    def deactivate_proxy(self, proxy):
        """
        Elimina un proxy de la lista de proxies activos (por ejemplo, si es detectado como bloqueado).
        """
        self.active_proxies.discard(proxy)