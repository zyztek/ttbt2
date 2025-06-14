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
    Puedes pasar argumentos para configurar el comportamiento, por ejemplo:
    ```bash
    python main.py --mode safe --max-views 100
    ```
    Consulta `python main.py --help` para más detalles.
    También puedes configurar variables de entorno como `LOG_PATH` y `FLASK_HOST` (ver `CONFIGURATION.md`).

---

## Ejemplo de Uso Programático del Bot (Python)

A continuación, un ejemplo básico de cómo instanciar y ejecutar `TikTokBot` directamente en un script de Python:

```python
from core.bot import TikTokBot

print("Iniciando el bot de ejemplo...")

# TikTokBot usa un AccountManager interno.
# Para este ejemplo, asegúrate que 'accounts.json' existe y es accesible,
# o que AccountManager en TikTokBot está configurado para obtener cuentas.
bot = TikTokBot()

# Opcionalmente, puedes asignar proxy/fingerprint si no usas BotEngine:
# bot.assign_proxy("http://tu_proxy:puerto")
# bot.assign_fingerprint("tu_fingerprint_string")

if bot.driver:
    print("Driver inicializado. Ejecutando sesión del bot...")
    try:
        bot.run_session()
    except Exception as e:
        print(f"Error durante la sesión del bot: {e}")
    finally:
        print("Cerrando driver del bot...")
        bot.driver.quit()
        print("Driver cerrado.")
else:
    print("Fallo al inicializar el driver del bot.")

print("Ejemplo de bot finalizado.")
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