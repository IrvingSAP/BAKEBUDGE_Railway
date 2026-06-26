# Setup — BAKEBUDGE

> Entorno de desarrollo local.

**Seguimiento de avance (Windows + PostgreSQL nativo):** [`setup-desarrollo-checklist.md`](setup-desarrollo-checklist.md)

## Stack de desarrollo

BAKEBUDGE v1 se desarrolla **solo** con:

- **Python** + **Django**
- **PostgreSQL** (motor de base de datos)
- **HTML**, **CSS**, **JavaScript** (templates)
- **DataTables** (tablas en la interfaz)

Ver [`arquitectura.md`](arquitectura.md#stack-de-desarrollo-v1).

## Requisitos

- Python 3.12+
- **PostgreSQL 16** (instalación local **o** Docker — ver checklist)
- Git

> **Entorno actual del proyecto:** PostgreSQL nativo en Windows (sin Docker). Detalle en [`setup-desarrollo-checklist.md`](setup-desarrollo-checklist.md).

## Stack previsto

| Componente | Versión / herramienta |
|------------|----------------------|
| Lenguaje | Python 3.12+ |
| Framework | Django 5.x |
| **Base de datos** | **PostgreSQL 16** (exclusivo; no SQLite) |
| Driver BD | psycopg2-binary |
| Frontend | HTML, CSS, JavaScript (en templates) |
| Tablas UI | [DataTables](https://datatables.net/manual/) (CDN o static local) |
| Config | django-environ |
| Imágenes | Pillow |

## Dependencias iniciales (requirements.txt)

```
Django>=5.0
psycopg2-binary
django-environ
Pillow
pyotp>=2.9,<3
qrcode>=7.4,<9
# resend>=2.0,<3   # producción — opcional al inicio
```

## Variables de entorno (.env.example)

```env
DEBUG=True
SECRET_KEY=change-me-in-production
DATABASE_URL=postgres://bakebudge:bakebudge@localhost:5432/bakebudge
ALLOWED_HOSTS=localhost,127.0.0.1
```

## PostgreSQL

### Instalación local (entorno actual)

Ver Fase 1 en [`setup-desarrollo-checklist.md`](setup-desarrollo-checklist.md): usuario `bakebudge`, BD `bakebudge`, puerto `5432`.

### Alternativa: Docker (opcional)

```yaml
# docker-compose.yml (previsto)
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: bakebudge
      POSTGRES_USER: bakebudge
      POSTGRES_PASSWORD: bakebudge
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Comandos (cuando exista el proyecto)

```powershell
# Activar entorno (cada sesión)
cd C:\IACursor\BakeBudge\BAKEBUDGE
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Servidor de desarrollo
python manage.py runserver
```

> Con PostgreSQL nativo **no** se usa `docker compose up -d`.

## Settings

Estructura partida en `config/settings/`:

- `base.py` — configuración compartida
- `local.py` — desarrollo
- `production.py` — despliegue

`AUTH_USER_MODEL` = User estándar de Django + `UserProfile` (no custom user en v1).
