"""
Módulo para aplicar técnicas de evasión de detección de bots directamente en el driver.
"""

class EvasionSystem:
    """
    Encapsula técnicas para evadir la detección de automatización en el navegador.
    """
    def __init__(self, driver):
        """
        Inicializa el sistema de evasión con una instancia del driver de Selenium.

        Args:
            driver: La instancia del driver de Selenium a la que se aplicarán las técnicas.
        """
        self.driver = driver

    def evade_detection(self):
        """
        Aplica varias técnicas de evasión de detección al driver.

        Actualmente, incluye un truco para ocultar el flag `navigator.webdriver`.
        """
        # Add anti-bot evasion tricks here
        if self.driver:
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("[EVASION_SYSTEM] Applied webdriver hiding trick.")
            except Exception as e:
                print(f"[EVASION_SYSTEM] Error applying webdriver hiding trick: {e}")
        else:
            print("[EVASION_SYSTEM] No driver available to apply evasion techniques.")
