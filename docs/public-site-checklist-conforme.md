# Checklist Conforme — Zona pública (`apps.public_site` + gestión Master)

**Estado global: CERRADO — Conforme v1 (2026-06-20).**

Lista de verificación para cerrar **diseño, reglas e implementación Django** de la **zona pública** (landing + contacto) y **MensajeContacto** (persistencia + gestión Master).

**Reglas:** [`mensajecontacto-reglas.md`](mensajecontacto-reglas.md)  
**Checklist prototipo landing:** [`fase-1b-landing.md`](fase-1b-landing.md)  
**Checklist prototipo gestión:** [`mensajecontacto-checklist-conforme.md`](mensajecontacto-checklist-conforme.md)  
**Modelo:** [`BAKEBUDGE_MODELS.md#mensajecontacto`](BAKEBUDGE_MODELS.md#mensajecontacto)  
**Apps Django:** `apps.public_site` (landing, contacto, modelo) · `apps.administration` (gestión Master)

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# Landing:  http://127.0.0.1:8000/
# Contacto: http://127.0.0.1:8000/contacto/
# Gestión:  http://127.0.0.1:8000/app/administracion/mensajes-contacto/  (Master)
```

| Bloque | URL Django |
|--------|------------|
| Home | `/` |
| Servicios | `/servicios/` |
| Contacto | `/contacto/` |
| Listado Master | `…/administracion/mensajecontacto_list.html?user_type=M` | `/app/administracion/mensajes-contacto/` |
| Detalle Master | `…/administracion/mensajecontacto_detail.html` | `/app/administracion/mensajes-contacto/<id>/` |
| Eliminar Master | `…/administracion/mensajecontacto_delete.html` | `/app/administracion/mensajes-contacto/<id>/eliminar/` |

> **Nota URLs:** las reglas legacy mencionaban `/app/admin/mensajes-contacto/`; la implementación Django usa `/app/administracion/mensajes-contacto/` (misma convención que Monedas, Usuarios, Facturación y Noticias).

---

## Bloque A — Modelo y migraciones — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | Modelo `MensajeContacto` en `apps.public_site` — tabla `public_site_mensajecontacto` | **Conforme** |
| A2 | Campos: `nombre`, `email`, `mensaje`, `estado` P/L, `created_at`, `leido_at`, `ip_origen` | **Conforme** |
| A3 | Índices `(estado, -created_at)` y `(-created_at,)` | **Conforme** |
| A4 | Método `marcar_leido()` + propiedad `is_pendiente` | **Conforme** |
| A5 | Migración `public_site.0001_initial` | **Conforme** |
| A6 | Admin Django `MensajeContactoAdmin` | **Conforme** |
| A7 | Servicio `contacto_helpers.py` — parse, validación, IP cliente | **Conforme** |

---

## Bloque B — Landing pública — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| B1 | Home `/` — hero, valor, CTA | ☑ | **Conforme** |
| B2 | Servicios `/servicios/` | ☑ | **Conforme** |
| B3 | Contacto `/contacto/` — layout dual (info + formulario) | ☑ | **Conforme** |
| B4 | `base_public.html` — header, footer, modal global | ☑ | **Conforme** |
| B5 | CSS `bakebudge-home.css` — tokens pastel, responsive | ☑ | **Conforme** |
| B6 | JS `main.js` — nav móvil, link activa (`data-page`) | ☑ | **Conforme** |
| B7 | Modal global vía `messages` (OK/ER/AV/IN) | ☑ | **Conforme** |
| B8 | Meta description y `<title>` por página | ☑ | **Conforme** |
| B9 | `apps.public_site` en `INSTALLED_APPS` + URLs en `config/urls.py` | — | **Conforme** |

---

## Bloque C — Formulario contacto (público) — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| C1 | `POST` real con CSRF | demo JS | **Conforme** |
| C2 | Validación servidor: nombre, email, mensaje (10–5000 chars) | — | **Conforme** |
| C3 | Persistencia `MensajeContacto` con `estado=P` | — | **Conforme** |
| C4 | `ip_origen` opcional desde request | — | **Conforme** |
| C5 | Éxito: modal OK + redirect PRG | demo modal | **Conforme** |
| C6 | Error validación: modal ER + repoblar campos | — | **Conforme** |
| C7 | No crea `User` ni activa registro | ☑ doc | **Conforme** |

---

## Bloque D — Integración gestión Master — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Vistas en `apps.administration.views.mensajecontacto_views` | **Conforme** |
| D2 | `@master_access` en listado, detalle, eliminar | **Conforme** |
| D3 | 3 rutas bajo `/app/administracion/mensajes-contacto/` | **Conforme** |
| D4 | Sidebar **Mensajes contacto** (solo Master) | **Conforme** |
| D5 | Filtros template `mensaje_estado_*` en `admin_extras` | **Conforme** |
| D6 | User estándar → sin acceso a gestión | **Conforme** |

---

## Bloque E — Gestión Master — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| E1 | Listado DataTables 10 / 20 / 50, búsqueda global off | ☑ | **Conforme** |
| E2 | Orden inicial: `-created_at` (col. fecha) | ☑ | **Conforme** |
| E3 | Columnas: fecha, nombre, correo, estado, acciones | ☑ | **Conforme** |
| E4 | Filtros: nombre, correo, estado + limpiar | ☑ | **Conforme** |
| E5 | Badges Pendiente / Leído | ☑ | **Conforme** |
| E6 | Detalle: datos completos + mensaje (`pre-wrap`) | ☑ | **Conforme** |
| E7 | **Marcar como leído** → `estado=L`, `leido_at=now()` | ☑ | **Conforme** |
| E8 | Enlace `mailto:` al solicitante | ☑ | **Conforme** |
| E9 | Eliminar: confirmación + borrado físico | ☑ | **Conforme** |
| E10 | Sin alta manual desde Master | ☑ doc | **Conforme** |
| E11 | Éxito vía `messages.success` + redirect | — | **Conforme** |

---

## Bloque F — Assets — **Conforme**

| Ítem | Ubicación Django |
|------|------------------|
| CSS landing | `apps/public_site/static/…/bakebudge-home.css` |
| CSS gestión | `apps/administration/static/…/mensajecontacto.css` |
| JS listado | `apps/administration/static/…/mensajecontacto_list.js` |
| Modal global | `apps/core/static/css/bakebudge-modal.css` (compartido) |
| DataTables vendor | `apps/catalog/static/catalog/vendor/` (reutilizado) |

---

## Bloque G — Tests automatizados — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| G1 | Validación formulario contacto | **Conforme** |
| G2 | `POST` público crea registro | **Conforme** |
| G3 | `POST` inválido no persiste | **Conforme** |
| G4 | Master listado, marcar leído, eliminar | **Conforme** |
| G5 | User estándar bloqueado en gestión | **Conforme** |
| G6 | `apps/public_site/tests.py` — 8 casos | **Conforme** |

---

## Criterios globales

- [x] Zona pública accesible sin login (`/`, `/servicios/`, `/contacto/`)
- [x] Formulario HTML puro + validación servidor
- [x] Modal global — errores y éxito (no `alert()`)
- [x] DataTables gestión: default **10**, opciones **10 · 20 · 50**
- [x] Mensajes solo entran vía formulario público (sin alta Master)
- [x] Borrado físico en gestión (mensaje transaccional)
- [x] Layout `/app/` para gestión Master

---

## Fuera de alcance v1 (documentado)

| Ítem | Notas |
|------|-------|
| Email al equipo / acuse al visitante | v2 — `email_delivery` |
| Rate limiting / CAPTCHA | v2 anti-spam |
| Export CSV | Futuro |
| Crear `User` desde detalle del mensaje | Flujo manual Master |
| Validación JS cliente en contacto público | v1.1 opcional |

---

## Cierre aplicado

1. ✅ Reglas: `mensajecontacto-reglas.md` → **Conforme v1**
2. ✅ Checklist prototipo gestión: `mensajecontacto-checklist-conforme.md` → **Conforme**
3. ✅ Landing Django: home, servicios, contacto → **Conforme v1**
4. ✅ Modelo + `POST` contacto + gestión Master → **Conforme v1**
5. ✅ Tests automatizados → **Conforme**
6. ✅ `docs/README.md` → enlace a este checklist

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Landing Django (`apps.public_site`) | Conforme — [`fase-1b-landing.md`](fase-1b-landing.md) |
| 2026-06-19 | Gestión Master prototipo + reglas | Conforme — [`mensajecontacto-checklist-conforme.md`](mensajecontacto-checklist-conforme.md) |
| 2026-06-20 | Implementación Django `apps.public_site` v1 + gestión Master | Revisión OK — **Conforme** (aprobación usuario) |
