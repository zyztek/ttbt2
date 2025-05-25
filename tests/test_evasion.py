# Tests para los módulos de evasión (core/evasion.py y core/evasion_system.py) del framework TTBT1
# Ejecutar con: pytest tests/test_evasion.py

from core.evasion import Evasion
from core.evasion_system import EvasionSystem

class DummyBot:
    def __init__(self):
        self.proxy = None
        self.fingerprint = None

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
    system = EvasionSystem(fps, proxies)
    bot = DummyBot()
    system.apply_evasion(bot)
    assert bot.fingerprint == "fpQ"
    assert bot.proxy == "proxyQ"

def test_evasion_system_empty_lists():
    system = EvasionSystem([], [])
    bot = DummyBot()
    system.apply_evasion(bot)
    assert bot.fingerprint is None
    assert bot.proxy is None