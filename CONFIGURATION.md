# Guía de Configuración de TTBT1

Esta guía cubre cómo configurar TTBT1 para operar con proxies, fingerprints y cuentas.

## 1. Configuración de cuentas

Archivo: `accounts.json`
```json
{
  "usuario1": {"pass": "contraseña1"},
  "usuario2": {"pass": "contraseña2"}
}
```

## 2. Configuración de proxies

Archivo: `proxies/proxies.json`
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

## 4. Carga de datos adicionales

Puedes añadir datasets personalizados en `data/`.

## 5. Ejemplo de estructura completa

```
accounts.json
proxies/
  proxies.json
fingerprints/
  fingerprints.json
data/
  dataset.yml
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