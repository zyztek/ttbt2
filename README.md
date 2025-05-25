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

## Licencia

MIT. Ver [LICENSE](LICENSE).