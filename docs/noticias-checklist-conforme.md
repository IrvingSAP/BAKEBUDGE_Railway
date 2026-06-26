# Checklist Conforme — Módulo Noticias (`apps.noticias`)

**Estado global: CERRADO — Conforme v1 (2026-06-20).**

Lista de verificación para cerrar **diseño y reglas** del módulo Noticias: feed de lectura + CRUD Master.

**Reglas:** [`noticias-reglas.md`](noticias-reglas.md)

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

| Bloque | URL de prueba |
|--------|----------------|
| Feed lectura | `http://127.0.0.1:8000/app/noticias.html` |
| Gestión Master | `http://127.0.0.1:8000/app/administracion/noticia_list.html?user_type=M` |

---

## Pantallas

| Pantalla | Archivo | Revisado | Conforme |
|----------|---------|----------|----------|
| Feed | `noticias.html` | ☑ | **Conforme** |
| Listado admin | `noticia_list.html` | ☑ | **Conforme** |
| Alta | `noticia_create.html` | ☑ | **Conforme** |
| Edición | `noticia_edit.html` | ☑ | **Conforme** |
| Desactivar | `noticia_delete.html` | ☑ | **Conforme** |

---

## Criterios globales

- [x] Menú **Gestión noticias** en Administración (solo Master)
- [x] Feed filtra por modelo (alcance, fechas, estado)
- [x] DataTables 10 / 20 / 50 en listado admin
- [x] Modal global + responsivo (375 / 768 / 1140 px)
- [x] Store demo compartido (`noticias_store.js`) feed ↔ CRUD
- [x] `noticias-reglas.md` alineado a `BAKEBUDGE_MODELS.md#noticia`

---

## Cierre aplicado

1. ✅ `noticias-reglas.md` → **Conforme**
2. ✅ `administracion/README.md` y assets `noticia_*` → **Conforme**
3. ✅ `prototype/README.md`, `dashboard-reglas.md`, `ui-ux.md` → actualizados

**Fuera de este cierre:** implementación Django → [`administracion-noticias-checklist-conforme.md`](administracion-noticias-checklist-conforme.md) (**Conforme v1**, 2026-06-20). Pendiente v2: `NoticiaLectura`, widget dashboard.

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Feed + CRUD Master | Cierre integral módulo Noticias — Conforme |
| 2026-06-20 | Implementación Django v1 | Enlace a [`administracion-noticias-checklist-conforme.md`](administracion-noticias-checklist-conforme.md) — **Conforme** (aprobación usuario) |
