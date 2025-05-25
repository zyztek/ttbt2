# Tests para el módulo DataLoader en data/data_loader.py del framework TTBT1
# Ejecutar con: pytest tests/test_data_loader.py

import os
import json
import tempfile

from data.data_loader import DataLoader

def test_data_loader_json():
    data = {"clave": "valor", "lista": [1, 2, 3]}
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.seek(0)
        loader = DataLoader(f.name)
        assert loader.data == data
    os.remove(f.name)

def test_data_loader_yaml():
    try:
        import yaml
    except ImportError:
        return  # PyYAML no instalado, omitir test
    data = {"uno": 1, "dos": [2, 2, 2]}
    with tempfile.NamedTemporaryFile("w+", suffix=".yml", delete=False) as f:
        yaml.safe_dump(data, f)
        f.seek(0)
        loader = DataLoader(f.name)
        assert loader.data == data
    os.remove(f.name)

def test_data_loader_file_not_found():
    loader = DataLoader("noexiste.json")
    assert loader.data == {}

def test_data_loader_invalid_json():
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        f.write("{invalido: ,}".encode("utf-8"))
        f.seek(0)
        loader = DataLoader(f.name)
        assert loader.data == {}
    os.remove(f.name)

def test_data_loader_invalid_yaml():
    try:
        import yaml
    except ImportError:
        return
    with tempfile.NamedTemporaryFile("w+", suffix=".yml", delete=False) as f:
        f.write(b":- { esto no es yaml")
        f.seek(0)
        loader = DataLoader(f.name)
        assert loader.data == {}
    os.remove(f.name)