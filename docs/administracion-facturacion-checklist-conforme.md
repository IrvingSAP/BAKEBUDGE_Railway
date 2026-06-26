# Checklist Conforme — Facturación Master (`apps.billing` + `apps.administration`)

**Estado global: CERRADO — Conforme v1.1 (2026-06-16).**

Lista de verificación para cerrar **diseño, reglas e implementación Django** del módulo **Administración → Facturación** (`PaymentControl`). Solo Master.

**Reglas:** [`facturacion-reglas.md`](facturacion-reglas.md)  
**Checklist prototipo (fase 1b):** [`facturacion-checklist-conforme.md`](facturacion-checklist-conforme.md)  
**Modelo:** [`BAKEBUDGE_MODELS.md#paymentcontrol`](BAKEBUDGE_MODELS.md#paymentcontrol)  
**Apps Django:** `apps.billing` (modelo) · `apps.administration` (vistas UI)

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/app/administracion/facturacion/
# Requiere sesión Master (UserProfile.user_type = 'M')
```

| Bloque | URL Django |
|--------|------------|
| Listado | `/app/administracion/facturacion/` |
| Alta | `/app/administracion/facturacion/nuevo/` |
| Ayuda alta | `/app/administracion/facturacion/nuevo/ayuda/` |
| Edición | `/app/administracion/facturacion/<id>/editar/` |
| Ayuda edición | `/app/administracion/facturacion/<id>/editar/ayuda/` |
| Suspender / cancelar | `/app/administracion/facturacion/<id>/accion/` |

> **Nota URLs:** las reglas originales mencionaban `/app/admin/facturacion/`; la implementación Django usa `/app/administracion/facturacion/` (misma convención que Monedas y Usuarios). Redacción unificada en [`facturacion-reglas.md`](facturacion-reglas.md).

---

## Bloque A — Modelo y migraciones — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | Modelo `PaymentControl` en `apps.billing` — tabla `billing_paymentcontrol` | **Conforme** |
| A2 | FK `owner` → User, `moneda` → Moneda, auditoría `created_by` / `updated_by` | **Conforme** |
| A3 | Choices `estado`, `modalidad`, `payment_method` según reglas | **Conforme** |
| A4 | Campo `plazo_de_gracia` (`plazoDeGracia` en DB) — default 0, rango 0–30 | **Conforme** |
| A5 | Propiedades `effective_end_date`, `is_vigente`, `is_expired`, `monto_display` (vigencia con gracia) | **Conforme** |
| A6 | Migraciones `billing.0001_initial`, `billing.0002_…plazo_de_gracia` | **Conforme** |
| A7 | Admin Django `PaymentControlAdmin` | **Conforme** |
| A8 | `UserProfile.has_active_subscription` conectado a `PaymentControl` (vigencia con gracia) | **Conforme** |
| A9 | `expire_overdue_payments` — `activo → consumido` al superar `effective_end_date` | **Conforme** |
| A10 | Hook login / acceso en `apps.security.views` | **Conforme** |

---

## Bloque B — Acceso e integración — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| B1 | Decorador `@master_access` | ☑ demo `?user_type=M` | **Conforme** |
| B2 | Listado global — sin filtro `owner` en queryset | ☑ | **Conforme** |
| B3 | Alta: selector `owner` solo Users (`user_type = U`) | ☑ | **Conforme** |
| B4 | `apps.billing` en `INSTALLED_APPS` | — | **Conforme** |
| B5 | Vistas UI en `apps.administration.views.facturacion_views` | — | **Conforme** |
| B6 | 7 rutas bajo `/app/administracion/facturacion/` | — | **Conforme** |
| B7 | Menú **Facturación** en sidebar Administración | ☑ | **Conforme** |
| B8 | Redirección Usuarios → Facturación tras alta User (`?owner=<pk>`) | ☑ | **Conforme** |
| B9 | Layout `/app/` — modal global, formularios HTML | ☑ | **Conforme** |

---

## Bloque C — Listado — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| C1 | DataTables 10 / 20 / 50, búsqueda global off | ☑ | **Conforme** |
| C2 | Orden inicial: `payment_date` DESC, luego `start_date` DESC (col. 7) | ☑ | **Conforme** |
| C3 | Filtros: usuario, estado, modalidad + limpiar | ☑ | **Conforme** |
| C4 | Columnas: usuario, modalidad, estado, fechas, monto, método, fecha pago | ☑ | **Conforme** |
| C5 | Badges estado (pendiente/activo/suspendido/consumido) | ☑ | **Conforme** (`admin_extras`) |
| C6 | Acciones según estado: Editar/Ver · Suspender/Cancelar | ☑ | **Conforme** |
| C7 | Botón **+ Nuevo período** | ☑ | **Conforme** |
| C8 | Filtro contextual `?owner=` (username) desde URL | ☑ | **Conforme** |

---

## Bloque D — Alta — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| D1 | Campos: owner, modalidad, estado, período, pago, `plazo_de_gracia` | ☑ | **Conforme** |
| D2 | Default alta: `estado=pendiente`, `plazo_de_gracia=0` | ☑ | **Conforme** |
| D3 | **Guardar período** — registro pendiente sin exigir pago | ☑ | **Conforme** |
| D4 | **Guardar y activar** — valida pago + fechas + `estado=activo` | ☑ | **Conforme** |
| D5 | Validación: un solo `activo` por owner | ☑ demo JS | **Conforme** (servidor) |
| D6 | Validación `plazo_de_gracia` 0–30 | — | **Conforme** |
| D7 | Banner provisión si `?owner=` tras alta usuario | ☑ | **Conforme** |
| D8 | Ayuda create + botón en formulario | ☑ | **Conforme** |
| D9 | Errores: modal + resaltado campo | ☑ | **Conforme** |
| D10 | Validación JS cliente (`facturacion_form.js`) | ☑ | **Conforme** |

---

## Bloque E — Edición — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| E1 | `owner` solo lectura — no reasignar período | ☑ | **Conforme** |
| E2 | Auditoría created/updated readonly | ☑ | **Conforme** |
| E3 | `estado=consumido` → editable por Master + aviso informativo | ☑ | **Conforme** |
| E4 | Cambio a `activo` — mismas reglas que confirmar pago | ☑ | **Conforme** |
| E5 | Edición de `plazo_de_gracia` (0–30) | — | **Conforme** |
| E6 | Ayuda edit + botón en formulario | ☑ | **Conforme** |
| E7 | Errores: modal + resaltado campo | ☑ | **Conforme** |

---

## Bloque F — Suspender / cancelar — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| F1 | `activo` → **Suspender** → `estado=suspendido` | ☑ | **Conforme** |
| F2 | `pendiente` → **Cancelar** → `estado=suspendido` | ☑ | **Conforme** |
| F3 | `consumido` → bloqueado (histórico auditoría) | ☑ | **Conforme** |
| F4 | `suspendido` → sin acción destructiva | ☑ | **Conforme** |
| F5 | No borrado físico de registros | ☑ doc | **Conforme** |

---

## Bloque G — Assets compartidos — **Conforme**

| Ítem | Prototipo | Django |
|------|-----------|--------|
| CSS módulo | `administracion/css/facturacion.css` | `apps/administration/static/…/facturacion.css` |
| JS listado + filtros | `administracion/js/facturacion_list.js` | `apps/administration/static/…/facturacion_list.js` |
| DataTables vendor | `assets/js/` | Reutiliza `apps/catalog/static/catalog/vendor/` |
| Partials ayuda/validación | — | `form_help_link`, `form_validation` |
| `admin_extras` — badges estado/modalidad | — | **Conforme** |
| `facturacion_helpers.py` — parse, validación, defaults | — | **Conforme** |
| `subscription.py` — vigencia con gracia, `expire_overdue_payments`, fechas sugeridas | — | **Conforme** |
| `facturacion_form.js` — validación cliente alta/edición | — | **Conforme** |
| `apps/billing/tests.py` — vigencia, expiración, validación plazo | — | **Conforme** |

---

## Criterios globales (layout `/app/`)

- [x] Sidebar: Administración → Facturación (solo Master)
- [x] Modal global — errores, éxito, avisos
- [x] Formularios HTML puros + validación servidor
- [x] DataTables: default **10**, opciones **10 · 20 · 50**
- [x] Histórico 1:N por `owner` — no borrado físico
- [x] Integración flujo Master: Usuarios → Facturación → login User
- [x] `has_active_subscription` operativo — vigencia = `end_date + plazo_de_gracia`
- [x] Vencimiento automático `activo → consumido` al login del User
- [x] Tests automatizados `apps.billing.tests`

---

## Fuera de alcance v1.1 (documentado)

| Ítem | Notas |
|------|-------|
| Pasarela de pago automática | Manual por Master |
| `voucher_image` (comprobante imagen) | Fase 2 |
| Prefijo URL `/app/admin/facturacion/` en docs legacy | Unificado a `/app/administracion/facturacion/` |
| Job/cron independiente para `activo → consumido` | Cubierto al login; tarea programada opcional futura |

---

## Cierre aplicado

1. ✅ Reglas módulo: `facturacion-reglas.md` → **Conforme** (diseño + URLs Django)
2. ✅ Checklist prototipo fase 1b: `facturacion-checklist-conforme.md` → **Conforme**
3. ✅ Modelo `apps.billing` + migraciones → **Conforme v1**
4. ✅ CRUD Master Facturación en `apps.administration` → **Conforme v1**
5. ✅ Campo `plazo_de_gracia` (0–30 días) → **Conforme**
6. ✅ Integración Usuarios → Facturación + `has_active_subscription` → **Conforme**
7. ✅ `docs/README.md` → enlace a este checklist
8. ✅ v1.1: vigencia con `plazo_de_gracia`, expiración al login, edición consumido, JS, tests → **Conforme**

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Diseño prototipo + reglas (`facturacion-reglas.md`) | Conforme — bloques A–E prototipo |
| 2026-06-16 | Implementación Django Facturación Master v1 + `plazo_de_gracia` | Revisión OK — **Conforme** (aprobación usuario) |
| 2026-06-16 | v1.1 — gracia en vigencia/acceso, expiración login, Master edita consumido, JS, tests | **Conforme** |
