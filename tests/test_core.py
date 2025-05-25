# Tests para los módulos principales en core/ del framework TTBT1
# Ejecutar con: pytest tests/test_core.py

import os
import json
import tempfile
from core.account_manager import AccountManager
from core.bot import Bot
from core.bot_engine import BotEngine
from core.config_loader import load_config

def test_account_manager_load_accounts():
    data = {"usera": {"pass": "123"}, "userb": {"pass": "456"}}
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.seek(0)
        manager = AccountManager(f.name)
        assert manager.accounts == data
    os.remove(f.name)

def test_account_manager_file_not_found():
    manager = AccountManager("noexiste.json")
    assert manager.accounts == {}

def test_bot_assign_proxy_and_fingerprint():
    bot = Bot("userx", {"pass": "xyz"})
    bot.assign_proxy("proxyX")
    bot.assign_fingerprint("fpY")
    assert bot.proxy == "proxyX"
    assert bot.fingerprint == "fpY"

def test_bot_engine_initialization(monkeypatch):
    accounts = {"bot1": {"pass": "a"}, "bot2": {"pass": "b"}}
    # Gestores dummy que siempre devuelven el mismo valor
    class DummyProxyManager:
        def get_random_active_proxy(self): return "proxyZ"
    class DummyFingerprintManager:
        def get_fingerprint(self): return "fpW"
    engine = BotEngine(accounts, DummyProxyManager(), DummyFingerprintManager())
    engine.initialize_bots()
    assert len(engine.bots) == 2
    for bot in engine.bots:
        assert bot.proxy == "proxyZ"
        assert bot.fingerprint == "fpW"

def test_config_loader_json_and_yaml():
    data = {"hello": "world"}
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as jf:
        json.dump(data, jf)
        jf.seek(0)
        loaded = load_config(jf.name)
        assert loaded == data
    os.remove(jf.name)
    try:
        import yaml
        with tempfile.NamedTemporaryFile("w+", suffix=".yml", delete=False) as yf:
            yaml.safe_dump(data, yf)
            yf.seek(0)
            loaded = load_config(yf.name)
            assert loaded == data
        os.remove(yf.name)
    except ImportError:
        pass