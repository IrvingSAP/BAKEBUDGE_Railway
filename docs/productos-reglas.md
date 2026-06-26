# Reglas del módulo Productos — `apps.catalog`

**Estado:** **Conforme** — reglas y diseño prototipo aprobados (2026-06-16).

Convenciones de UI, listado y CRUD para el catálogo de **insumos** (`Producto`).

**Templates Django:** `apps/catalog/templates/catalog/productos/` · **URL:** `/app/productos/`  
**Implementación Django:** `apps.catalog`  
**Relacionado:** [`categorias-reglas.md`](categorias-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md), [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#producto), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye (otras apps) |
|---------|-------------------------|
| Listado y CRUD de `Producto` | CRUD de `ProductCategory` — [`categorias-reglas.md`](categorias-reglas.md) |
| — | Recetas, producción, analytics |
| — | `ConversionUnidad` — [`conversiones-reglas.md`](conversiones-reglas.md) |
| — | CRUD global de monedas |

---

## Regla fundamental: datos del usuario conectado

Todo producto y categoría mostrado o editable pertenece a **`request.user`**:

- Listado: `Producto.objects.filter(owner=request.user)`
- Categorías en selectores: `ProductCategory.objects.filter(owner=request.user, status="A")`
- Crear producto: `owner=request.user` y `categoria.owner == request.user`
- Editar/eliminar: `get_object_or_404(Producto, pk=pk, owner=request.user)`

Ver [`dashboard-reglas.md#regla-fundamental-datos-del-usuario-conectado`](dashboard-reglas.md#regla-fundamental-datos-del-usuario-conectado).

---

## Pantallas del módulo

Convención de nombres: **`producto_{accion}.html`** (prefijo = app en singular). Ver [`ui-ux.md`](ui-ux.md#nombres-de-archivos-html-zona-app).

| Pantalla | URL Django (futuro) | Prototipo |
|----------|---------------------|-----------|
| Listado | `/app/productos/` | `productos/producto_list.html` |
| Alta | `/app/productos/nuevo/` | `productos/producto_create.html` |
| Ayuda alta | `/app/productos/nuevo/ayuda/` | `productos/producto_create_help.html` |
| Edición | `/app/productos/<id>/editar/` | `productos/producto_edit.html` |
| Ayuda edición | `/app/productos/<id>/editar/ayuda/` | `productos/producto_edit_help.html` |
| Eliminación | `/app/productos/<id>/eliminar/` | `productos/producto_delete.html` |

Todas extienden layout `/app/` (sidebar, Usuario, modal global).

---

## Listado de productos (`producto_list.html`)

### DataTables — configuración obligatoria

Seguir [`ui-ux.md`](ui-ux.md#tablas-datatables) y el [manual DataTables](https://datatables.net/manual/). Inicialización vía [`BakeBudgeDataTables`](../apps/core/static/js/datatables-init.js) (no repetir opciones en cada pantalla).

| Parámetro | Valor |
|-----------|--------|
| **Registros por página (default)** | **10** |
| **Opciones de cantidad** | **10 · 20 · 50** |
| Idioma | Español (`es-ES`) |
| Orden inicial | Nombre (A→Z), columna 0 |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada en productos — se usan filtros propios (`layout.topEnd: null`) |

Implementación prototipo: `apps/catalog/static/catalog/js/producto_list.js` → `BakeBudgeDataTables.init(...)`.

### Filtros de búsqueda (obligatorios)

Barra sobre la tabla con tres controles independientes:

| Filtro | Tipo | Columna | Comportamiento |
|--------|------|---------|----------------|
| **Nombre** | `<input type="search">` | 0 | Coincidencia parcial (contiene), en tiempo real |
| **Categoría** | `<select>` | 1 | Coincidencia exacta; opción «Todas» = sin filtro |
| **Estado** | `<select>` | 4 | Coincidencia exacta sobre etiqueta visible; «Todos» = sin filtro |

Botón **Limpiar filtros** restablece los tres campos y la tabla.

En Django: mismos filtros vía querystring (`?nombre=&categoria=&status=`) o filtrado server-side en fase posterior; en v1 el queryset ya viene acotado al owner y DataTables filtra en cliente.

### Columnas de la tabla

| # | Columna | Origen modelo | Notas |
|---|---------|---------------|-------|
| 0 | Nombre | `Producto.nombre` | |
| 1 | Categoría | `Producto.categoria.nombre` | FK [`ProductCategory`](BAKEBUDGE_MODELS.md#productcategory) |
| 2 | Unidad base | `Producto.unidad_base` | Desde `ConversionUnidad.hacia_unidad` del owner |
| 3 | Costo / unidad | `Producto.costo_por_unidad_base` | Formato moneda según `UserProfile.moneda` |
| 4 | Estado | `Producto.status` | Badge según tabla abajo |
| 5 | Acciones | — | Enlace «Editar» |

### Badges de estado (`Producto.status`)

| Código | Etiqueta UI | Clase CSS prototipo |
|--------|-------------|---------------------|
| `A` | Activo | `badge badge-active` |
| `P` | En proceso | `badge badge-draft` |
| `I` | Inactivo | `badge badge-inactive` |

Listado muestra **todos** los estados por defecto; el filtro permite acotar.

### Acciones de cabecera

| Control | Destino |
|---------|---------|
| **+ Nuevo producto** | Formulario alta |
| **Editar** (por fila) | Formulario edición del producto |

### Mensajes al usuario

Errores de validación, éxito al guardar y avisos → **modal global** (`BakeBudgeModal` / `message_modal` + `error_tipo`). No `alert()`.

---

## Alta de producto (`producto_create.html`)

Reglas del proceso de **creación** de insumos. Aplican al prototipo y a la vista Django `producto_create`.

### Campos obligatorios

Los cuatro campos siguientes **deben completarse** antes de guardar. Si falta alguno o no cumple la validación, mostrar error vía **modal global** (`BakeBudgeModal.showError` / `message_modal` + `error_tipo=ER`).

| Campo HTML | Modelo | Regla |
|------------|--------|-------|
| `nombre` | `Producto.nombre` | Obligatorio. Texto no vacío (trim). Máx. 150 caracteres. |
| `categoria` | `Producto.categoria` | Obligatorio. FK `ProductCategory` activa del mismo `owner`. Opción vacía no válida. |
| `unidad_base` | `Producto.unidad_base` | Obligatorio. Valor ∈ `hacia_unidad` distintos de `ConversionUnidad` del owner. |
| `costo_por_unidad_base` | `Producto.costo_por_unidad_base` | Obligatorio. Numérico **> 0**. No negativo, no cero, no vacío. |

### Campo `costo_por_unidad_base` — validación numérica

| Regla | Detalle |
|-------|---------|
| Tipo | `DecimalField(12,4)` — en HTML `type="number"`, `step="0.0001"` |
| Mínimo | **> 0** (estrictamente mayor que cero) |
| Prohibido | Valores negativos (`< 0`), cero (`= 0`) o campo vacío |
| Mensaje error (ES) | «El costo por unidad base debe ser un número mayor que 0.» |
| Moneda | Se ingresa en la moneda de `UserProfile.moneda`; sin FK en `Producto` |

**HTML (prototipo / template):**

```html
<input type="number" name="costo_por_unidad_base" step="0.0001" min="0.0001" required>
```

**Django (vista):**

```python
costo = Decimal(request.POST.get("costo_por_unidad_base", "").strip() or "0")
if costo <= 0:
    return render(request, "...", {
        "error_tipo": "ER",
        "message_modal": "El costo por unidad base debe ser un número mayor que 0.",
    })
```

### Campo `unidad_base` — origen

No es lista fija. Opciones = `ConversionUnidad.objects.filter(owner=request.user).values_list("hacia_unidad", flat=True).distinct()`.

Si no hay conversiones: deshabilitar guardado y avisar al usuario.

### Campos opcionales en alta

| Campo | Default alta |
|-------|----------------|
| `proveedor` | vacío |
| `notas` | vacío |
| `status` | `P` (En proceso) — salvo botón «Guardar y marcar activo» → `A` |

### Flujo de validación (orden)

1. `nombre` no vacío  
2. `categoria` seleccionada  
3. `unidad_base` seleccionada (catálogo ConversionUnidad)  
4. `costo_por_unidad_base` > 0  
5. Persistir con `owner=request.user`  
6. Éxito → modal `OK` o redirect a listado  

### Acciones del formulario

| Botón | Comportamiento |
|-------|----------------|
| **Guardar producto** | Valida obligatorios; guarda con `status` seleccionado (default `P`) |
| **Guardar y marcar activo** | Igual validación; fuerza `status=A` |
| **Cancelar** | Vuelve a `producto_list.html` sin guardar |

### Checklist `producto_create.html`

- [ ] Cuatro campos obligatorios marcados con `*` y `required`
- [ ] `costo_por_unidad_base`: `min="0.0001"`, sin default `0`
- [ ] Botón **Ayuda** con icono → `producto_create_help.html` (nueva pestaña)
- [ ] Validación JS + validación servidor (Django)
- [ ] Errores vía modal global, no `alert()`
- [ ] `unidad_base` poblado desde ConversionUnidad del owner
- [ ] Layout `/app/` + responsivo

---

## Edición de producto (`producto_edit.html`)

Mismas reglas de **campos obligatorios** y validación que en alta (`producto_create.html`).

| Aspecto | Regla |
|---------|--------|
| Campos obligatorios | `nombre`, `categoria`, `unidad_base`, `costo_por_unidad_base` (> 0) |
| Validación | Mismo orden y mensajes que en alta; modal global |
| Scope | Solo productos con `owner=request.user` |
| `pk` | Hidden + lectura; no editable |
| Acciones | **Guardar cambios**, **Guardar y marcar activo** (`status=A`), **Cancelar** |

**Django:** `get_object_or_404(Producto, pk=pk, owner=request.user)` — POST sin `django.forms`.

### Checklist `producto_edit.html`

- [ ] Cuatro campos obligatorios con `*` y `required`
- [ ] `costo_por_unidad_base`: `min="0.0001"`, validación JS + servidor
- [ ] Botón **Ayuda** con icono → `producto_edit_help.html` (nueva pestaña)
- [ ] `unidad_base` poblado desde ConversionUnidad; valor actual preseleccionado
- [ ] Errores vía modal global

---

## Formularios producto — otros archivos

| Archivo | Uso |
|---------|-----|
| `producto_edit.html` | Edición (mismas reglas obligatorias) |
| `producto_delete.html` | Confirmación eliminación / inactivar |

Campos del formulario (referencia rápida):

| Campo | Obligatorio |
|-------|-------------|
| `nombre` | **Sí** |
| `categoria` | **Sí** |
| `unidad_base` | **Sí** |
| `costo_por_unidad_base` | **Sí** (> 0) |
| `proveedor` | No |
| `notas` | No |
| `status` | Sí (default `P` en alta) |

- Solo HTML; procesamiento en vista sin `django.forms`.
- Select categoría: `ProductCategory` activas del owner.
- Select unidad base: `ConversionUnidad.hacia_unidad` distintos del owner.

---

## Responsivo

| Viewport | Comportamiento |
|----------|----------------|
| Desktop | Filtros en fila (3 columnas + acciones) |
| Tablet | Filtros 2 columnas |
| Móvil | Filtros apilados; tabla con scroll horizontal |

Ver [`ui-ux.md#diseño-responsivo-obligatorio`](ui-ux.md#diseño-responsivo-obligatorio).

---

## Checklist pantalla listado

- [ ] Layout `/app/` completo (sidebar, Usuario, logout, modal)
- [ ] DataTable: default **10**, opciones **10 / 20 / 50**
- [ ] Filtros: nombre, categoría, estado + limpiar
- [ ] Datos scoped a `request.user` (prototipo: demo del usuario demo)
- [ ] Badges P / A / I
- [ ] Responsivo 375 / 768 / 1140 px
- [ ] Enlace «Nuevo producto» y «Editar»

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/producto_list.html` | Listado prototipo |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/producto_create.html` | Alta — reglas obligatorios |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/js/producto_create.js` | Validación alta |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/producto_edit.html` | Edición — reglas obligatorios |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/producto_edit_help.html` | Ayuda edición |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/js/producto_edit.js` | Validación edición |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/js/producto_list.js` | Init DataTables + filtros |
| `apps/catalog/templates/catalog/productos/ o apps/catalog/static/catalog/css/productos.css` | Toolbar filtros |
| `apps/catalog/views.py` | Vistas Django (futuro) |
| `apps/catalog/templates/catalog/producto_list.html` | Template Django (futuro) |
