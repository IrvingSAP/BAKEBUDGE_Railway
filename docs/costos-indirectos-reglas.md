# Reglas del módulo Costos indirectos — `CostoIndirecto` (`apps.catalog`)

**Estado:** **Conforme** — diseño y reglas aprobados ([`recetas-checklist-conforme.md`](recetas-checklist-conforme.md)).

Convenciones de UI, listado y CRUD del **catálogo de gastos indirectos** del usuario (gas, luz, mano de obra, empaque, etc.).

**Templates Django:** `apps/catalog/templates/catalog/costos_indirectos/` · **URL:** `/app/costos-indirectos/`  
**Modelo:** [`BAKEBUDGE_MODELS.md#costoindirecto`](BAKEBUDGE_MODELS.md#costoindirecto)  
**Relacionado:** [`recetaversion-reglas.md`](recetaversion-reglas.md), [`productos-reglas.md`](productos-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| CRUD de `CostoIndirecto` del owner | Asignación a recetas (`RecetaCostoIndirecto` — ver formulación) |
| Catálogo libre sin categorías fijas | Prorrateo automático mensual |

Acceso menú: **Catálogo base → Costos indirectos**.

---

## Regla fundamental: datos del usuario conectado

- Listado: `CostoIndirecto.objects.filter(owner=request.user)`
- Crear: `owner=request.user`
- Editar/eliminar: `get_object_or_404(CostoIndirecto, pk=pk, owner=request.user)`
- Selector en recetas: solo `status = A` (`usable_en_recetas`)

---

## Pantallas del módulo

Convención: **`costoindirecto_{accion}.html`**

| Pantalla | URL Django (futuro) | Prototipo |
|----------|---------------------|-----------|
| Listado | `/app/catalogo/costos-indirectos/` | `costos_indirectos/costoindirecto_list.html` |
| Alta | `/app/catalogo/costos-indirectos/nuevo/` | `costos_indirectos/costoindirecto_create.html` |
| Ayuda alta | `…/nuevo/ayuda/` | `costos_indirectos/costoindirecto_create_help.html` |
| Edición | `/app/catalogo/costos-indirectos/<id>/editar/` | `costos_indirectos/costoindirecto_edit.html` |
| Ayuda edición | `…/editar/ayuda/` | `costos_indirectos/costoindirecto_edit_help.html` |
| Eliminación | `/app/catalogo/costos-indirectos/<id>/eliminar/` | `costos_indirectos/costoindirecto_delete.html` |

---

## Listado (`costoindirecto_list.html`)

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
| **Estado** | 4 | Exacto sobre etiqueta badge |
| **Unidad cobro** | 2 | Exacto; «Todas» = sin filtro |

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Nombre | `CostoIndirecto.nombre` |
| 1 | Costo / unidad | `costo_por_unidad` + moneda perfil |
| 2 | Unidad cobro | `unidad_cobro` |
| 3 | Tarifa ref. | UI: «$ X / {unidad_cobro}» |
| 4 | Estado | `status` |
| 5 | Acciones | Editar · Eliminar |

### Cabecera

| Control | Destino |
|---------|---------|
| **+ Nuevo costo indirecto** | `costoindirecto_create.html` |

---

## Alta (`costoindirecto_create.html`)

### Campos obligatorios

| Campo | Modelo | Regla |
|-------|--------|-------|
| `nombre` | `CostoIndirecto.nombre` | Obligatorio. Trim. Máx. 50. |
| `unidad_cobro` | `CostoIndirecto.unidad_cobro` | Obligatorio. Valores v1: `hora`, `minuto`, `lote`, `porcion`, `mes`, `fijo` |
| `costo_por_unidad` | `CostoIndirecto.costo_por_unidad` | Obligatorio. Numérico **> 0** |

### Campos opcionales

| Campo | Modelo |
|-------|--------|
| `notas` | `CostoIndirecto.notas` |

### Estado en alta

| Campo | Default |
|-------|---------|
| `status` | `P` (En proceso) |

Botón **Guardar y marcar activo** → `status = A`.

---

## Edición (`costoindirecto_edit.html`)

Mismas reglas que alta. `pk` solo lectura.

---

## Eliminación (`costoindirecto_delete.html`)

| Regla | Detalle |
|-------|---------|
| `PROTECT` | No eliminar si está en `RecetaCostoIndirecto` |
| Preferencia | **Inactivar** (`status=I`) si tiene historial en recetas |

---

## Uso en recetas

En formulación (`recetaversion_edit.html`), el selector carga:

```python
CostoIndirecto.objects.filter(owner=request.user, status="A")
```

`costo_linea = cantidad × costo_por_unidad` en `RecetaCostoIndirecto`.

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `costos_indirectos/costoindirecto_list.html` | Listado |
| `costos_indirectos/js/costoindirecto_list.js` | DataTables + filtros |
| `costos_indirectos/js/costoindirecto_create.js` | Validación alta |
| `costos_indirectos/js/costoindirecto_edit.js` | Demo + validación edición |
| `costos_indirectos/js/costoindirecto_delete.js` | Demo PROTECT |
