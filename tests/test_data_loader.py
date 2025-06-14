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
    with tempfile.NamedTemporaryFile("wb+", suffix=".json", delete=False) as f: # Changed "w+" to "wb+"
        f.write("{invalido: ,}".encode("utf-8"))
        f.seek(0)
        loader = DataLoader(f.name)
        assert loader.data == {}
    os.remove(f.name)

def test_data_loader_yaml_file_not_found():
    # This test assumes DataLoader's __init__ calls load_data,
    # and load_data uses os.path.exists before trying to open,
    # or handles FileNotFoundError directly in its try-except.
    # The DataLoader's load_data method already handles FileNotFoundError.

    loader = DataLoader("non_existent.yaml") # Path that doesn't exist
    assert loader.data == {}

def test_data_loader_unknown_extension():
    # This test also relies on DataLoader's load_data returning {} for unknown extensions.
    # Create a dummy file to ensure it's not a FileNotFoundError, but an extension issue.
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write("some data")
        filepath = tmp_file.name

    loader = DataLoader(filepath)
    assert loader.data == {}

    os.remove(filepath) # Cleanup

def test_data_loader_invalid_yaml():
    try:
        import yaml
    except ImportError:
        return
    with tempfile.NamedTemporaryFile("wb+", suffix=".yml", delete=False) as f: # Changed "w+" to "wb+"
        # Using a truly invalid YAML structure
        f.write("key: [unclosed_bracket".encode("utf-8"))
        f.seek(0)
        loader = DataLoader(f.name)
        assert loader.data == {}
    os.remove(f.name)