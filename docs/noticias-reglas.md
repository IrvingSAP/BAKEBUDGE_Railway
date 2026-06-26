# Reglas del módulo Noticias — `Noticia` (`apps.noticias`)

**Estado:** **Conforme v1.2** — prototipo, reglas e implementación Django aprobados; **Copiar** (v1.1) y **primer acceso → Noticias** (v1.2) confirmados (2026-06-20). Checklists: [`noticias-checklist-conforme.md`](noticias-checklist-conforme.md), [`administracion-noticias-checklist-conforme.md`](administracion-noticias-checklist-conforme.md), [`acceso-checklist-conforme.md`](acceso-checklist-conforme.md).

Convenciones para **lectura** (todos los usuarios con acceso) y **CRUD** (solo Master).

**Checklist:** [`noticias-checklist-conforme.md`](noticias-checklist-conforme.md)  
**Template Django:** `apps/noticias/templates/noticias/feed.html` · **URL:** `/app/noticias/`  
**Templates Django:** `apps/administration/templates/administration/noticias/` · **URL:** `/app/administracion/noticias/`  
**Modelo:** [`BAKEBUDGE_MODELS.md#noticia`](BAKEBUDGE_MODELS.md#noticia)  
**Relacionado:** [`dashboard-reglas.md`](dashboard-reglas.md), [`acceso-reglas.md`](acceso-reglas.md), [`usuarios-reglas.md`](usuarios-reglas.md), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| Feed `/app/noticias/` (User + Master) | RSS público / blog marketing |
| Alcance global y personal | Edición por usuarios estándar |
| **Pantalla de bienvenida** en primer acceso post-seguridad | `NoticiaLectura` / badge «no leídas» (v2) |
| CRUD Master en Administración | Notificaciones push o email |
| Periodo de visibilidad por fechas | — |

---

## Dos zonas de UI

| Zona | Menú | Quién | Prototipo |
|------|------|-------|-----------|
| **Lectura** | Sidebar → **Noticias** | User + Master autenticados | `noticias.html` |
| **Gestión** | Administración → **Gestión noticias** | Solo Master | `administracion/noticia_*.html` |

Prototipo Master: `?user_type=M` en URL (menú Administración visible).

---

## Primer acceso → Noticias — **Conforme v1.2** (aprobación usuario 2026-06-20)

Tras completar login + correo + 2FA (`apps.security`), el **primer** ingreso a `/app/` redirige al feed **`/app/noticias/`** en lugar del Dashboard.

| Aspecto | Regla |
|---------|--------|
| Trigger | `UserProfile.primer_acceso_app_completado = False` y `can_access_app` |
| Destino | `noticias:feed` |
| Contenido | Master publica noticias de bienvenida, primeros pasos y flujo del sistema |
| Alcance | Global (todos) y/o **Personal** (por usuario; usar **Copiar** para plantillas) |
| Siguiente login | Dashboard (`/app/`) — flag ya en `True` |
| Implementación | [`post_login_routing.py`](../apps/security/services/post_login_routing.py) · [`acceso-reglas.md`](acceso-reglas.md) |

---

## Regla fundamental: visibilidad en lectura

Una noticia aparece en `noticias.html` solo si:

1. `status = 'A'`
2. `visible_desde ≤ hoy ≤ visible_hasta`
3. `alcance = 'G'` **o** (`alcance = 'P'` y `request.user` ∈ `destinatarios`)

Orden: `-destacada`, `-fecha_noticia`, `orden`.

Texto en tarjeta: `resumen` si no vacío; si no, truncar `detalle` (~200 caracteres).

---

## Regla fundamental: gestión Master

- Vistas CRUD exigen `request.user.profile.user_type == "M"`.
- Listado admin: **todas** las noticias (activas e inactivas).
- No borrado físico v1: **Desactivar** → `status = 'I'`.

---

## Pantallas — lectura

| Pantalla | URL Django | Prototipo |
|----------|------------|-----------|
| Feed | `/app/noticias/` | `noticias.html` |
| Detalle | `/app/noticias/<id>/` | — (v1 Django) |

Render: tarjetas con badge `tipo`, `<time>` de `fecha_noticia`, `titulo`, resumen. Enlaces en feed según contenido:

| Condición | Enlace en feed |
|-----------|----------------|
| Hay `detalle` | **Leer más →** (vista detalle; ahí también van enlaces interno/externo) |
| Sin `detalle` + `enlace_interno` | **Ver más →** |
| Sin `detalle` + `enlace_externo` | **Abrir enlace →** (nueva pestaña) |

Demo: datos desde `js/noticias_store.js` (misma fuente que gestión).

---

## Pantallas — gestión (Master)

Convención: **`noticia_{accion}.html`**

| Pantalla | URL Django | Prototipo |
|----------|------------|-----------|
| Listado | `/app/administracion/noticias/` | `administracion/noticia_list.html` |
| Alta | `/app/administracion/noticias/nuevo/` | `administracion/noticia_create.html` |
| Edición | `/app/administracion/noticias/<id>/editar/` | `administracion/noticia_edit.html` |
| Copiar | `/app/administracion/noticias/<id>/copiar/` | — (clona y abre edición) |
| Desactivar | `/app/administracion/noticias/<id>/desactivar/` | `administracion/noticia_delete.html` |

---

## Listado admin (`noticia_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Registros por página (default) | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | `fecha_noticia` DESC (columna 6) |
| Columna acciones | No ordenable |

### Filtros

| Filtro | Columna |
|--------|---------|
| Título | 0 — contiene |
| Tipo | 1 — exacto |
| Alcance | 2 — exacto |
| Estado | 5 — exacto |

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Título | `titulo` |
| 1 | Tipo | `tipo` |
| 2 | Alcance | `G` Global / `P` Personal |
| 3 | Visible desde | `visible_desde` |
| 4 | Visible hasta | `visible_hasta` |
| 5 | Estado | `status` |
| 6 | Fecha noticia | `fecha_noticia` |
| 7 | Acciones | Editar · Copiar · Desactivar |

### Copiar — **Conforme v1.1** (aprobación usuario 2026-06-20)

Acción en listado: **Editar · Copiar · Desactivar**.

| Aspecto | Regla |
|---------|--------|
| URL | `GET /app/administracion/noticias/<id>/copiar/` (`administration:noticia_copy`) |
| Efecto | Clona el registro como **noticia nueva** (no modifica el original) |
| Campos copiados | Contenido, fechas, alcance, `status`, `destacada`, `orden`, enlaces |
| Título | Sufijo ` (copia)` (truncado si supera 200 caracteres) |
| Destinatarios | Se copian **tal cual** del original (M2M) |
| Alcance **Personal** | Tras copiar, redirige a **Editar** para cambiar destinatarios u otros campos antes de guardar |
| Auditoría | `created_by` / `updated_by` = Master que copia |
| Tras copiar | Redirect a edición del clon + modal éxito |

**Caso de uso:** plantillas similares (bienvenida, primeros pasos) donde solo cambia el usuario destinatario.

Implementación: `duplicate_noticia()` en `noticia_helpers.py` · vista `noticia_copy`.

### Badges

| Campo | Valor | Clase |
|-------|-------|-------|
| Alcance | Global | `badge badge-type-user` |
| Alcance | Personal | `badge badge-process` |
| Estado | Activo | `badge badge-active` |
| Estado | Inactivo | `badge badge-inactive` |

Cabecera: **+ Nueva noticia** → `noticia_create.html`.

---

## Alta / edición (`noticia_create.html`, `noticia_edit.html`)

### Campos obligatorios

| Campo | Control | Validación |
|-------|---------|------------|
| `alcance` | radio `G` / `P` | — |
| `tipo` | text, maxlength 20 | No vacío |
| `titulo` | text, maxlength 200 | No vacío |
| `detalle` | textarea | Opcional — si vacío, no hay vista detalle ni enlace «Leer más» |
| `fecha_noticia` | date | Requerido |
| `visible_desde` | date | Requerido |
| `visible_hasta` | date | ≥ `visible_desde` |
| `status` | select A/I | Default `A` en alta |

### Campos opcionales

| Campo | Control |
|-------|---------|
| `resumen` | text, maxlength 300 |
| `destinatarios` | `<select multiple>` | Obligatorio ≥1 si `alcance = P` |
| `destacada` | checkbox |
| `orden` | number ≥ 0 |
| `enlace_interno` | text |
| `enlace_externo` | url |

Si `alcance = G`, ocultar destinatarios y enviar lista vacía.

---

## Desactivar (`noticia_delete.html`)

- Muestra resumen de la noticia (título, tipo, vigencia).
- Acción: `status → I` (no DELETE).
- User ya no la ve en el feed; Master puede reactivar editando.

---

## Store demo (prototipo)

| Archivo | Rol |
|---------|-----|
| `js/noticias_store.js` | Seed + `localStorage`; API `getVisibleForUser`, `getAll`, `save`, `update`, `deactivate` |
| `js/noticias_feed.js` | Render en `noticias.html` |
| `administracion/js/noticia_*.js` | CRUD demo |

---

## Escenarios de prueba

| # | Escenario | Resultado |
|---|-----------|-----------|
| 1 | Noticia global activa en rango | Visible para cualquier User |
| 2 | Noticia personal | Solo destinatarios |
| 3 | Fuera de rango de fechas | No visible en feed |
| 4 | `status = I` | No visible; sí en listado admin |
| 5 | User intenta `/admin/noticias/` | 403 |
| 6 | Master crea y User abre Noticias | Aparece en feed |
| 7 | Master **Copiar** noticia personal | Clon con mismos destinatarios; edición para cambiar usuario |

---

## Registro

| Fecha | Evento |
|-------|--------|
| 2026-06-16 | Diseño prototipo + reglas — Conforme |
| 2026-06-20 | Implementación Django v1 — Conforme |
| 2026-06-20 | Acción **Copiar** (destinatarios copiados; edición para ajustar) — **Conforme v1.1**, confirmado y aprobado por usuario |
| 2026-06-20 | **Primer acceso → Noticias** (integración con `apps.security`) — **Conforme v1.2**, confirmado y aprobado por usuario |

---

*Documento de reglas UI/UX — módulo Noticias BAKEBUDGE.*
