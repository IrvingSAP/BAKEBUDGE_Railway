# Reglas del módulo Producción — `OrdenProduccion` (`apps.production`)

**Estado:** **Conforme** — diseño aprobado; **Django v1 implementado** (2026-06-16).

**Implementación Django:** `/app/produccion/` — [`produccion-checklist-conforme.md`](produccion-checklist-conforme.md) bloque F.

Convenciones de UI, listado, planificación y ciclo de vida de **órdenes de producción** del usuario.

**Templates Django:** `apps/production/templates/production/` · **URL:** `/app/produccion/`  
**Modelo:** [`BAKEBUDGE_MODELS.md#ordenproduccion`](BAKEBUDGE_MODELS.md#ordenproduccion)  
**Relacionado:** [`recetas-reglas.md`](recetas-reglas.md), [`recetaversion-reglas.md`](recetaversion-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md), [`flujos.md`](flujos.md#5-orden-de-producción)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| CRUD planificación `OrdenProduccion` | Descuento de inventario / stock |
| Ciclo de estados borrador → en_proceso → completada/cancelada | `costo_real` vs estimado (**Pendiente** — no prioritario; v1 usa solo `costo_estimado`) |
| Vista detalle con ingredientes/pasos escalados por lotes | Reapertura de órdenes cerradas |
| Override precio al completar | |

Acceso menú: **Producción** → `/app/produccion/` (`production:orden_list`).

---

## Regla fundamental: datos del usuario conectado

- Listado: `OrdenProduccion.objects.filter(owner=request.user).select_related("receta_version__receta")`
- Crear: `owner=request.user`; validar `receta_version.receta.owner == owner`
- Detalle/editar: `get_object_or_404(OrdenProduccion, pk=pk, owner=request.user)`

---

## Pantallas del módulo

Convención: **`orden_{accion}.html`**

| Pantalla | URL Django | Prototipo |
|----------|---------------------|-----------|
| Listado | `/app/produccion/` | `produccion/orden_list.html` |
| Alta | `/app/produccion/nueva/` | `produccion/orden_create.html` |
| Ayuda alta | `…/nueva/ayuda/` | `produccion/orden_create_help.html` |
| Edición | `/app/produccion/<id>/editar/` | `produccion/orden_edit.html` |
| Ayuda edición | `…/editar/ayuda/` | `produccion/orden_edit_help.html` |
| Detalle / ejecución | `/app/produccion/<id>/` | `produccion/orden_detail.html` |

---

## Listado (`orden_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Default página | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | Fecha programada (col. 5) desc |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada — filtros propios |

### Filtros

| Filtro | Columna | Comportamiento |
|--------|---------|----------------|
| **Código / receta** | 0 + 1 | Contiene, tiempo real |
| **Estado** | 4 | Exacto sobre etiqueta badge |

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Código | `codigo` |
| 1 | Receta | `receta_version.receta.nombre` + «vN» |
| 2 | Lotes | `cantidad_lotes` |
| 3 | Costo estimado | `costo_estimado` |
| 4 | Estado | `estado` |
| 5 | Fecha | `fecha_programada` o `created_at` |
| 6 | Acciones | Ver · Editar (solo borrador) |

### Cabecera

Botón **+ Nueva orden** → `orden_create.html`.

---

## Alta (`orden_create.html`)

| Campo | Regla |
|-------|-------|
| Receta | Select obligatorio; solo recetas del owner |
| Versión | Default `version_actual`; readonly si una sola opción |
| `cantidad_lotes` | Obligatorio, numérico **> 0**; default `1` |
| `fecha_programada` | Opcional; DateField |
| `notas` | Opcional |

**Preview en vivo (demo):** `costo_estimado = lotes × receta_version.costo_total`, `rendimiento_esperado = lotes × rendimiento_cantidad`.

**Entrada desde recetas:** `?receta_id=N` preselecciona receta y versión vigente.

**Avisos (no bloqueantes en demo):** receta en `P` o `costo_total = 0`.

Al guardar: estado `borrador`, `codigo` auto (ej. `OP-2026-009`).

---

## Edición (`orden_edit.html`)

Solo órdenes en estado **`borrador`**.

| Editable | No editable |
|----------|-------------|
| `cantidad_lotes`, `fecha_programada`, `notas` | `receta_version` (en v1: recrear orden si cambia versión) |
| Recalculo `costo_estimado` al cambiar lotes | `codigo`, `estado` |

Redirigir a detalle si estado ≠ `borrador`.

---

## Detalle / ejecución (`orden_detail.html`)

Vista principal del ciclo operativo. Muestra:

1. Cabecera orden: código, estado, fechas ciclo
2. Planificación: receta, versión, lotes, rendimiento esperado
3. Panel costos: `costo_estimado`, costo/porción orden
4. Ingredientes escalados (`cantidad × cantidad_lotes`)
5. Pasos de la versión (sin escalar)
6. Costos indirectos de referencia

### Acciones por estado

| Estado | Acciones |
|--------|----------|
| `borrador` | Editar · **Iniciar producción** · Cancelar |
| `en_proceso` | **Completar** (modal precio) · Cancelar |
| `completada` | Solo lectura; nota analytics generado |
| `cancelada` | Solo lectura |

### Transiciones (modal `BakeBudgeModal`)

```
borrador → en_proceso   (Iniciar — congela costo_estimado)
borrador → cancelada    (Cancelar — confirmación)
en_proceso → completada (Completar — precio opcional)
en_proceso → cancelada  (Cancelar — confirmación)
```

### Completar orden — precio de venta

| Campo | Regla |
|-------|-------|
| `precio_venta_unitario` | Default `receta_version.precio_venta_sugerido`; editable |
| `precio_venta_total` | Alternativa opcional |
| Botón «Usar precio sugerido» | Restaura default de versión |

Django: dispara `record_production_analytics` al pasar a `completada`. Canceladas **no** generan analytics.

---

## Cálculo de costos

```
costo_estimado = cantidad_lotes × receta_version.costo_total
rendimiento_esperado = cantidad_lotes × receta_version.rendimiento_cantidad
costo_por_porcion_orden = costo_estimado / rendimiento_esperado
```

| Momento | Comportamiento |
|---------|----------------|
| `borrador` | Recalculable al guardar o cambiar lotes |
| `en_proceso` | Snapshot congelado en `costo_estimado` |
| `completada` / `cancelada` | Valores históricos inmutables |

---

## Enlaces cruzados

| Origen | Destino |
|--------|---------|
| `receta_list.html` | **Producir** → `orden_create.html?receta_id=` |
| `receta_edit.html` | Enlace «Nueva orden» (futuro) |
| `dashboard.html` | Tabla reciente → `orden_detail.html?id=` |
| `orden_detail.html` | Receta → `receta_edit.html`; versión → `recetaversion_edit.html` |

---

## Reglas de negocio (referencia)

1. `cantidad_lotes` > 0.
2. Solo recetas **A** recomendadas para órdenes nuevas; aviso si `P`.
3. `codigo` único por owner; secuencial al crear.
4. No editar `receta_version` ni `cantidad_lotes` en `en_proceso`, `completada`, `cancelada`.
5. `receta_version` con órdenes → PROTECT (no borrar versión).
6. Varias órdenes pueden usar la misma versión el mismo día.

---

## Limitaciones del prototipo

1. Demo completo de detalle/ejecución en **`?id=1`** (Brownie completada) y **`?id=4`** (borrador editable); otras filas del listado con datos estáticos.
2. Selectores de receta: lista fija en JS.
3. Transiciones de estado: modal demo; no persiste entre recargas.
4. Ingredientes escalados solo en demo Brownie (`receta_id=1`).

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `produccion/orden_list.html` | Listado + filtros |
| `produccion/js/orden_list.js` | DataTables + filtros |
| `produccion/orden_create.html` | Alta planificación |
| `produccion/js/orden_create.js` | Preview costo + validación |
| `produccion/orden_edit.html` | Edición borrador |
| `produccion/orden_detail.html` | Ejecución + estados |
| `produccion/js/orden_detail.js` | Demo Brownie + transiciones |
| `produccion/css/produccion.css` | Estilos módulo |
