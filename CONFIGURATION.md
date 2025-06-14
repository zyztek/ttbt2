# Guía de Configuración de TTBT1

Esta guía cubre cómo configurar TTBT1 para operar con proxies, fingerprints y cuentas.

## Variables de Entorno

Estas variables de entorno pueden ser utilizadas para configurar aspectos del framework:

-   **`LOG_PATH`**: Define la ruta completa del archivo de log. Ejemplo: `logs/mi_bot.log`. Por defecto: `logs/ttbt1.log` (según `core/logger.py`).
-   **`FLASK_HOST`**: Define el host en el que las aplicaciones Flask (API, Dashboard) escucharán. Ejemplo: `0.0.0.0` para todas las interfaces, `127.0.0.1` para localhost. Por defecto: `127.0.0.1`.
-   **`PORT`**: Define el puerto para la aplicación del Dashboard (`dashboard/app.py`). Ejemplo: `8080`. Por defecto: `5000`.
-   **`MAX_VIEWS_PER_HOUR`**: Controla el número máximo de videos que el bot intentará procesar por sesión (utilizado por `TikTokBot`). Se establece a través de los argumentos de `main.py` (`--max-views`), que por defecto es `5000`.

## 1. Configuración de cuentas

Archivo: `accounts.json`

El archivo `accounts.json` debe ser un diccionario donde cada clave es un identificador de usuario (ej. email) y el valor es un diccionario con los detalles de la cuenta, como mínimo `{"pass": "contraseña"}`.
```json
{
  "usuario1@example.com": {"pass": "contraseña1"},
  "usuario2@example.com": {"pass": "contraseña2"}
}
```
Por defecto, `core.account_manager.AccountManager` puede cargar un archivo con este nombre si se le pasa la ruta, o si se modifica para buscar `accounts.json` por defecto en la raíz del proyecto.

## 2. Configuración de proxies

Archivo: `proxies/proxies.json`

Por defecto, se espera que este archivo esté en `proxies/proxies.json`.
```json
{
  "proxies": [
    "proxy1:port",
    "proxy2:port"
  ]
}
```

## 3. Configuración de fingerprints

Archivo: `fingerprints/fingerprints.json`
```json
{
  "fingerprints": [
    "fp1",
    "fp2"
  ]
}
```
Por defecto, se espera que este archivo esté en `fingerprints/fingerprints.json`.

## 4. Carga de datos adicionales

Puedes añadir archivos de datos personalizados en el directorio `data/`. El `DataLoader` (`data/data_loader.py`) puede cargar archivos JSON o YAML. La estructura interna de estos archivos depende de cómo planeas utilizar los datos en tus bots.

## 5. Ejemplo de estructura completa

```
accounts.json
proxies/
  proxies.json
fingerprints/
  fingerprints.json
data/
  mi_dataset.yml
  # o data/mi_config.json
```

## 6. Herramientas recomendadas

- Para gestionar proxies a escala: [BrightData](https://brightdata.com)
- Para fingerprints reales: [FingerprintJS](https://fingerprint.com)
- Para monitoreo y dashboards: [Grafana](https://grafana.com)

## 7. Configuración visual interactiva

Consulta la herramienta externa para diagramas y flujos:
[Imagine Explainers](https://imagineexplainers.com/) ([enlace directo](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj6_dCx8b2NAxW9ODQIHR2eGqIQFnoECAsQAQ&url=https%3A%2F%2Fimagineexplainers.com%2F&usg=AOvVaw0QPBZTs5IXMQc-fcnZ82Hr&opi=89978449))

Utiliza Imagine Explainers para crear diagramas de flujo personalizados sobre tu configuración y arquitectura TTBT1.

---