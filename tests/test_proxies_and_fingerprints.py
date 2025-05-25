# Tests para los gestores de proxies y fingerprints del framework TTBT1
# Usar pytest para ejecutar estos tests: `pytest tests/test_proxies_and_fingerprints.py`

import pytest
from proxies.proxy_manager import ProxyManager
from fingerprints.fingerprint_manager import FingerprintManager

def test_proxy_manager_returns_random_proxy():
    proxies = ["proxy1", "proxy2", "proxy3"]
    manager = ProxyManager(proxies)
    random_proxy = manager.get_random_active_proxy()
    assert random_proxy in proxies

def test_proxy_manager_deactivate_proxy():
    proxies = ["proxyA", "proxyB"]
    manager = ProxyManager(proxies)
    manager.deactivate_proxy("proxyA")
    assert "proxyA" not in manager.active_proxies
    assert "proxyB" in manager.active_proxies

def test_fingerprint_manager_returns_random_fingerprint():
    fingerprints = ["fp1", "fp2", "fp3"]
    manager = FingerprintManager(fingerprints)
    fp = manager.get_fingerprint()
    assert fp in fingerprints

def test_proxy_manager_handles_empty_list():
    manager = ProxyManager([])
    assert manager.get_random_active_proxy() is None

def test_fingerprint_manager_handles_empty_list():
    manager = FingerprintManager([])
    assert manager.get_fingerprint() is None