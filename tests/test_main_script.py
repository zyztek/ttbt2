# Tests de integración básicos para main.py del framework TTBT1
# Ejecutar con: pytest tests/test_main_script.py

import os
import json
import tempfile
import shutil

import pytest

def create_temp_file(directory, filename, content):
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f)
    return path

@pytest.fixture
def temp_env():
    # Crea estructura temporal de archivos y carpetas
    base_dir = tempfile.mkdtemp()
    proxies_dir = os.path.join(base_dir, "proxies")
    fingerprints_dir = os.path.join(base_dir, "fingerprints")
    os.makedirs(proxies_dir)
    os.makedirs(fingerprints_dir)
    yield base_dir, proxies_dir, fingerprints_dir
    shutil.rmtree(base_dir)

def test_main_runs_without_errors(monkeypatch, temp_env):
    base_dir, proxies_dir, fingerprints_dir = temp_env

    # Crea archivos de configuración mínimos
    accounts_path = create_temp_file(base_dir, "accounts.json", {"testuser": {"pass": "tpass"}})
    proxies_path = create_temp_file(proxies_dir, "proxies.json", {"proxies": ["proxyA"]})
    fingerprints_path = create_temp_file(fingerprints_dir, "fingerprints.json", {"fingerprints": ["fpA"]})

    # Monkeypatch paths usados en main.py
    monkeypatch.chdir(base_dir)
    # Importar aquí para asegurar que se usa el entorno temporal
    import sys
    sys.path.insert(0, os.getcwd())
    from main import main as main_entrypoint if hasattr(__import__('main'), 'main') else None

    # Ejecuta el script principal (no debe lanzar error)
    try:
        __import__('main')
    except Exception as e:
        pytest.fail(f"main.py lanzó una excepción: {e}")

def test_main_handles_missing_files(monkeypatch, temp_env):
    # No se crean archivos de configuración
    base_dir, _, _ = temp_env
    monkeypatch.chdir(base_dir)
    import sys
    sys.path.insert(0, os.getcwd())
    try:
        __import__('main')
    except Exception as e:
        pytest.fail(f"main.py lanzó una excepción con archivos faltantes: {e}")