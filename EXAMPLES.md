# Ejemplos de uso y configuración — TTBT1

Aquí encontrarás ejemplos para facilitar el despliegue y pruebas del framework.

---

## Ejemplo: `accounts.json`

```json
{
  "alice": { "pass": "alicepass" },
  "bob":   { "pass": "bobpass" }
}
```

---

## Ejemplo: `proxies/proxies.json`

```json
{
  "proxies": [
    "http://192.168.1.10:8080",
    "http://192.168.1.11:8080"
  ]
}
```

---

## Ejemplo: `fingerprints/fingerprints.json`

```json
{
  "fingerprints": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ..."
  ]
}
```

---

## Ejemplo: archivo YAML de datos (`data/dataset.yml`)

```yaml
usuarios:
  - nombre: carlos
    nivel: admin
  - nombre: laura
    nivel: user
parametros:
  modo: "prueba"
  max_intentos: 4
```

---

## Ejecución rápida

1. Coloca los archivos de configuración en los directorios adecuados.
2. Ejecuta:
    ```bash
    python main.py
    ```

---

## Ejecución de tests

```bash
pytest tests/
```

---

## Notas

- Puedes agregar o quitar cuentas, proxies y fingerprints simplemente editando los archivos respectivos.
- El sistema de evasión y la gestión de bots funcionarán sobre los datos que proporciones.