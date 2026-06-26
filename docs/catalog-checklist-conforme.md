# Checklist Conforme — Catálogo base (`apps.catalog`)

**Estado global: CERRADO — Conforme v1 (2026-06-20).**

Lista de verificación para cerrar **diseño, reglas e implementación Django** del catálogo base: **Productos**, **Categorías**, **Conversiones de unidad** y **Costos indirectos**.

**Reglas:**

- [`productos-reglas.md`](productos-reglas.md)
- [`categorias-reglas.md`](categorias-reglas.md)
- [`conversiones-reglas.md`](conversiones-reglas.md)
- [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md)

**Modelos:** [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) — `ProductCategory`, `Producto`, `ConversionUnidad`, `CostoIndirecto`

**App Django:** `apps/catalog/`

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/app/  (requiere sesión /app/)
```

| Bloque | URL Django |
|--------|------------|
| Productos — listado | `/app/productos/` |
| Productos — alta | `/app/productos/nuevo/` |
| Productos — ayuda alta | `/app/productos/nuevo/ayuda/` |
| Productos — edición | `/app/productos/<id>/editar/` |
| Productos — ayuda edición | `/app/productos/<id>/editar/ayuda/` |
| Productos — eliminar | `/app/productos/<id>/eliminar/` |
| Categorías — listado | `/app/categorias/` |
| Categorías — CRUD + ayuda | `/app/categorias/…` |
| Conversiones — listado | `/app/conversiones/` |
| Conversiones — CRUD + ayuda | `/app/conversiones/…` |
| Costos indirectos — listado | `/app/costos-indirectos/` |
| Costos indirectos — CRUD + ayuda | `/app/costos-indirectos/…` |

> **Nota URLs:** las reglas mencionan prefijo `/app/catalogo/…`; la implementación Django usa rutas directas (`/app/categorias/`, etc.) alineadas con el sidebar. Comportamiento equivalente; pendiente unificar redacción en reglas.

---

## Bloque A — Modelos y migraciones — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | `ProductCategory` — constraints `(owner, nombre)` y `(owner, codigo)` | **Conforme** |
| A2 | `Producto` — FK categoría PROTECT, `costo_por_unidad_base >= 0`, default status `P` | **Conforme** |
| A3 | `ConversionUnidad` — unicidad genérica / por producto, `factor > 0`, `clean()` | **Conforme** |
| A4 | `CostoIndirecto` — `UnidadCobro` v1, índices `(owner, status)` | **Conforme** |
| A5 | Migración inicial `catalog.0001_initial` | **Conforme** |
| A6 | Admin Django registrado (4 modelos) | **Conforme** |
| A7 | Constantes `Status` y `UnidadCobro` en `constants.py` | **Conforme** |

---

## Bloque B — Integración y multi-tenant — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | `apps.catalog` en `INSTALLED_APPS` | **Conforme** |
| B2 | `path("app/", include("apps.catalog.urls"))` en `config/urls.py` | **Conforme** |
| B3 | Decorador `@catalog_access` (login + perfil + `can_access_app`) | **Conforme** |
| B4 | Scope `owner=request.user` en listados y `get_object_or_404(..., owner=…)` | **Conforme** |
| B5 | Seeds al registrar usuario (`ensure_user_catalog_defaults`) | **Conforme** |
| B6 | Signal `accounts` → categorías + conversiones predeterminadas | **Conforme** |
| B7 | Sidebar: Productos + Catálogo base (3 submódulos) | **Conforme** |
| B8 | Dashboard KPI productos (`apps/dashboard/services/summary.py`) | **Conforme** |
| B9 | Layout `/app/` — `app_base.html`, modal global, responsivo | **Conforme** |

---

## Bloque C — Productos — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| C1 | Listado DataTables 10 / 20 / 50 | ☑ | **Conforme** |
| C2 | Filtros: nombre, categoría, estado + limpiar | ☑ | **Conforme** |
| C3 | Columnas: nombre, categoría, unidad, costo, estado, acciones | ☑ | **Conforme** |
| C4 | Badges P / A / I (`status_label`, `status_badge`) | ☑ | **Conforme** |
| C5 | Costo formateado con moneda de perfil | ☑ | **Conforme** |
| C6 | Alta: 4 campos obligatorios + validación servidor | ☑ | **Conforme** |
| C7 | `unidad_base` desde `ConversionUnidad.hacia_unidad` del owner | ☑ | **Conforme** |
| C8 | Bloqueo alta sin conversiones (redirect + mensaje) | ☑ | **Conforme** |
| C9 | Edición: mismas reglas que alta | ☑ | **Conforme** |
| C10 | Eliminación: soft-delete (`status=I`) si `ProtectedError` | ☑ | **Conforme** |
| C11 | Ayuda create/edit + botón en formulario (nueva pestaña) | ☑ | **Conforme** |
| C12 | Errores: modal global + resaltado campo (`form_validation`) | ☑ | **Conforme** |
| C13 | Botón «Guardar y marcar activo» | ☑ | Pendiente v1.1 |
| C14 | Validación JS cliente (como `producto_create.js`) | ☑ | Pendiente v1.1 |
| C15 | Selector categoría solo activas en formulario | — | Pendiente v1.1 |
| C16 | Campo `pk` solo lectura en edición | ☑ | Pendiente v1.1 |

---

## Bloque D — Categorías — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| D1 | Listado DataTables 10 / 20 / 50 | ☑ | **Conforme** |
| D2 | Orden inicial por `orden`, luego nombre | ☑ | **Conforme** |
| D3 | Filtros: nombre, estado, predeterminada + limpiar | ☑ | **Conforme** |
| D4 | Columnas: orden, nombre, código, color, predeterminada, estado | ☑ | **Conforme** |
| D5 | Alta/edición: nombre + orden obligatorios | ☑ | **Conforme** |
| D6 | Default status `A` en alta | ☑ | **Conforme** |
| D7 | Eliminación bloqueada si tiene productos asociados | ☑ | **Conforme** |
| D8 | Ayuda create/edit + botón en formulario | ☑ | **Conforme** |
| D9 | Errores: modal + resaltado campo | ☑ | **Conforme** |
| D10 | Validación unicidad nombre/código (vista, case-insensitive) | ☑ | Pendiente v1.1 |
| D11 | Validación color hex `#RRGGBB` | ☑ | Pendiente v1.1 |
| D12 | `es_predeterminada` solo lectura en formulario manual | ☑ | Pendiente v1.1 |
| D13 | Botón «Guardar y marcar activo» | ☑ | Pendiente v1.1 |

---

## Bloque E — Conversiones — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| E1 | Listado DataTables 10 / 20 / 50 | ☑ | **Conforme** |
| E2 | Filtros: etiqueta/unidad, alcance, hacia unidad + limpiar | ☑ | **Conforme** |
| E3 | Columnas: etiqueta, alcance, desde, hacia, factor, equivalencia | ☑ | **Conforme** |
| E4 | Alta: desde, hacia, factor obligatorios; factor > 0 | ☑ | **Conforme** |
| E5 | Alcance genérico (`producto=null`) o por producto | ☑ | **Conforme** |
| E6 | `hacia_unidad` = unidad base del producto si aplica | ☑ | **Conforme** |
| E7 | Ayuda create/edit + botón en formulario | ☑ | **Conforme** |
| E8 | Errores: modal + resaltado campo | ☑ | **Conforme** |
| E9 | Vista previa fórmula en tiempo real (formulario) | ☑ | Pendiente v1.1 |
| E10 | Validación JS cliente | ☑ | Pendiente v1.1 |

---

## Bloque F — Costos indirectos — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| F1 | Listado DataTables 10 / 20 / 50 | ☑ | **Conforme** |
| F2 | Filtros: nombre, estado, unidad cobro + limpiar | ☑ | **Conforme** |
| F3 | Columnas: nombre, costo/unidad, unidad cobro, tarifa ref., estado | ☑ | **Conforme** |
| F4 | Alta: nombre, unidad cobro, costo obligatorios | ☑ | **Conforme** |
| F5 | Default status `P` en alta; activo exige costo > 0 | ☑ | **Conforme** |
| F6 | Ayuda create/edit + botón en formulario | ☑ | **Conforme** |
| F7 | Errores: modal + resaltado campo | ☑ | **Conforme** |
| F8 | Botón «Guardar y marcar activo» | ☑ | Pendiente v1.1 |
| F9 | Vista previa tarifa en tiempo real (formulario) | ☑ | Pendiente v1.1 |

---

## Bloque G — Assets compartidos — **Conforme**

| Ítem | Prototipo | Django |
|------|-----------|--------|
| CSS por módulo (`productos`, `categorias`, `conversiones`, `costos-indirectos`) | ☑ | `apps/catalog/static/catalog/css/` |
| JS listados + filtros DataTables | ☑ | `apps/catalog/static/catalog/js/*_list.js` |
| DataTables vendor + `datatables-init.js` | ☑ | `apps/catalog/static/catalog/vendor/` |
| i18n DataTables es-ES | ☑ | `apps/catalog/static/catalog/i18n/` |
| Icono ayuda | ☑ | `apps/catalog/static/catalog/images/icon-help.svg` |
| Partials: `form_help_link`, `form_validation` | — | **Conforme** |
| `catalog_extras` (`status_label`, `status_badge`, `format_money`) | — | **Conforme** |
| `apps/core/form_validation.py` + `bakebudge-form-errors.js` | — | **Conforme** |

---

## Criterios globales (layout `/app/`)

- [x] Sidebar: Productos + Catálogo base (Categorías, Conversiones, Costos indirectos)
- [x] Topbar **Usuario** + **Cerrar sesión**
- [x] Regla **datos por `request.user`** en queryset y formularios
- [x] Modal global (`BakeBudgeModal`) — errores, éxito, avisos; no `alert()`
- [x] Errores de formulario: mensaje con nombre de campo + resaltado inline
- [x] Formularios HTML puros (sin `django.forms`)
- [x] DataTables: default **10**, opciones **10 · 20 · 50**, búsqueda global off en listados CRUD
- [x] 28 rutas CRUD + ayuda bajo `/app/`
- [x] `@catalog_access` en todas las vistas catalog
- [x] Seeds categorías (4) + conversiones genéricas (5) al alta de usuario

---

## Fuera de alcance v1 (documentado)

| Ítem | Notas |
|------|-------|
| Tests automatizados (`apps/catalog/tests.py`) | Stub vacío — cubrir en v1.1 |
| Botón «Guardar y marcar activo» | Documentado en reglas y ayudas; pendiente en formularios Django |
| Validación JS en formularios create/edit | Prototipo sí; Django solo servidor en v1 |
| Vista previa en vivo (fórmula conversión, tarifa costo) | Solo en ayuda/prototipo |
| Filtros server-side en listados | v1 filtra en cliente con DataTables |
| Prefijo URL `/app/catalogo/` | Docs vs implementación — unificar redacción |
| Recetas / producción consumiendo catálogo | Apps futuras (`recipes`, `production`) |

---

## Cierre aplicado

1. ✅ Reglas módulo: `productos-reglas.md`, `categorias-reglas.md`, `conversiones-reglas.md`, `costos-indirectos-reglas.md` → **Conforme** (diseño)
2. ✅ Implementación Django `apps.catalog` → **Conforme v1**
3. ✅ Integración `/app/`, sidebar, dashboard, accounts seeds → **Conforme**
4. ✅ Pantallas de ayuda (8) + validación modal/campo → **Conforme**
5. ✅ `docs/README.md` → enlace a este checklist

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Diseño prototipo + reglas (4 módulos catálogo) | Conforme — reglas aprobadas |
| 2026-06-20 | Implementación Django `apps.catalog` v1 | CRUD, ayuda, listados, seeds, validación — Conforme con pendientes v1.1 documentados |
