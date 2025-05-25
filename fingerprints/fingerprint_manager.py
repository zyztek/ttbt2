# Gestor de fingerprints para el framework TTBT1
# Permite la selección aleatoria de fingerprints.
# Todos los comentarios están en español.

import random

class FingerprintManager:
    def __init__(self, fingerprints):
        """
        Inicializa el gestor de fingerprints.
        :param fingerprints: Lista de fingerprints.
        """
        self.fingerprints = fingerprints or []

    def get_fingerprint(self):
        """
        Devuelve un fingerprint aleatorio o None si no hay disponibles.
        """
        if not self.fingerprints:
            return None
        return random.choice(self.fingerprints)