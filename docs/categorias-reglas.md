# Reglas del módulo Categorías — `ProductCategory` (`apps.catalog`)

**Estado:** **Conforme** — reglas y diseño prototipo aprobados (2026-06-16).

Convenciones de UI, listado y CRUD para el catálogo de **categorías de producto** del usuario.

**Templates Django:** `apps/catalog/templates/catalog/categorias/` · **URL:** `/app/categorias/`  
**Modelo:** [`BAKEBUDGE_MODELS.md#productcategory`](BAKEBUDGE_MODELS.md#productcategory)  
**Relacionado:** [`productos-reglas.md`](productos-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| CRUD de `ProductCategory` del owner | CRUD de `Producto` |
| — | `ConversionUnidad` — [`conversiones-reglas.md`](conversiones-reglas.md) |

Acceso menú: **Catálogo base → Categorías**.

---

## Regla fundamental: datos del usuario conectado

- Listado: `ProductCategory.objects.filter(owner=request.user)`
- Crear: `owner=request.user`
- Editar/eliminar: `get_object_or_404(ProductCategory, pk=pk, owner=request.user)`
- Selectores en productos: solo `status="A"` (`is_usable`)

---

## Pantallas del módulo

Convención: **`categoria_{accion}.html`**

| Pantalla | URL Django (futuro) | Prototipo |
|----------|---------------------|-----------|
| Listado | `/app/catalogo/categorias/` | `categorias/categoria_list.html` |
| Alta | `/app/catalogo/categorias/nuevo/` | `categorias/categoria_create.html` |
| Ayuda alta | `…/nuevo/ayuda/` | `categorias/categoria_create_help.html` |
| Edición | `/app/catalogo/categorias/<id>/editar/` | `categorias/categoria_edit.html` |
| Ayuda edición | `…/editar/ayuda/` | `categorias/categoria_edit_help.html` |
| Eliminación | `/app/catalogo/categorias/<id>/eliminar/` | `categorias/categoria_delete.html` |

---

## Listado (`categoria_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Registros por página (default) | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | `orden` ASC (columna 0), luego nombre |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada — filtros propios |

### Filtros

| Filtro | Columna | Comportamiento |
|--------|---------|----------------|
| **Nombre** | 1 | Contiene, tiempo real |
| **Estado** | 5 | Exacto sobre etiqueta badge |
| **Predeterminada** | 4 | «Sí» / «No» / Todas |

Botón **Limpiar filtros**.

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Orden | `ProductCategory.orden` |
| 1 | Nombre | `ProductCategory.nombre` |
| 2 | Código | `ProductCategory.codigo` |
| 3 | Color | `ProductCategory.color` — badge visual |
| 4 | Predeterminada | `ProductCategory.es_predeterminada` |
| 5 | Estado | `ProductCategory.status` |
| 6 | Acciones | Editar · Eliminar |

### Badges estado

| Código | Etiqueta | Clase CSS |
|--------|----------|-----------|
| `A` | Activo | `badge badge-active` |
| `P` | En proceso | `badge badge-draft` |
| `I` | Inactivo | `badge badge-inactive` |

### Cabecera

| Control | Destino |
|---------|---------|
| **+ Nueva categoría** | `categoria_create.html` |

---

## Alta (`categoria_create.html`)

### Campos obligatorios

| Campo | Modelo | Regla |
|-------|--------|-------|
| `nombre` | `ProductCategory.nombre` | Obligatorio. Trim. Máx. 50. **Único por owner** (case-insensitive). |
| `orden` | `ProductCategory.orden` | Obligatorio. Entero **≥ 0**. Menor = primero en listados. |
| `status` | `ProductCategory.status` | Obligatorio. Default alta: **`A`** (Activo). |

### Campos opcionales

| Campo | Regla |
|-------|-------|
| `codigo` | Máx. 30. Slug estable (`insumo`, `empaque`). Si no vacío, **único por owner**. |
| `descripcion` | Texto libre para ayuda contextual. |
| `color` | Hex `#RRGGBB` opcional; si se ingresa, validar formato. |

### No editable en alta

| Campo | Notas |
|-------|-------|
| `es_predeterminada` | Solo `True` en seeds al registrar usuario; en alta manual = `False`. |
| `owner` | Asignado en vista. |

### Validación (orden)

1. `nombre` no vacío, único (demo JS)  
2. `orden` ≥ 0  
3. `codigo` único si presente  
4. `color` hex válido si presente  
5. Persistir con `owner=request.user`  

### Acciones

| Botón | Comportamiento |
|-------|----------------|
| **Guardar categoría** | Valida y guarda |
| **Guardar y marcar activo** | Fuerza `status=A` |
| **Cancelar** | Vuelve al listado |

---

## Edición (`categoria_edit.html`)

Mismas reglas de campos que en alta.

| Aspecto | Regla |
|---------|-------|
| `pk` | Solo lectura |
| `es_predeterminada` | Solo lectura en formulario (badge) |
| Categorías `I` | No aparecen en selectores de productos nuevos |

---

## Eliminación (`categoria_delete.html`)

| Regla | Detalle |
|-------|---------|
| PROTECT | No eliminar si tiene productos asociados (`Producto.categoria`) |
| Predeterminada | Puede inactivarse (`status=I`); borrado físico solo si sin productos |
| UI | Confirmación + modal éxito/error |

Mensaje bloqueo: «No puedes eliminar esta categoría porque tiene productos asociados.»

---

## Mensajes al usuario

Errores, éxito y avisos → **modal global** (`BakeBudgeModal`). No `alert()`.

---

## Seeds al registrar usuario

| codigo | nombre | orden |
|--------|--------|-------|
| `insumo` | Insumo | 10 |
| `empaque` | Empaque | 20 |
| `decoracion` | Decoración | 30 |
| `otro` | Otro | 40 |

Todas: `es_predeterminada=True`, `status=A`.

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `apps/catalog/templates/catalog/categorias/ o apps/catalog/static/catalog/categoria_list.html` | Listado |
| `apps/catalog/templates/catalog/categorias/ o apps/catalog/static/catalog/js/categoria_list.js` | DataTables + filtros |
| `apps/catalog/templates/catalog/categorias/ o apps/catalog/static/catalog/js/categoria_create.js` | Validación alta |
| `apps/catalog/templates/catalog/categorias/ o apps/catalog/static/catalog/js/categoria_edit.js` | Validación edición |
| `apps/catalog/views.py` | Vistas Django (futuro) |
