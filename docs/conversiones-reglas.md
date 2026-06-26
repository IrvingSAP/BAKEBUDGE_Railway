# Reglas del módulo Conversiones — `ConversionUnidad` (`apps.catalog`)

**Estado:** **Conforme** — reglas y diseño prototipo aprobados (2026-06-16).

Convenciones de UI, listado y CRUD para las **reglas de conversión de unidades** del usuario (recetas → unidad base del producto).

**Templates Django:** `apps/catalog/templates/catalog/conversiones/` · **URL:** `/app/conversiones/`  
**Modelo:** [`BAKEBUDGE_MODELS.md#conversionunidad`](BAKEBUDGE_MODELS.md#conversionunidad)  
**Relacionado:** [`productos-reglas.md`](productos-reglas.md), [`categorias-reglas.md`](categorias-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| CRUD de `ConversionUnidad` del owner | CRUD de `Producto` o `ProductCategory` |
| Conversiones genéricas (`producto=null`) | Unidades globales predefinidas del sistema |
| Conversiones por producto | Cálculo en recetas (servicio futuro) |

Acceso menú: **Catálogo base → Conversiones de unidad**.

---

## Semántica del `factor`

```
1 × desde_unidad  =  factor × hacia_unidad
```

Ejemplo: `desde_unidad = "taza"`, `hacia_unidad = "g"`, `factor = 120` → 1 taza = 120 g.

---

## Regla fundamental: datos del usuario conectado

- Listado: `ConversionUnidad.objects.filter(owner=request.user)`
- Crear: `owner=request.user`; si hay `producto`, validar `producto.owner == request.user`
- Editar/eliminar: `get_object_or_404(ConversionUnidad, pk=pk, owner=request.user)`

Los valores **`hacia_unidad` distintos** del owner alimentan el selector `Producto.unidad_base` en alta/edición de productos.

---

## Pantallas del módulo

Convención: **`conversion_{accion}.html`**

| Pantalla | URL Django (futuro) | Prototipo |
|----------|---------------------|-----------|
| Listado | `/app/catalogo/conversiones/` | `conversiones/conversion_list.html` |
| Alta | `/app/catalogo/conversiones/nuevo/` | `conversiones/conversion_create.html` |
| Ayuda alta | `…/nuevo/ayuda/` | `conversiones/conversion_create_help.html` |
| Edición | `/app/catalogo/conversiones/<id>/editar/` | `conversiones/conversion_edit.html` |
| Ayuda edición | `…/editar/ayuda/` | `conversiones/conversion_edit_help.html` |
| Eliminación | `/app/catalogo/conversiones/<id>/eliminar/` | `conversiones/conversion_delete.html` |

---

## Listado (`conversion_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Default página | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | Etiqueta/nombre (col. 0) A→Z |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada — filtros propios |

### Filtros

| Filtro | Columna | Comportamiento |
|--------|---------|----------------|
| **Etiqueta / unidad** | 0, 2 | Contiene (nombre o `desde_unidad`) |
| **Alcance** | 1 | Genérica / Por producto / Todos |
| **Hacia unidad** | 3 | Exacto; «Todas» = sin filtro |

Botón **Limpiar filtros**.

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Etiqueta | `ConversionUnidad.nombre` o «desde → hacia» |
| 1 | Alcance | `producto` — «Genérica» o `Producto.nombre` |
| 2 | Desde | `ConversionUnidad.desde_unidad` |
| 3 | Hacia | `ConversionUnidad.hacia_unidad` |
| 4 | Factor | `ConversionUnidad.factor` |
| 5 | Equivalencia | UI: «1 {desde} = {factor} {hacia}» |
| 6 | Acciones | Editar · Eliminar |

> Sin columna `status` — el modelo no usa estado.

### Cabecera

| Control | Destino |
|---------|---------|
| **+ Nueva conversión** | `conversion_create.html` |

---

## Alta (`conversion_create.html`)

### Campos obligatorios

| Campo | Modelo | Regla |
|-------|--------|-------|
| `desde_unidad` | `ConversionUnidad.desde_unidad` | Obligatorio. Texto libre, máx. 20 (taza, cdta, oz…). |
| `hacia_unidad` | `ConversionUnidad.hacia_unidad` | Obligatorio. Máx. 20. Si hay `producto`, debe = `producto.unidad_base`. |
| `factor` | `ConversionUnidad.factor` | Obligatorio. Numérico **> 0**. `DecimalField(12,6)`. |

### Campos opcionales

| Campo | Regla |
|-------|-------|
| `producto` | FK opcional. Vacío = **genérica** del owner. |
| `nombre` | Etiqueta UI, máx. 50. |
| `notas` | Texto libre — origen de la medida, referencia. |

### Validación (orden)

1. `desde_unidad` no vacío  
2. `hacia_unidad` no vacío  
3. `factor` > 0  
4. Si `producto` seleccionado → `hacia_unidad == producto.unidad_base`  
5. Unicidad demo: no duplicar `(owner, producto, desde_unidad)`  
6. Persistir con `owner=request.user`  

### Acciones

| Botón | Comportamiento |
|-------|----------------|
| **Guardar conversión** | Valida y guarda |
| **Cancelar** | Vuelve al listado |

---

## Edición (`conversion_edit.html`)

Mismas reglas que alta. Campo `pk` solo lectura.

---

## Eliminación (`conversion_delete.html`)

| Regla | Detalle |
|-------|---------|
| Confirmación | Modal / pantalla confirmación |
| Impacto | Si se usa en recetas, el costo puede quedar sin calcular hasta nueva regla |
| Producto CASCADE | Al eliminar producto se eliminan sus conversiones ligadas |

---

## Tipos de conversión

| `producto` | Alcance |
|------------|---------|
| **null** | Genérica — aplica si `hacia_unidad` = `producto.unidad_base` y coincide `desde_unidad` |
| **Con producto** | Solo ese insumo; `hacia_unidad` = `producto.unidad_base` |

---

## Mensajes al usuario

Errores, éxito y avisos → **modal global** (`BakeBudgeModal`). No `alert()`.

Mensajes clave:

- «El factor debe ser un número mayor que 0.»
- «La unidad destino debe coincidir con la unidad base del producto seleccionado ({unidad}).»
- «Ya existe una conversión con esa unidad de origen para este alcance.»

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `apps/catalog/templates/catalog/conversiones/ o apps/catalog/static/catalog/conversion_list.html` | Listado |
| `apps/catalog/templates/catalog/conversiones/ o apps/catalog/static/catalog/js/conversion_list.js` | DataTables + filtros |
| `apps/catalog/templates/catalog/conversiones/ o apps/catalog/static/catalog/js/conversion_create.js` | Validación alta |
| `apps/catalog/templates/catalog/conversiones/ o apps/catalog/static/catalog/js/conversion_edit.js` | Validación edición |
