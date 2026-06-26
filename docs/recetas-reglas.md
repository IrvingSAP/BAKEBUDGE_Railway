# Reglas del módulo Recetas — `Receta` (`apps.recipes`)

**Estado:** **Conforme** — diseño aprobado; **Django v1 implementado** (2026-06-16).

**Implementación Django:** `/app/recetas/` — [`recetas-checklist-conforme.md`](recetas-checklist-conforme.md) bloque F.

Convenciones de UI, listado y CRUD de la **cabecera de receta** del usuario. La formulación (`RecetaVersion`: ingredientes, pasos, costos, precio) está en [`recetaversion-reglas.md`](recetaversion-reglas.md).

**Templates Django:** `apps/recipes/templates/recipes/` · **URL:** `/app/recetas/`  
**Modelos:** [`BAKEBUDGE_MODELS.md#receta`](BAKEBUDGE_MODELS.md#receta), [`RecetaVersion`](BAKEBUDGE_MODELS.md#recetaversion)  
**Relacionado:** [`recetaversion-reglas.md`](recetaversion-reglas.md), [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md), [`productos-reglas.md`](productos-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md)

---

## Alcance

| Este módulo (`recetas/`) | Submódulos relacionados |
|--------------------------|-------------------------|
| CRUD cabecera `Receta` | Formulación → [`recetaversion-reglas.md`](recetaversion-reglas.md) |
| Alta con **versión inicial v1** (rendimiento en create) | Catálogo indirectos → [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md) |
| Listado con métricas de `version_actual` | Producción → [`produccion-reglas.md`](produccion-reglas.md) |
| Estado P / A / I | |

Acceso menú: **Recetas** → `/app/recetas/` (`recipes:receta_list`).

---

## Regla fundamental: datos del usuario conectado

- Listado: `Receta.objects.filter(owner=request.user).select_related("version_actual")`
- Crear: `owner=request.user`; al guardar crear `RecetaVersion` v1 y asignar `version_actual`
- Editar/eliminar: `get_object_or_404(Receta, pk=pk, owner=request.user)`

---

## Pantallas del módulo

Convención: **`receta_{accion}.html`**

| Pantalla | URL Django (futuro) | Prototipo |
|----------|---------------------|-----------|
| Listado | `/app/recetas/` | `recetas/receta_list.html` |
| Alta | `/app/recetas/nuevo/` | `recetas/receta_create.html` |
| Ayuda alta | `…/nuevo/ayuda/` | `recetas/receta_create_help.html` |
| Edición | `/app/recetas/<id>/editar/` | `recetas/receta_edit.html` |
| Ayuda edición | `…/editar/ayuda/` | `recetas/receta_edit_help.html` |
| Eliminación | `/app/recetas/<id>/eliminar/` | `recetas/receta_delete.html` |

---

## Listado (`receta_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Default página | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | Nombre (col. 0) A→Z |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada — filtros propios |

### Filtros

| Filtro | Columna | Comportamiento |
|--------|---------|----------------|
| **Nombre** | 0 | Contiene, tiempo real |
| **Estado** | 6 | Exacto sobre etiqueta badge |

Botón **Limpiar filtros**.

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Receta | `Receta.nombre` |
| 1 | Versión | `Receta.version_actual.numero_version` → «vN» |
| 2 | Rendimiento | `version_actual.rendimiento_cantidad` + `rendimiento_unidad` |
| 3 | Costo total | `version_actual.costo_total` |
| 4 | Costo / porción | `version_actual.costo_por_porcion` |
| 5 | Precio sugerido | `version_actual.precio_venta_sugerido` |
| 6 | Estado | `Receta.status` |
| 7 | Acciones | Editar · Formulación · Producir · Eliminar |

Moneda según `UserProfile.moneda` (demo: COP).

### Badges estado (`Receta.status`)

| Código | Etiqueta | Clase CSS |
|--------|----------|-----------|
| `A` | Activo | `badge badge-active` |
| `P` | En proceso | `badge badge-draft` |
| `I` | Inactivo | `badge badge-inactive` |

### Cabecera

| Control | Destino |
|---------|---------|
| **+ Nueva receta** | `receta_create.html` |

---

## Alta (`receta_create.html`)

Al crear se genera `Receta` (`status=P` por defecto) + `RecetaVersion` **v1** con rendimiento.

### Campos obligatorios — cabecera

| Campo | Modelo | Regla |
|-------|--------|-------|
| `nombre` | `Receta.nombre` | Obligatorio. Trim. Máx. 100. |

### Campos obligatorios — versión inicial v1

| Campo | Modelo | Regla |
|-------|--------|-------|
| `rendimiento_cantidad` | `RecetaVersion.rendimiento_cantidad` | Obligatorio. Numérico **> 0**. Default sugerido: `1`. |
| `rendimiento_unidad` | `RecetaVersion.rendimiento_unidad` | Obligatorio. Texto libre, máx. 30. Default: `porciones`. |

### Campos opcionales

| Campo | Modelo |
|-------|--------|
| `descripcion_corta` | `Receta.descripcion_corta` (255) |
| `notas` | `Receta.notas` |
| `imagen` | `Receta.imagen` — file input; demo sin subida real |

### Estado en alta

| Campo | Default |
|-------|---------|
| `status` | `P` (En proceso) |

Botón **Guardar y marcar activo** → fuerza `status=A`.

### Validación (orden)

1. `nombre` no vacío  
2. `rendimiento_cantidad` > 0  
3. `rendimiento_unidad` no vacío  
4. Persistir `Receta` + `RecetaVersion` v1 + `version_actual`  

---

## Edición (`receta_edit.html`)

| Sección | Contenido |
|---------|-----------|
| Cabecera | `nombre`, `descripcion_corta`, `notas`, `status`, `imagen` |
| Versión vigente | Stats readonly + enlaces a formulación / historial / nueva versión |
| Formulación | → `apps/recipes/templates/recipes/version/recetaversion_edit.html` |

Rendimiento, ingredientes y pasos se editan en **Formulación** (`recetaversion_edit.html`), no en la cabecera.

---

## Eliminación (`receta_delete.html`)

| Regla | Detalle |
|-------|---------|
| Preferencia | **Inactivar** (`status=I`) si hay historial o producción |
| Borrado físico | Solo si sin órdenes de producción (Django futuro) |
| CASCADE | Eliminar receta elimina `RecetaVersion` e hijos |

---

## Mensajes al usuario

Modal global (`BakeBudgeModal`). No `alert()`.

---

## Reglas de negocio (referencia modelo)

1. Solo recetas **A** en órdenes de producción nuevas.  
2. Costos en listado vienen de `version_actual`, no de `Receta`.  
3. Cambio de formulación mayor → nueva versión (servicio Django).  
4. Ingredientes solo de productos **A** del owner.

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `recetas/receta_list.html` | Listado |
| `recetas/js/receta_list.js` | DataTables + filtros |
| `recetas/js/receta_create.js` | Validación alta |
| `recetas/js/receta_edit.js` | Validación edición cabecera |
| `recetas/version/` | Submódulo `RecetaVersion` — [`recetaversion-reglas.md`](recetaversion-reglas.md) |
| — | Checklist Conforme — [`recetas-checklist-conforme.md`](recetas-checklist-conforme.md) |
