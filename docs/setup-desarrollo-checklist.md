# Checklist — Inicio de desarrollo local (Windows)

**Última actualización:** 2026-06-19  
**Entorno:** Windows · PostgreSQL **nativo** (sin Docker) · raíz del proyecto: `C:\IACursor\BakeBudge\BAKEBUDGE`

Seguimiento paso a paso para pasar de **diseño/prototipo** a **proyecto Django ejecutable**.

**Referencia técnica:** [`setup.md`](setup.md) · [`arquitectura.md`](arquitectura.md) · [`roadmap.md`](roadmap.md)

---

## Resumen de avance

| Fase | Descripción | Estado |
|------|-------------|--------|
| **0** | Verificar herramientas base | **Completado** |
| **1** | Base de datos PostgreSQL local | **Completado** |
| **2** | Entorno virtual Python | **Completado** |
| **3** | Dependencias Python (Django + seguridad) | **Completado** |
| **4** | Scaffold Django (`manage.py`, `config/`) | **Completado** |
| **5** | Variables de entorno (`.env`) | **Completado** |
| **6** | Configuración settings (`base` / `local`) | **Completado** |
| **7** | Crear apps bajo `apps/` | **Completado** |
| **8** | Migraciones y servidor de desarrollo | **Completado** |
| **9** | Prototipos HTML (opcional, paralelo) | Disponible cuando se necesite |

---

## Fase 0 — Verificar herramientas base

**Estado: Completado**

Comandos de verificación:

```powershell
python --version
# Esperado: Python 3.12+

psql --version
# Esperado: PostgreSQL 16 (o compatible)

git --version
```

Si `psql` no está en PATH:

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" --version
```

| Herramienta | Requerido | Estado |
|-------------|-----------|--------|
| Git | Sí | Completado |
| Python 3.12+ | Sí | Completado |
| PostgreSQL 16 | Sí (nativo; **no Docker**) | Completado |

---

## Fase 1 — Base de datos PostgreSQL local

**Estado: Completado**

> **Nota:** Docker Postgres **no aplica** en este entorno. La BD corre en la instalación local de PostgreSQL.

### Creación (referencia — ya ejecutado)

```powershell
psql -U postgres
```

```sql
CREATE USER bakebudge WITH PASSWORD 'bakebudge';
CREATE DATABASE bakebudge OWNER bakebudge ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE bakebudge TO bakebudge;
\q
```

### Comprobar conexión

```powershell
psql -U bakebudge -d bakebudge -h localhost -p 5432
# Password: bakebudge
\q
```

| Ítem | Valor acordado | Estado |
|------|----------------|--------|
| Base de datos | `bakebudge` | Completado |
| Usuario | `bakebudge` | Completado |
| Host | `localhost` | Completado |
| Puerto | `5432` (ajustar en `.env` si difiere) | Completado |

**URL de conexión para Django:**

```text
postgres://bakebudge:bakebudge@localhost:5432/bakebudge
```

---

## Fase 2 — Entorno virtual Python

**Estado: Completado**

Directorio de trabajo:

```powershell
cd C:\IACursor\BakeBudge\BAKEBUDGE
```

Comandos (referencia — ya ejecutados):

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

| Ítem | Estado |
|------|--------|
| Carpeta `.venv/` en raíz `BAKEBUDGE/` | Completado |
| `pip` actualizado | Completado |
| Activación del venv documentada | Completado |

**Recordatorio:** activar el venv en cada sesión nueva:

```powershell
cd C:\IACursor\BakeBudge\BAKEBUDGE
.\.venv\Scripts\Activate.ps1
```

---

## Fase 3 — Dependencias Python

**Estado: Completado**

### Núcleo Django (scaffold + BD)

```powershell
pip install "Django>=5.0" psycopg2-binary django-environ Pillow
```

### Seguridad — 2FA / TOTP (Fase 1a)

```powershell
pip install "pyotp>=2.9,<3" "qrcode>=7.4,<9"
```

### Paquetes instalados

| Paquete | Rol | Estado |
|---------|-----|--------|
| Django 5.x | Framework web | Completado |
| psycopg2-binary | Driver PostgreSQL | Completado |
| django-environ | Variables `.env` | Completado |
| Pillow | Imágenes | Completado |
| pyotp | TOTP (2FA) | Completado |
| qrcode | QR autenticador | Completado |

### Pendiente en esta fase

| Ítem | Cuándo | Estado |
|------|--------|--------|
| `requirements.txt` en raíz | Tras scaffold (Fase 4) | **Pendiente** |
| `pip freeze > requirements.txt` | Tras fijar versiones | **Pendiente** |
| `resend` (correo producción) | Railway + `EMAIL_DELIVERY=resend` | **Completado** (local sigue consola) |

**Contenido previsto de `requirements.txt`:**

```text
Django>=5.0
psycopg2-binary
django-environ
Pillow
pyotp>=2.9,<3
qrcode>=7.4,<9
# resend>=2.0,<3   # producción Railway — ver deploy-railway-plan.md
```

---

## Fase 4 — Scaffold Django

**Estado: Completado**

Desde la raíz (venv activado):

```powershell
cd C:\IACursor\BakeBudge\BAKEBUDGE

django-admin startproject config .
```

Genera:

```text
BAKEBUDGE/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py      # → refactorizar a settings/base.py, local.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── docs/
├── prototype/
└── apps/                # ya existe parcialmente
```

Congelar dependencias:

```powershell
pip freeze > requirements.txt
```

| Ítem | Estado |
|------|--------|
| `manage.py` | Completado |
| `config/` (proyecto Django) | Completado |
| `requirements.txt` | Completado |
| `.gitignore` (`.env`, `.venv/`, `__pycache__/`) | Completado |

---

## Fase 5 — Variables de entorno

**Estado: Completado**

Archivos creados en la raíz `BAKEBUDGE/`:

| Archivo | Rol |
|---------|-----|
| `.env` | Valores locales (no se commitea) |
| `.env.example` | Plantilla para el repositorio |

Recrear `.env` en otra máquina:

```powershell
Copy-Item .env.example .env
# Editar SECRET_KEY y DATABASE_URL si aplica
```

| Variable | Propósito | Estado |
|----------|-----------|--------|
| `DEBUG` | Modo desarrollo | Completado |
| `SECRET_KEY` | Clave Django | Completado |
| `DATABASE_URL` | Conexión PostgreSQL local | Completado |
| `ALLOWED_HOSTS` | Hosts permitidos | Completado |
| `EMAIL_DELIVERY=console` | Códigos 2FA en terminal (dev) | Completado |
| `RESEND_API_KEY` | Vacío en local | Completado |
| `DEFAULT_FROM_EMAIL` | Remitente (producción) | Completado |

Ajustar `DATABASE_URL` si el puerto o credenciales de Postgres difieren de la Fase 1.

---

## Fase 6 — Configuración Django (settings)

**Estado: Completado**

Estructura en `config/settings/`:

```text
config/settings/
├── __init__.py
├── base.py        # compartido: apps, DB, static, templates, auth URLs
├── local.py       # desarrollo — correo consola
└── production.py  # despliegue (base; completar al deploy)
```

| Tarea | Estado |
|-------|--------|
| Partir settings en `base.py` / `local.py` | Completado |
| `django-environ` + `DATABASE_URL` | Completado |
| `DJANGO_SETTINGS_MODULE=config.settings.local` | Completado |
| `LOCAL_APPS` preparado para `apps.*` (Fase 7) | Completado |
| User estándar + `UserProfile` en Fase 7 | Documentado |
| `LOGIN_URL = "/ingresar/"`, `LOGIN_REDIRECT_URL = "/app/"` | Completado |

Comprobación ejecutada:

```powershell
python manage.py check
# System check identified no issues (0 silenced).

python manage.py migrate --plan
# Plan de migraciones contra PostgreSQL OK
```

---

## Fase 7 — Apps bajo `apps/`

**Estado: Completado**

> **Alcance Fase 7:** solo esqueleto Django (`startapp`, `AppConfig`, registro en settings).  
> **Sin** modelos de negocio, vistas, URLs, servicios nuevos ni templates de app.

Convención: [`arquitectura.md`](arquitectura.md#estructura-modular-django).

### Estructura creada

```text
apps/
├── core/           # utilidades compartidas, static/tokens (futuro)
├── accounts/       # UserProfile (futuro)
├── security/       # login, 2FA (futuro)
├── public_site/    # landing (futuro)
├── dashboard/      # /app/ home (futuro)
├── catalog/        # productos, categorías (futuro)
├── recipes/        # recetas (+ services/cost_calculator.py preexistente)
├── production/     # órdenes (futuro)
└── analytics/      # existente — NO registrada aún (modelos dependen de otras apps)
```

### Comandos ejecutados

```powershell
python manage.py startapp core apps/core
python manage.py startapp accounts apps/accounts
python manage.py startapp security apps/security
python manage.py startapp public_site apps/public_site
python manage.py startapp dashboard apps/dashboard
python manage.py startapp catalog apps/catalog
python manage.py startapp recipes apps/recipes
python manage.py startapp production apps/production
```

Cada `AppConfig`: `name = "apps.<nombre>"`.

### Registro en `LOCAL_APPS` (`config/settings/base.py`)

| App | Registrada | Notas |
|-----|------------|-------|
| `apps.core` | Sí | `static/`, `templates/` vacíos |
| `apps.accounts` | Sí | |
| `apps.security` | Sí | |
| `apps.public_site` | Sí | |
| `apps.dashboard` | Sí | |
| `apps.catalog` | Sí | |
| `apps.recipes` | Sí | CRUD + formulación + costos |
| `apps.production` | Sí | Órdenes de producción |
| `apps.analytics` | Sí | Snapshots + `/app/estadisticas/` |
| `apps.noticias` | Sí | Feed + CRUD Master |
| `apps.administration` | Sí | Master: usuarios, facturación, monedas, etc. |
| `apps.billing` | Sí | `PaymentControl` (gate en evolución) |
| `apps.ayuda` | Sí | `/app/ayuda/` — [`ayuda-reglas.md`](ayuda-reglas.md) |

Comprobación:

```powershell
python manage.py check
# System check identified no issues (0 silenced).
```

### Pendiente (post v1 operativo)

- Gate `can_access_app` completo en runtime (billing)
- Extensiones: `costo_real`, inventario, `ResumenMensual`, Chart.js

---

## Fase 8 — Migraciones y servidor

**Estado: Completado**

Comandos ejecutados:

```powershell
cd C:\IACursor\BakeBudge\BAKEBUDGE
.\.venv\Scripts\Activate.ps1

python manage.py migrate
python manage.py runserver
```

URL: `http://127.0.0.1:8000/` (admin Django en `/admin/`).

Comandos útiles (opcionales):

```powershell
python manage.py createsuperuser
python manage.py showmigrations
```

| Ítem | Estado |
|------|--------|
| Migraciones iniciales (`auth`, `contenttypes`, `sessions`, `admin`, …) | Completado |
| Servidor `runserver` respondiendo | Completado |
| Superusuario de prueba | Opcional — cuando se necesite `/admin/` |

> Solo migraciones de apps Django built-in; aún **sin** modelos de negocio en `apps.*`.

---

## Fase 9 — Vista previa local (Django)

**Estado:** disponible en cualquier momento con `runserver`.

```powershell
cd C:\IACursor\BakeBudge\BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
```

| URL demo | Ruta |
|----------|------|
| Dashboard | http://127.0.0.1:8000/app/ |
| Landing | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/ingresar/ |

La UI vive en templates Django (`apps/*/templates/`). Ver [`fase-1b-landing.md`](fase-1b-landing.md).

---

## Orden de ejecución restante (checklist rápido)

```text
[x] 0.  Verificar Python, PostgreSQL, Git
[x] 1.  Crear BD bakebudge + usuario bakebudge
[x] 2.  venv .venv + pip upgrade
[x] 3.  pip install Django, psycopg2, environ, Pillow, pyotp, qrcode
[x] 4.  django-admin startproject config .
[x] 5.  Crear .env y .env.example
[x] 6.  Configurar settings (base/local, DATABASE_URL, INSTALLED_APPS)
[x] 7.  startapp apps/* + registrar en LOCAL_APPS
[x] 8.  python manage.py check → migrate → runserver
```

**Entorno local base: listo.** Siguiente bloque de trabajo: modelos y lógica por app ([`roadmap.md`](roadmap.md)).

---

## Lo que NO necesitas (stack v1)

| No instalar | Motivo |
|-------------|--------|
| Docker (Postgres) | BD nativa ya configurada |
| SQLite como BD principal | Prohibido en v1 — solo PostgreSQL |
| Node.js / npm | Sin bundler en v1 |
| React / Vue / Bootstrap | Server-rendered HTML + CSS propio |
| `django.forms` en UI | Formularios HTML puro ([`ui-ux.md`](ui-ux.md)) |

**Frontend en templates (no pip):** jQuery + DataTables 2.x vía CDN o `static/` ([`ui-ux.md`](ui-ux.md)).

---

## Registro de avance

| Fecha | Fase | Notas |
|-------|------|-------|
| 2026-06-16 | 4 | Scaffold Django (`manage.py`, `config/`, `requirements.txt`) — **completado** |
| 2026-06-16 | 7 | Esqueleto `apps/*` (8 apps), `LOCAL_APPS`, sin vistas/modelos — **completado** |
| 2026-06-19 | 8 | `migrate` + `runserver` contra PostgreSQL — **completado** |

---

## Próximo paso recomendado

**Desarrollo por módulo** (sin mezclar todo a la vez):

1. Modelos base — `Moneda`, `UserProfile` ([`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md))
2. App `security` — login / 2FA ([`BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md`](BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md))
3. Resto de apps según [`roadmap.md`](roadmap.md)

La UI está en templates Django. Índice de módulos: [`fase-1b-landing.md`](fase-1b-landing.md) y [`prototype/README.md`](../prototype/README.md) (nota histórica).
