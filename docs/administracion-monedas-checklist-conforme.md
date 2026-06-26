# Checklist Conforme — Monedas Master (`apps.administration`)

**Estado global: CERRADO — Conforme v1 (2026-06-20).**

Lista de verificación para cerrar **implementación Django** del CRUD Master de **Monedas** (`core.Moneda`) en la zona `/app/administracion/monedas/`.

**Modelo:** [`BAKEBUDGE_MODELS.md#moneda`](BAKEBUDGE_MODELS.md#moneda)  
**App Django:** `apps.administration`

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/app/administracion/monedas/
# Requiere sesión Master (UserProfile.user_type = 'M')
```

| Pantalla | URL Django |
|----------|------------|
| Listado | `/app/administracion/monedas/` |
| Alta | `/app/administracion/monedas/nuevo/` |
| Edición | `/app/administracion/monedas/<codigo>/editar/` |
| Eliminación | `/app/administracion/monedas/<codigo>/eliminar/` |

---

## Bloque A — Acceso y seguridad — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | Decorador `@master_access` (login + perfil + `is_master`) | **Conforme** |
| A2 | Usuarios no Master → `dashboard:access_denied` | **Conforme** |
| A3 | Menú **Monedas** en sidebar Administración (solo Master) | **Conforme** |
| A4 | Layout `/app/` — `app_base.html`, modal global | **Conforme** |

---

## Bloque B — Listado — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | DataTables 10 / 20 / 50, búsqueda global off | **Conforme** |
| B2 | Orden inicial: `orden` ASC, luego `codigo` | **Conforme** |
| B3 | Filtros: nombre, estado activa/inactiva + limpiar | **Conforme** |
| B4 | Columnas: código, nombre, símbolo, decimales, estado, orden, perfiles, acciones | **Conforme** |
| B5 | Conteo de perfiles por moneda (`annotate`) | **Conforme** |
| B6 | Botón **+ Nueva moneda** | **Conforme** |

---

## Bloque C — Alta y edición — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | Campos: código (ISO 3 letras), nombre, símbolo, decimales, orden, activa | **Conforme** |
| C2 | Código solo en alta; readonly en edición | **Conforme** |
| C3 | Validación servidor: código único, decimales 0–6, orden ≥ 0 | **Conforme** |
| C4 | Errores: modal + resaltado campo (`form_validation`) | **Conforme** |
| C5 | Éxito vía `messages.success` + redirect al listado | **Conforme** |

---

## Bloque D — Eliminación — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Bloqueo si `perfiles_count > 0` (FK `PROTECT`) | **Conforme** |
| D2 | Confirmación con resumen de la moneda | **Conforme** |
| D3 | Manejo `ProtectedError` con mensaje al usuario | **Conforme** |

---

## Bloque E — Integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| E1 | `apps.administration` en `INSTALLED_APPS` | **Conforme** |
| E2 | URLs en `config/urls.py` bajo `app/` | **Conforme** |
| E3 | Modelo `Moneda` en `apps.core` (sin duplicar) | **Conforme** |
| E4 | Seed existente `core.0002_seed_monedas` | **Conforme** |
| E5 | Django Admin `MonedaAdmin` conservado | **Conforme** |

---

## Fuera de alcance v1 (documentado)

| Ítem | Notas |
|------|-------|
| Pantallas de ayuda create/edit | Pendiente v1.1 |
| Prototipo HTML `moneda_list.html` | No existía; Django es referencia |
| Otros módulos Administración | Ayuda pendiente — Monedas, Usuarios, Facturación, Noticias y Mensajes contacto **Conforme v1** |
| Filtro por código en listado | v1.1 opcional |

---

## Cierre aplicado

1. ✅ CRUD Master Monedas en `apps.administration` → **Conforme v1**
2. ✅ Sidebar Administración → Monedas
3. ✅ `docs/README.md` → enlace a este checklist

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-20 | Implementación Django Monedas Master | Revisión OK — **Conforme** (aprobación usuario) |
