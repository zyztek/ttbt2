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

    def apply_evasion(self, bot):
        """
        Aplica un nuevo fingerprint y proxy a un bot.
        :param bot: Instancia del bot al que se aplicará la evasión.
        """
        fp = self.rotate_fingerprint()
        px = self.rotate_proxy()

        if fp: # Ensure a fingerprint was returned
            bot.assign_fingerprint(fp)

        if px: # Ensure a proxy was returned
            bot.assign_proxy(px)
