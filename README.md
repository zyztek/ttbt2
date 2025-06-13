# TTBT1 Framework

TTBT1 es un framework modular y extensible para bots, enfocado en evasión, rotación de proxies/fingerprints, CI, logging profesional, plugins, dashboard web y Docker.

---

<div align="center">
  <img src="docs/img/ttbt1_architecture.png" alt="TTBT1 Arquitectura" width="600">
</div>

---

## Tabla de contenidos

- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Ejemplo de uso básico](#ejemplo-de-uso-básico)
- [Ejemplo avanzado de bot](#ejemplo-avanzado-de-bot)
- [Plugins](#plugins)
- [Dashboard web](#dashboard-web)
- [Logging avanzado](#logging-avanzado)
- [Integración CI](#integración-ci)
- [Dockerización](#dockerización)
- [Diagramas de arquitectura](#diagramas-de-arquitectura)
- [Herramientas y servicios recomendados](#herramientas-y-servicios-recomendados)
- [Licencia](#licencia)

---

## Instalación

```bash
git clone https://github.com/tuusuario/ttbt1.git
cd ttbt1
pip install -r requirements.txt
```

## Dockerización

```bash
docker build -t ttbt1 .
docker run --rm -it -v $(pwd)/accounts.json:/app/accounts.json ttbt1
```

## Estructura del Proyecto

```
core/               # Núcleo del framework
proxies/            # Gestión de proxies
fingerprints/       # Gestión de fingerprints
data/               # Carga de datos adicionales
bots/               # Bots personalizados y avanzados
plugins/            # Plugins externos
dashboard/          # Dashboard web Flask
logs/               # Archivos de logs
tests/              # Pruebas unitarias e integración
docs/               # Diagramas, imágenes y documentación extendida
.github/workflows/  # Integración continua (CI)
```

## Configuración

Consulta la [Guía de configuración](CONFIGURATION.md).

---

## Ejemplo de uso básico

```python
from bots.sample_bot import SampleBot

bot = SampleBot("usuario1", {"pass": "secreta"})
bot.assign_proxy("proxyX")
bot.assign_fingerprint("fpY")
bot.run()
```

---

## Ejemplo avanzado de bot

```python
from bots.advanced_bot import AdvancedBot

bot = AdvancedBot("usuario1", {"pass": "supersecreta"})
bot.assign_proxy("proxyZ")
bot.assign_fingerprint("fpMega")
bot.run()
```

---

## Plugins

El sistema de plugins permite extender el comportamiento de los bots sin tocar el core.

Ejemplo de plugin:

```python
# plugins/logger_plugin.py
def after_login(bot):
    bot.logger.info(f"[PLUGIN] {bot.username} pasó after_login")
```

Carga en el bot:

```python
self.plugin_manager.load_plugin("plugins/logger_plugin.py")
```

---

## Dashboard web

Levanta un dashboard con Flask para monitorear bots en tiempo real.

```bash
cd dashboard
python app.py
```

Accede a [http://localhost:5000](http://localhost:5000)

---

## Logging avanzado

Integración con [loguru](https://github.com/Delgan/loguru) para logs rotativos y estructurados.

```python
from core.logger import get_logger
logger = get_logger("mi-bot")
logger.info("¡Bot iniciado!")
```

---

## Integración CI

Incluye [GitHub Actions](.github/workflows/ci.yml) para tests automáticos con pytest.

---

## Diagramas de arquitectura

### General

<div align="center">
  <img src="docs/img/ttbt1_architecture.png" width="600" alt="Arquitectura general">
</div>

### Flujo del bot

<div align="center">
  <img src="docs/img/bot_flow.png" width="600" alt="Flujo del bot">
</div>

---

## Herramientas y servicios recomendados

- **Logging avanzado**: [Loguru](https://github.com/Delgan/loguru), [Sentry](https://sentry.io)
- **Dashboard**: [Flask](https://flask.palletsprojects.com/)
- **Proxies premium**: [BrightData](https://brightdata.com), [Oxylabs](https://oxylabs.io)
- **Fingerprints**: [FingerprintJS](https://fingerprint.com)
- **Documentación**: [MkDocs](https://www.mkdocs.org/), [Read the Docs](https://readthedocs.org/)
- **CI/CD**: [GitHub Actions](https://docs.github.com/en/actions)
- **Monitoreo**: [Grafana](https://grafana.com)
- **Diagramas**: [Imagine Explainers](https://imagineexplainers.com/)

---

## Estado del Proyecto y Registro de Depuración

Este proyecto fue sometido a un proceso de inspección y depuración intensivo. A continuación, se presenta un resumen del proceso y el estado actual.

### Resumen del Proceso de Depuración

*   **Solicitud Inicial**: Inspección general del código, identificación de problemas y depuración.
*   **Hallazgos Clave**:
    *   Dependencias no fijadas (unpinned) en `requirements.txt` (ej. `flask`, `pyyaml`, `loguru`, `pytest`), lo que podría ocultar vulnerabilidades o causar problemas de compatibilidad.
    *   Numerosas advertencias de Pylint: Puntuación inicial baja (3.53/10), errores críticos de importación (ej. `selenium`, `loguru`, `flask`, `utilities.database`, `core.evasion`), falta de docstrings y problemas de estilo.
    *   Error de sintaxis en `tests/test_main_script.py` debido a una línea de importación condicional compleja.
    *   Al añadir `pytest-cov` e intentar ejecutar la suite de tests completa, se encontraron 9 fallos iniciales. Estos se debían principalmente a constructores de clases que no coincidían con las llamadas en los tests y a errores lógicos tanto en los tests como en el código fuente.
    *   Ausencia del fichero `core/__init__.py`, lo que impedía que Pylint (y potencialmente Python en algunos contextos) reconociera el directorio `core` como un paquete, causando errores de importación para módulos dentro de `core`.
*   **Acciones Tomadas**:
    *   Se fijaron las versiones de las dependencias en `requirements.txt` (ej. `pytest==8.4.0`, `pyyaml==6.0.2`, `loguru==0.7.3`, `flask==3.1.1`) y se verificó la seguridad de estas versiones con la herramienta `safety` (resultado: 0 vulnerabilidades).
    *   Se añadieron `selenium` y `pytest-cov` a `requirements.txt` para facilitar las pruebas de navegador y la medición de cobertura de código, respectivamente.
    *   Se corrigieron los errores críticos de importación mediante la corrección de rutas de importación, la adición del fichero `core/__init__.py`, y el cambio de nombre de la clase `CoreAccountManager` a `AccountManager` para que coincidiera con las expectativas de importación.
    *   No se encontró la definición de la clase `HumanBehaviorSimulator`. El código relacionado en `core/bot.py` que utilizaba esta clase fue comentado temporalmente para permitir el progreso en otras áreas. Este sigue siendo un problema pendiente.
    *   Se corrigió el error de sintaxis en `tests/test_main_script.py` eliminando la línea problemática.
    *   Se abordaron sistemáticamente los 9 fallos de tests. Esto implicó la refactorización de componentes del núcleo (`AccountManager`, `TikTokBot`, `BotEngine`, `Evasion`, `ConfigLoader`) y de los scripts de prueba para alinear las interfaces (constructores, métodos) y la lógica subyacente. Por ejemplo, se ajustaron los constructores para que aceptaran los argumentos correctos, se implementaron métodos faltantes en clases dummy y reales, y se corrigió la lógica de carga de ficheros YAML y el manejo de errores en los tests.
*   **Estado Actual**:
    *   Los 22 tests existentes en la suite ahora pasan satisfactoriamente.
    *   La cobertura de código del proyecto es del 70% según la última ejecución de `pytest-cov`.
*   **Problemas Pendientes / Próximos Pasos**:
    *   Resolver el problema de la clase `HumanBehaviorSimulator` faltante en `core/bot.py` (investigar su origen o implementar una versión funcional si es necesaria).
    *   Mejorar la cobertura de tests, especialmente para módulos con baja o nula cobertura como `core/logger.py`, `core/evasion_system.py` (o eliminar este último si ya no es relevante tras las refactorizaciones), `main.py`, y `todo_app.py`.
    *   Atender las advertencias restantes de Pylint y Bandit para mejorar la calidad y seguridad del código.

---

## Licencia

MIT. Ver [LICENSE](LICENSE).