# Implementación de un bot de ejemplo para TTBT1
# Este bot simula una tarea de login y una acción simple.

from core.bot import Bot

class SampleBot(Bot):
    def run(self):
        print(f"[{self.username}] Iniciando SampleBot...")
        # Simula login
        if "pass" in self.account_data:
            print(f"[{self.username}] Login exitoso usando contraseña: {self.account_data['pass']}")
        else:
            print(f"[{self.username}] No se encontró contraseña.")
        # Simula una acción
        print(f"[{self.username}] Acción de ejemplo ejecutada con proxy {self.proxy} y fingerprint {self.fingerprint}")