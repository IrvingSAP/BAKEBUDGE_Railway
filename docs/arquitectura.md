# Arquitectura — BAKEBUDGE

## Visión general

BAKEBUDGE tiene dos superficies web:

| Zona | Propósito | Acceso |
|------|-----------|--------|
| **Pública** | Marca, ilustraciones, recetas destacadas (marketing), CTA Entrar/Registro | Sin login |
| **Privada** | CRUD de productos, recetas, costos, producción | Login obligatorio |

## Stack de desarrollo (v1)

Stack **oficial y único** para el desarrollo actual de BAKEBUDGE:

| Capa | Tecnología | Notas |
|------|------------|-------|
| Lenguaje | **Python** 3.12+ | |
| Framework | **Django** 5.x | Vistas, ORM, templates (formularios en HTML puro) |
| Base de datos | **PostgreSQL** 16 | Motor exclusivo v1; conexión vía `psycopg2` / `DATABASE_URL` |
| Marcado | **HTML** | Templates Django |
| Estilos | **CSS** | Tokens propios (`tokens.css`) |
| Scripts | **JavaScript** | En templates/HTML solo si se necesita |
| Tablas UI | [**DataTables**](https://datatables.net/manual/) | Listados CRUD y analytics |

> No se usará SQLite ni otros motores en v1. PostgreSQL local con Docker (ver [`setup.md`](setup.md)).

## Enfoque frontend

Stack acordado para todo el desarrollo:

| Tecnología | Uso |
|------------|-----|
| **Python** + **Django** | Backend, ORM, vistas, templates |
| **HTML** | Templates Django (`{% extends %}`, partials por app) |
| **CSS** | Estilos propios; tokens en `apps/core/static/css/tokens.css` |
| **JavaScript** | Solo donde aporte valor (p. ej. init de tablas, validaciones puntuales); inline o `<script>` en templates, sin bundler en v1 |
| [**DataTables**](https://datatables.net/manual/) | Tablas interactivas en listados (productos, recetas, órdenes, analytics) |

**Principios:**

- Django **server-rendered** (templates + vistas basadas en clases o funciones).
- **Sin React/SPA** en la fase base.
- DataTables sobre `<table>` renderizada en servidor; configuración mínima en JS por vista.
- Estética pastel documentada en [`ui-ux.md`](ui-ux.md).
- **Diseño responsivo obligatorio** en todas las páginas (prototipos y templates Django); ver [`ui-ux.md#diseño-responsivo-obligatorio`](ui-ux.md#diseño-responsivo-obligatorio).

### Assets estáticos (convención)

```
apps/core/static/
├── css/
│   ├── tokens.css          # Variables de diseño
│   └── datatables-theme.css # Ajustes visuales DataTables + tokens BAKEBUDGE
└── js/
    ├── datatables-init.js  # Helpers comunes (idioma es, defaults)
    └── bakebudge-modal.js    # Modal global de mensajes
```

DataTables: incluir CSS/JS desde CDN en `base.html` de la app privada o archivos locales en `static/` (decisión al scaffold). Manual de referencia: https://datatables.net/manual/

## Estructura modular Django

Todas las **apps propias del sistema** viven bajo la carpeta **`apps/`**. En la raíz solo quedan `config/` (proyecto Django), `docs/`, `manage.py` y archivos de entorno.

```
BAKEBUDGE/
├── docs/
├── prototype/                  # Nota histórica (README); HTML archivado fuera del repo
├── manage.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── config/                     # Proyecto Django (settings, urls, wsgi)
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
└── apps/                       # Apps propias del sistema
    ├── core/                   # Utilidades compartidas, email_delivery
    │   ├── mixins.py
    │   ├── models.py
    │   └── templates/base.html
    ├── accounts/               # UserProfile (negocio + seguridad)
    ├── security/               # Login, registro, correo, TOTP
    ├── dashboard/              # Home autenticado /app/
    ├── catalog/                # ProductCategory, Producto, CostoIndirecto, ConversionUnidad
    ├── recipes/                # Receta, versiones, ingredientes, pasos
    ├── production/             # OrdenProduccion
    ├── analytics/              # ProduccionAnalytics, snapshots
    ├── noticias/             # Noticia — feed global
    ├── billing/                # PaymentControl
    └── public_site/            # Landing y páginas de marca
```

### Convención `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # Django built-ins...
    "apps.core",
    "apps.accounts",
    "apps.security",
    "apps.public_site",
    "apps.dashboard",
    "apps.catalog",
    "apps.administration",
    "apps.billing",
    "apps.noticias",
    "apps.recipes",
    "apps.production",
    "apps.analytics",
    "apps.ayuda",
]
```

Cada app usa `AppConfig` con `name = "apps.<app>"` (p. ej. `apps/catalog/apps.py` → `name = "apps.catalog"`).

**Imports:** `from apps.accounts.models import UserProfile`  
**URLs:** `path("", include("apps.security.urls"))`

## Aislamiento de datos

- Cada usuario es individual; no comparte información con otros.
- Todo modelo de negocio lleva `owner = ForeignKey(User)` (o mixin equivalente).
- Vistas y querysets siempre filtran por `request.user`.
- **Toda pantalla bajo `/app/`** (dashboard, listados, estadísticas, perfil) muestra únicamente datos del usuario conectado. Detalle por pantalla: [`dashboard-reglas.md`](dashboard-reglas.md#regla-fundamental-datos-del-usuario-conectado).
- Nunca exponer IDs de otros usuarios.

**Excepciones:** noticias del sistema (global), catálogo `Moneda` (lectura), landing pública. Ver tabla de excepciones en [`dashboard-reglas.md`](dashboard-reglas.md#excepciones-documentadas).

## Decisiones técnicas (v1)

1. **Stack cerrado v1** — Python, Django, PostgreSQL, HTML, CSS, JS puntual, DataTables (sin alternativas de BD ni SPA).
2. **PostgreSQL obligatorio** — desarrollo y producción; Django `DATABASES` apunta siempre a Postgres.
3. **No API REST en v1** — vistas Django + HTML; DRF solo si más adelante se necesita app móvil.
4. **Formularios solo HTML** — no usar `django.forms` (`Form` / `ModelForm`); markup HTML en templates y procesamiento en vistas vía `request.POST`. Ver [`ui-ux.md`](ui-ux.md#formularios-solo-html-sin-django-forms).
5. **Frontend HTML + CSS + JS** — sin framework JS; JavaScript en templates solo cuando se requiera (DataTables, UX puntual).
6. **Listados con DataTables** — productos, recetas, producción, analytics; ver [`ui-ux.md`](ui-ux.md#tablas-datatables).
7. **Versionado de recetas** desde el inicio — preserva historial de costos.
8. **Costos en servicio** (`recipes/services/cost_calculator.py`) — testeable y reutilizable.
9. **Soft delete** — campo `activo` en Producto/Receta en lugar de borrado físico.
10. **Imágenes** — `MEDIA_ROOT` local en dev; S3/Cloudinary en producción (fase posterior).

## Apps y responsabilidades

| App (`apps.*`) | Responsabilidad |
|----------------|-----------------|
| `apps.core` | Modelos base, mixins, email_delivery, templates compartidos, CSS tokens |
| `apps.accounts` | UserProfile (negocio + flags 2FA), señales post-registro |
| `apps.security` | Wizard login/registro, correo, TOTP, reset 2FA |
| `apps.dashboard` | Panel autenticado `/app/`; consume analytics para estadísticas |
| `apps.catalog` | Categorías de producto, insumos, costos indirectos y conversiones de unidad |
| `apps.recipes` | Recetas, versiones, ingredientes, pasos, cálculo de costos |
| `apps.production` | Órdenes de producción |
| `apps.analytics` | Snapshots al completar órdenes; `/app/estadisticas/`; `record_production`, `summary` |
| `apps.ayuda` | Ayuda General: guía paso a paso del ciclo en `/app/ayuda/` (**Conforme v1**) |
| `apps.noticias` | Noticias globales — feed `/app/noticias/` + CRUD Master |
| `apps.billing` | `PaymentControl` y suscripciones (modelo ✓; gate en evolución) |
| `apps.administration` | Master: usuarios, facturación, monedas, noticias, mensajes contacto |
| `apps.public_site` | Landing y contenido de marca |

## Seguridad y acceso

Flujo completo documentado en [`BAKEBUDGE_SECURITY.md`](BAKEBUDGE_SECURITY.md):

1. **Registro público** → crea `User` + `UserProfile`
2. **Primer login** → correo (5 min) + TOTP (QR)
3. **Login recurrente** → contraseña + TOTP
4. **Zona privada** (`/app/`) → requiere `@login_required` + `is_security_complete`

URLs de seguridad: `/ingresar/`, `/registro/`, `/seguridad/*`  
Destino post-login: `/app/` (`dashboard:home`)
