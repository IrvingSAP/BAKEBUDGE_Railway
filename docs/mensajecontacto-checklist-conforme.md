# Checklist Conforme — Módulo MensajeContacto (`apps.public_site`)

**Estado global: CERRADO — Conforme v1 (2026-06-20).**

Lista de verificación para cerrar **diseño y reglas** del módulo MensajeContacto: formulario público + gestión Master (listado, detalle, eliminar).

**Reglas:** [`mensajecontacto-reglas.md`](mensajecontacto-reglas.md)  
**Checklist Django v1:** [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md)  
**Modelo:** [`BAKEBUDGE_MODELS.md#mensajecontacto`](BAKEBUDGE_MODELS.md#mensajecontacto)

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

| Bloque | URL de prueba |
|--------|----------------|
| Formulario público (demo) | `http://127.0.0.1:8000/contacto.html` |
| Formulario Django | `http://127.0.0.1:8000/contacto/` |
| Gestión Master | `http://127.0.0.1:8000/app/administracion/mensajecontacto_list.html?user_type=M` |
| Detalle demo | `…/mensajecontacto_detail.html?id=1&user_type=M` |
| Eliminar demo | `…/mensajecontacto_delete.html?id=1&user_type=M` |

---

## Pantallas — gestión Master

| Pantalla | Archivo | Revisado | Conforme |
|----------|---------|----------|----------|
| Listado | `mensajecontacto_list.html` | ☑ | **Conforme** |
| Detalle | `mensajecontacto_detail.html` | ☑ | **Conforme** |
| Eliminar | `mensajecontacto_delete.html` | ☑ | **Conforme** |

---

## Assets

| Ítem | Archivo | Conforme |
|------|---------|----------|
| Estilos | `css/mensajecontacto.css` | **Conforme** |
| Store demo | `js/mensajecontacto_store.js` | **Conforme** |
| Listado JS | `js/mensajecontacto_list.js` | **Conforme** |
| Detalle JS | `js/mensajecontacto_detail.js` | **Conforme** |
| Eliminar JS | `js/mensajecontacto_delete.js` | **Conforme** |
| Nav sidebar | `scripts/update-nav.py` → **Mensajes contacto** | **Conforme** |

---

## Criterios globales (diseño)

- [x] Convención `mensajecontacto_{accion}.html` en Administración
- [x] Menú **Mensajes contacto** en Administración (solo Master, `data-nav="mensajes-contacto"`)
- [x] Sin alta manual Master (mensajes solo desde formulario público)
- [x] Listado DataTables 10 / 20 / 50, orden `-created_at`
- [x] Columnas: Fecha, Nombre, Correo, Estado, Acciones
- [x] Filtros: nombre, correo, estado (`P` / `L`)
- [x] Detalle: datos completos + **Marcar como leído** + `mailto:` + enlace eliminar
- [x] Eliminar: confirmación + modal OK (demo store)
- [x] Badges estado: Pendiente / Leído
- [x] Modal global + layout `/app/` + responsivo
- [x] `mensajecontacto-reglas.md` y `BAKEBUDGE_MODELS.md#mensajecontacto` alineados
- [x] Store demo con `localStorage` (`bakebudge_mensajecontacto_demo`)

---

## Fuera de este cierre (prototipo)

Implementación Django → [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md) (**Conforme v1**, 2026-06-20). Pendiente v2: email, anti-spam.

---

## Cierre aplicado

1. ✅ `mensajecontacto-reglas.md` → **Conforme v1**
2. ✅ `administracion/README.md` → sección MensajeContacto
3. ✅ `prototype/README.md` → índice actualizado
4. ✅ `docs/README.md` → enlace checklist prototipo
5. ✅ Implementación Django → [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md) **Conforme v1**

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-19 | Gestión Master (list, detail, delete) + store demo | Cierre diseño prototipo — Conforme |
| 2026-06-20 | Implementación Django v1 | Enlace a [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md) — **Conforme** (aprobación usuario) |
