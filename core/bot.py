"""
Módulo principal del bot para TikTok.

Este módulo define la clase TikTokBot, que encapsula la lógica para interactuar
con la plataforma TikTok, incluyendo la inicialización del driver de Selenium,
autenticación, y la ejecución de acciones orgánicas simulando comportamiento humano.
"""
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from core.account_manager import AccountManager
from core.behavior import HumanBehaviorSimulator

class TikTokBot:
    """
    Clase principal para el bot de TikTok.

    Gestiona la interacción con TikTok, incluyendo la configuración del navegador,
    autenticación de cuenta, y la ejecución de acciones en la plataforma.
    Utiliza AccountManager para la gestión de cuentas y HumanBehaviorSimulator
    para simular interacciones humanas realistas.
    """
    def __init__(self, _email=None, _account_details=None):
        """
        Inicializa una instancia de TikTokBot.

        Args:
            _email (str, optional): Email de la cuenta a utilizar. No se usa directamente
                                   en esta versión pero se mantiene por compatibilidad con tests.
            _account_details (dict, optional): Detalles de la cuenta. No se usa directamente
                                             en esta versión.
        """
        self.driver = self._init_driver()
        # TODO: AccountManager debería idealmente recibir un filepath o configuración.
        self.account_manager = AccountManager()
        self.proxy = None
        self.fingerprint = None
        self.behavior = HumanBehaviorSimulator(self.driver)

    def assign_proxy(self, proxy_value):
        """Asigna un valor de proxy al bot."""
        self.proxy = proxy_value

    def assign_fingerprint(self, fingerprint_value):
        """Asigna un valor de fingerprint al bot."""
        self.fingerprint = fingerprint_value

    def _init_driver(self):
        """
        Inicializa el driver de Selenium (Chrome) con opciones específicas.

        Configura el navegador para operar en modo headless, con un user-agent
        móvil y deshabilita la GPU y el sandbox para compatibilidad en servidores.

        Returns:
            selenium.webdriver.Chrome: Instancia del driver de Chrome configurado.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
        return webdriver.Chrome(options=options)

    def _authenticate(self):
        """
        Autentica el bot en TikTok utilizando una cuenta del AccountManager.

        Navega a la página de login, introduce las credenciales y envía el formulario.
        Utiliza HumanBehaviorSimulator para las interacciones.

        Returns:
            bool: True si la autenticación fue exitosa, False en caso contrario.
        """
        account = self.account_manager.get_next_account()
        if not account or not account.get("email") or not account.get("password"):
            print("No se encontró ninguna cuenta válida en la base de datos.")
            return False
        try:
            self.driver.get("https://www.tiktok.com/login")
            self.behavior.random_delay(3, 5) # Uncommented

            # Llenar campos de login
            email_field = self.driver.find_element(By.NAME, "username")
            self.behavior.human_type(email_field, account['email']) # Uncommented

            pass_field = self.driver.find_element(By.NAME, "password")
            self.behavior.human_type(pass_field, account['password']) # Uncommented

            # Enviar formulario
            submit_btn = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            self.behavior.human_click(submit_btn) # Uncommented

            return True
        except Exception as e:
            print(f"Error de autenticación: {str(e)}")
            return False

    def run_session(self):
        """
        Ejecuta una sesión completa del bot.

        Intenta autenticar y, si tiene éxito, realiza acciones orgánicas.
        """
        if self._authenticate():
            self._perform_organic_actions()

    def _perform_organic_actions(self):
        """
        Realiza acciones orgánicas en TikTok después de la autenticación.

        Simula ver videos, dar 'like' y hacer scroll, con pausas aleatorias
        para imitar el comportamiento humano. El número de videos a ver se
        controla mediante la variable de entorno MAX_VIEWS_PER_HOUR.
        """
        max_views = int(os.getenv("MAX_VIEWS_PER_HOUR", "50"))
        for _ in range(max_views):
            self.behavior.watch_video() # Uncommented
            # 65% de probabilidad de like
            if random.random() < 0.65: # This line itself is fine
                self.behavior.like_video() # Uncommented
            self.behavior.random_scroll() # Uncommented
            time.sleep(random.uniform(8, 15))
