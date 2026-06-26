# Prototipos HTML — archivo externo

Los diseños HTML/CSS/JS estáticos de Fase 1b **ya no viven en este repositorio**. Fueron migrados a Django y la copia completa está **archivada fuera del repo** (respaldada por el equipo).

## Fuente activa (desarrollo y QA)

| Zona | App Django | URL local típica |
|------|------------|------------------|
| Landing pública | `apps.public_site` | http://127.0.0.1:8000/ |
| Acceso / 2FA | `apps.security` | http://127.0.0.1:8000/ingresar/ |
| Zona privada `/app/` | `apps.dashboard`, `apps.catalog`, … | http://127.0.0.1:8000/app/ |

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
```

## Dónde está la UI hoy

| Área | Templates |
|------|-----------|
| Layout app | `apps/core/templates/app_base.html`, `partials/app_sidebar.html` |
| Estáticos compartidos | `apps/core/static/`, `apps/dashboard/static/dashboard/` |
| Módulos | `apps/*/templates/` (ver [`docs/ui-ux.md`](../docs/ui-ux.md)) |

## Convención de nombres (sigue vigente)

Patrón `{app}_{accion}.html` en templates Django — ver [`docs/ui-ux.md`](../docs/ui-ux.md#nombres-de-archivos-html-zona-app).

## Histórico

- **Jun 2026:** retirados del repo `prototype_app/`, `security/`, `prototype_home/`, `assets/` y legacy (`home_page/`, redirects, etc.).
- Documentación actualizada para apuntar solo a Django.
