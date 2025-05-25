# Módulo de evasión para el framework TTBT1
# Proporciona utilidades para rotar fingerprints y proxies.
# Todos los comentarios están en español.

import random

class Evasion:
    def __init__(self, fingerprints, proxies):
        """
        Inicializa el módulo de evasión.
        :param fingerprints: Lista de fingerprints disponibles.
        :param proxies: Lista de proxies disponibles.
        """
        self.fingerprints = fingerprints
        self.proxies = proxies

    def rotate_fingerprint(self):
        """
        Selecciona aleatoriamente un fingerprint.
        :return: Un fingerprint o None si la lista está vacía.
        """
        if not self.fingerprints:
            return None
        return random.choice(self.fingerprints)

    def rotate_proxy(self):
        """
        Selecciona aleatoriamente un proxy.
        :return: Un proxy o None si la lista está vacía.
        """
        if not self.proxies:
            return None
        return random.choice(self.proxies)