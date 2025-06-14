"""
Módulo de evasión de detección centrado en datos (fingerprints y proxies).

Este módulo proporciona la clase `Evasion`, que gestiona la rotación de
identidades de navegador (fingerprints) y direcciones IP (proxies) para
ayudar a los bots a evitar la detección basada en patrones de estos elementos.

Se diferencia de `core.evasion_system`, que se enfoca en modificar
directamente el estado del driver del navegador para ocultar indicadores
de automatización (ej. `navigator.webdriver`).
"""
# Módulo de evasión para el framework TTBT1
# Proporciona utilidades para rotar fingerprints y proxies.
# Todos los comentarios están en español.

import random

class Evasion:
    """
    Gestiona y rota listas de fingerprints y proxies para un bot.

    Esta clase mantiene colecciones de fingerprints (perfiles de navegador)
    y proxies (direcciones IP). Ofrece métodos para seleccionar aleatoriamente
    un elemento de cada colección y para aplicar estos elementos a una instancia
    de bot dada, asumiendo que el bot tiene métodos `assign_fingerprint` y
    `assign_proxy`.
    """
    def __init__(self, fingerprints, proxies):
        """
        Inicializa la instancia de Evasion con listas de fingerprints y proxies.

        Args:
            fingerprints (list): Una lista de fingerprints (ej. strings o dicts) disponibles.
            proxies (list): Una lista de proxies (ej. strings de 'ip:port') disponibles.
        """
        self.fingerprints = fingerprints
        self.proxies = proxies

    def rotate_fingerprint(self):
        """
        Selecciona aleatoriamente un fingerprint de la lista `self.fingerprints`.

        Returns:
            str/dict/any or None: Un fingerprint de la lista, o None si la lista
                                  `self.fingerprints` está vacía. El tipo exacto
                                  depende de cómo se almacenen los fingerprints.
        """
        if not self.fingerprints:
            return None
        return random.choice(self.fingerprints)

    def rotate_proxy(self):
        """
        Selecciona aleatoriamente un proxy de la lista `self.proxies`.

        Returns:
            str or None: Una cadena de proxy (ej. 'ip:port') de la lista, o None
                         si la lista `self.proxies` está vacía.
        """
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def apply_evasion(self, bot):
        """
        Aplica un fingerprint y un proxy rotados a la instancia de bot proporcionada.

        Obtiene un nuevo fingerprint llamando a `self.rotate_fingerprint()` y un
        nuevo proxy llamando a `self.rotate_proxy()`. Luego, si estos valores
        no son None, los asigna al bot utilizando los métodos `bot.assign_fingerprint()`
        y `bot.assign_proxy()`.

        Args:
            bot: Una instancia de un objeto bot que se espera tenga los métodos
                 `assign_fingerprint(fp)` y `assign_proxy(px)`.
        """
        fp = self.rotate_fingerprint()
        px = self.rotate_proxy()

        if fp: # Ensure a fingerprint was returned
            bot.assign_fingerprint(fp)

        if px: # Ensure a proxy was returned
            bot.assign_proxy(px)
