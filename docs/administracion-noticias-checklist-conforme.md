# Checklist Conforme — Noticias (`apps.noticias` + `apps.administration`)

**Estado global: CERRADO — Conforme v1.2 (2026-06-20).**

Lista de verificación para cerrar **diseño, reglas e implementación Django** del módulo **Noticias**: feed de lectura (User + Master), CRUD Master (gestión), acción **Copiar** e integración **primer acceso → Noticias**.

**Reglas:** [`noticias-reglas.md`](noticias-reglas.md)  
**Checklist prototipo:** [`noticias-checklist-conforme.md`](noticias-checklist-conforme.md)  
**Diseño funcional:** [`BAKEBUDGE_NOTICIAS.md`](BAKEBUDGE_NOTICIAS.md)  
**Modelo:** [`BAKEBUDGE_MODELS.md#noticia`](BAKEBUDGE_MODELS.md#noticia)  
**Apps Django:** `apps.noticias` (modelo, feed, detalle) · `apps.administration` (gestión Master)

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# Feed:    http://127.0.0.1:8000/app/noticias/          (User + Master)
# Detalle: http://127.0.0.1:8000/app/noticias/<id>/    (solo si hay detalle)
# Gestión: http://127.0.0.1:8000/app/administracion/noticias/  (Master)
```

| Bloque | URL prototipo | URL Django |
|--------|---------------|------------|
| Feed lectura | `…/noticias.html` | `/app/noticias/` |
| Detalle lectura | — | `/app/noticias/<id>/` |
| Listado admin | `…/administracion/noticia_list.html?user_type=M` | `/app/administracion/noticias/` |
| Alta | `…/administracion/noticia_create.html` | `/app/administracion/noticias/nuevo/` |
| Edición | `…/administracion/noticia_edit.html` | `/app/administracion/noticias/<id>/editar/` |
| Copiar | — | `/app/administracion/noticias/<id>/copiar/` |
| Desactivar | `…/administracion/noticia_delete.html` | `/app/administracion/noticias/<id>/desactivar/` |

> **Nota URLs:** las reglas legacy mencionaban `/app/admin/noticias/`; la implementación Django usa `/app/administracion/noticias/` (misma convención que Monedas, Usuarios y Facturación).

---

## Bloque A — Modelo y migraciones — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | Modelo `Noticia` en `apps.noticias` — tabla `noticias_noticia` | **Conforme** |
| A2 | M2M `destinatarios` → User; auditoría `created_by` / `updated_by` | **Conforme** |
| A3 | Alcance `G`/`P`, tipo libre (≤20), título, resumen, fechas, `status` A/I | **Conforme** |
| A4 | `detalle` opcional (`blank=True`); propiedad `tiene_detalle` | **Conforme** |
| A5 | `enlace_interno`, `enlace_externo`, `destacada`, `orden` | **Conforme** |
| A6 | Migraciones `noticias.0001_initial`, `noticias.0002_…detalle` | **Conforme** |
| A7 | Admin Django `NoticiaAdmin` | **Conforme** |
| A8 | Servicios `queries.py` (visibilidad), `display.py` (resumen, badges) | **Conforme** |
| A9 | `noticias_extras` — filtros template alcance, estado, tipo | **Conforme** |

---

## Bloque B — Integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | `apps.noticias` en `INSTALLED_APPS` | **Conforme** |
| B2 | `path("app/", include("apps.noticias.urls"))` en `config/urls.py` | **Conforme** |
| B3 | Gestión Master en `apps.administration.views.noticia_views` | **Conforme** |
| B4 | 5 rutas gestión bajo `/app/administracion/noticias/` (incl. copiar) | **Conforme** |
| B5 | Sidebar **Noticias** (lectura) — User + Master | **Conforme** |
| B6 | Sidebar **Gestión noticias** — solo Master | **Conforme** |
| B7 | Layout `/app/` — `app_base.html`, modal global, responsivo | **Conforme** |
| B8 | `noticia_helpers.py` — parse, validación, defaults | **Conforme** |

---

## Bloque C — Feed lectura — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| C1 | Vista `/app/noticias/` con `@app_access_required` | ☑ | **Conforme** |
| C2 | Filtro: `status=A`, rango fechas, alcance global/personal | ☑ | **Conforme** |
| C3 | Orden: `-destacada`, `-fecha_noticia`, `orden` | ☑ | **Conforme** |
| C4 | Tarjetas: badge tipo, fecha, título, resumen | ☑ | **Conforme** |
| C5 | Texto tarjeta: `resumen` o truncado de `detalle` | ☑ | **Conforme** |
| C6 | Enlace **Leer más** solo si hay `detalle` | — | **Conforme** |
| C7 | Sin `detalle`: enlaces interno/externo en feed | ☑ | **Conforme** |
| C8 | Estado vacío informativo | ☑ | **Conforme** |
| C9 | Badge «Personal» en tarjeta alcance P | ☑ | **Conforme** |

---

## Bloque D — Detalle lectura — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Vista `/app/noticias/<id>/` con `@app_access_required` | **Conforme** |
| D2 | Mismas reglas de visibilidad que feed; 404 si no visible | **Conforme** |
| D3 | 404 si `detalle` vacío (acceso solo vía feed con cuerpo) | **Conforme** |
| D4 | Cuerpo completo (`detalle` con saltos de línea) | **Conforme** |
| D5 | Enlaces interno/externo al pie del detalle | **Conforme** |
| D6 | Botón «Volver a noticias» | **Conforme** |

---

## Bloque E — Gestión Master — **Conforme**

| # | Ítem | Prototipo | Django |
|---|------|-----------|--------|
| E1 | `@master_access` en listado, alta, edición, copiar, desactivar | ☑ | **Conforme** |
| E2 | Listado global (activas e inactivas) | ☑ | **Conforme** |
| E3 | DataTables 10 / 20 / 50, búsqueda global off | ☑ | **Conforme** |
| E4 | Orden inicial: `fecha_noticia` DESC (col. 6) | ☑ | **Conforme** |
| E5 | Filtros: título, tipo, alcance, estado + limpiar | ☑ | **Conforme** |
| E6 | Columnas según reglas + badges alcance/estado | ☑ | **Conforme** |
| E7 | Alta/edición: alcance G/P, destinatarios si P | ☑ | **Conforme** |
| E8 | Campos obligatorios: tipo, título, fechas, status | ☑ | **Conforme** |
| E9 | `detalle`, resumen, enlaces opcionales | ☑ | **Conforme** |
| E10 | Validación servidor (`noticia_helpers.py`) | — | **Conforme** |
| E11 | Validación JS cliente (`noticia_form.js`) | ☑ | **Conforme** |
| E12 | Errores: modal + resaltado campo (`form_validation`) | ☑ | **Conforme** |
| E13 | Desactivar → `status=I` (sin DELETE físico) | ☑ | **Conforme** |
| E14 | Reactivar editando `status` a `A` | ☑ | **Conforme** |
| E15 | Botón **+ Nueva noticia** | ☑ | **Conforme** |
| E16 | **Copiar** — clona registro + destinatarios; redirect edición; título ` (copia)` | — | **Conforme** |

---

## Bloque F — Assets — **Conforme**

| Ítem | Prototipo | Django |
|------|-----------|--------|
| CSS gestión | `administracion/css/noticias.css` | `apps/administration/static/…/noticias.css` |
| CSS tarjetas feed | `css/bakebudge-app.css` (`.news-*`) | `apps/dashboard/static/dashboard/css/bakebudge-app.css` |
| JS listado + filtros | `administracion/js/noticia_list.js` | `apps/administration/static/…/noticia_list.js` |
| JS formulario | `administracion/js/noticia_form.js` | `apps/administration/static/…/noticia_form.js` |
| Partial enlaces feed | — | `noticias/partials/noticia_feed_links.html` |
| DataTables vendor | `assets/js/` | Reutiliza `apps/catalog/static/catalog/vendor/` |

---

## Bloque G — Tests automatizados — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| G1 | Visibilidad global / personal / inactiva / fuera de rango | **Conforme** |
| G2 | `list_noticias_publicadas` por usuario | **Conforme** |
| G3 | Detalle: cuerpo completo, 404 sin acceso | **Conforme** |
| G4 | Feed: «Leer más» con detalle; oculto sin detalle | **Conforme** |
| G5 | Feed: enlace externo sin detalle | **Conforme** |
| G6 | `apps/noticias/tests.py` — 15 casos (incl. copiar) | **Conforme** |
| G7 | Copiar: clon, destinatarios, redirect edición, bloqueo User | **Conforme** |

---

## Bloque H — Primer acceso → Noticias — **Conforme v1.2**

| # | Ítem | Estado |
|---|------|--------|
| H1 | Redirect post-TOTP a `/app/noticias/` si primer acceso | **Conforme** |
| H2 | Campo `UserProfile.primer_acceso_app_completado` | **Conforme** |
| H3 | Siguientes logins → Dashboard | **Conforme** |
| H4 | Contenido bienvenida publicado por Master (operativo) | **Conforme** |
| H5 | Tests routing en `apps/security/tests.py` | **Conforme** |

---

## Criterios globales (layout `/app/`)

- [x] Sidebar: **Noticias** (lectura) + **Gestión noticias** (Master)
- [x] Modal global — errores, éxito, avisos
- [x] Formularios HTML puros + validación servidor
- [x] DataTables gestión: default **10**, opciones **10 · 20 · 50**
- [x] No borrado físico — desactivar (`status=I`)
- [x] Noticias de producto (no por `owner` de negocio)
- [x] Alcance global y personal con destinatarios
- [x] Acción **Copiar** en listado Master (plantillas por destinatario)
- [x] **Primer acceso** post-seguridad redirige al feed Noticias

---

## Fuera de alcance v1 (documentado)

| Ítem | Notas |
|------|-------|
| `NoticiaLectura` / badge «no leídas» en sidebar | v2 |
| Widget «últimas noticias» en dashboard | Opcional futuro |
| Pantallas de ayuda create/edit gestión | Pendiente v1.1 |
| Prototipo detalle lectura HTML | Django es referencia |
| Notificaciones push o email masivo | Futuro |
| RSS público / blog marketing | Fase 5 |

---

## Cierre aplicado

1. ✅ Reglas módulo: `noticias-reglas.md` → **Conforme** (diseño + URLs Django)
2. ✅ Checklist prototipo: `noticias-checklist-conforme.md` → **Conforme**
3. ✅ Modelo `apps.noticias` + migraciones → **Conforme v1**
4. ✅ Feed y detalle lectura → **Conforme v1**
5. ✅ CRUD Master en `apps.administration` → **Conforme v1**
6. ✅ Tests automatizados visibilidad, feed y detalle → **Conforme**
7. ✅ `docs/README.md` → enlace a este checklist
8. ✅ Acción **Copiar** en gestión — [`noticias-reglas.md`](noticias-reglas.md) **Conforme v1.1**
9. ✅ **Primer acceso → Noticias** — [`acceso-reglas.md`](acceso-reglas.md) **Conforme v1.2**

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Diseño prototipo + reglas (`noticias-reglas.md`) | Conforme — [`noticias-checklist-conforme.md`](noticias-checklist-conforme.md) |
| 2026-06-16 | Implementación Django Noticias v1 (feed + CRUD) | Revisión técnica OK |
| 2026-06-20 | Revisión usuario + ajustes (detalle opcional, enlaces feed, detalle lectura) | **Conforme** — aprobación usuario |
| 2026-06-20 | Acción **Copiar** en listado gestión (destinatarios copiados; edición para ajustar) | **Conforme v1.1** — confirmado y aprobado por usuario |
| 2026-06-20 | **Primer acceso → Noticias** (integración `apps.security`) | **Conforme v1.2** — confirmado y aprobado por usuario |
