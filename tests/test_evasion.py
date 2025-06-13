# Tests para los módulos de evasión (core/evasion.py y core/evasion_system.py) del framework TTBT1
# Ejecutar con: pytest tests/test_evasion.py

from core.evasion import Evasion
# No longer need EvasionSystem for these tests
# from core.evasion_system import EvasionSystem

class DummyBot:
    def __init__(self):
        self.proxy = None
        self.fingerprint = None

    def assign_proxy(self, proxy_value):
        self.proxy = proxy_value

    def assign_fingerprint(self, fingerprint_value):
        self.fingerprint = fingerprint_value

def test_evasion_rotate_fingerprint_and_proxy():
    fps = ["fpA", "fpB"]
    proxies = ["proxy1", "proxy2"]
    evasion = Evasion(fps, proxies)
    for _ in range(5):
        assert evasion.rotate_fingerprint() in fps
        assert evasion.rotate_proxy() in proxies

def test_evasion_empty_lists():
    evasion = Evasion([], [])
    assert evasion.rotate_fingerprint() is None
    assert evasion.rotate_proxy() is None

def test_evasion_system_apply_evasion_sets_bot_fields():
    fps = ["fpQ"]
    proxies = ["proxyQ"]
    evasion_logic = Evasion(fps, proxies) # Changed EvasionSystem to Evasion
    bot = DummyBot()
    evasion_logic.apply_evasion(bot) # Changed system to evasion_logic
    assert bot.fingerprint == "fpQ"
    assert bot.proxy == "proxyQ"

def test_evasion_system_empty_lists():
    evasion_logic = Evasion([], []) # Changed EvasionSystem to Evasion
    bot = DummyBot()
    evasion_logic.apply_evasion(bot) # Changed system to evasion_logic
    assert bot.fingerprint is None
    assert bot.proxy is None