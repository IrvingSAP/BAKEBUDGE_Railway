# Reglas del submódulo RecetaVersion — `apps.recipes`

**Estado:** **Conforme** — diseño y reglas aprobados ([`recetas-checklist-conforme.md`](recetas-checklist-conforme.md)).

Formulación versionada: rendimiento, ingredientes, pasos, costos indirectos y costos cacheados de una `RecetaVersion`. La cabecera `Receta` sigue en [`recetas-reglas.md`](recetas-reglas.md).

**Templates Django:** `apps/recipes/templates/recipes/version/` · **URL:** `/app/recetas/`  
**Modelos:** [`BAKEBUDGE_MODELS.md#recetaversion`](BAKEBUDGE_MODELS.md#recetaversion), [`RecetaIngrediente`](BAKEBUDGE_MODELS.md#recetaingrediente), [`RecetaPaso`](BAKEBUDGE_MODELS.md#recetapaso)  
**Relacionado:** [`recetas-reglas.md`](recetas-reglas.md), [`productos-reglas.md`](productos-reglas.md), [`conversiones-reglas.md`](conversiones-reglas.md), [`flujos.md`](flujos.md)

---

## Alcance

| Incluye | Fuera de alcance |
|------------------|------------------|
| Editar formulación de `version_actual` | Recálculo batch por cambio de producto |
| Ingredientes (`RecetaIngrediente`) | Edición de versiones históricas |
| **Costos indirectos** (`RecetaCostoIndirecto`) | |
| **Precio sugerido** editable (`precio_venta_sugerido`) | |
| Pasos (`RecetaPaso`) | |
| Crear nueva versión (copia + `notas_cambio`) | |
| Historial de versiones (lectura) | |

Catálogo `CostoIndirecto`: [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md) — [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md) (`/app/costos-indirectos/`).

Acceso: desde **Editar receta** → «Formulación» o listado → «Formulación».

---

## Regla fundamental: datos del usuario conectado

- Toda operación parte de `Receta` con `owner=request.user`.
- `RecetaVersion` no tiene `owner`; aislamiento vía `version.receta.owner`.
- Ingredientes: `producto.owner == receta.owner` y `producto.status = A` al agregar.
- Conversiones: `ConversionUnidad` del mismo owner para normalizar unidades.

```python
receta = get_object_or_404(Receta, pk=receta_id, owner=request.user)
version = receta.version_actual  # o get_object_or_404(RecetaVersion, pk=..., receta=receta)
```

---

## Pantallas del submódulo

Convención: **`recetaversion_{accion}.html`** en carpeta `recetas/version/`.

| Pantalla | URL Django (futuro) | Prototipo |
|----------|---------------------|-----------|
| Formulación vigente | `/app/recetas/<id>/version/` | `version/recetaversion_edit.html` |
| Ayuda formulación | `…/version/ayuda/` | `version/recetaversion_edit_help.html` |
| Nueva versión | `/app/recetas/<id>/version/nueva/` | `version/recetaversion_create.html` |
| Ayuda nueva versión | `…/nueva/ayuda/` | `version/recetaversion_create_help.html` |
| Historial | `/app/recetas/<id>/versiones/` | `version/recetaversion_list.html` |
| Detalle histórico | `/app/recetas/<id>/versiones/<n>/` | `version/recetaversion_detail.html` |

Query prototipo: `?receta_id=1` (y `&version=1` en detalle).

---

## Formulación vigente (`recetaversion_edit.html`)

Edita solo `receta.version_actual` (no versiones pasadas).

### Cabecera de pantalla

| Elemento | Origen |
|----------|--------|
| Título | `Receta.nombre` |
| Badge versión | `version_actual.numero_version` → «vN · vigente» |
| Enlaces | Historial · Nueva versión · Cabecera receta |

### Sección rendimiento

| Campo | Modelo | Regla |
|-------|--------|-------|
| `rendimiento_cantidad` | `RecetaVersion` | Obligatorio. **> 0** |
| `rendimiento_unidad` | `RecetaVersion` | Obligatorio. Máx. 30 |

Al cambiar rendimiento → recalcular `costo_por_porcion` y `precio_venta_sugerido`.

### Sección ingredientes

Tabla editable de `RecetaIngrediente` (orden por `orden`).

| Columna | Campo |
|---------|-------|
| Producto | FK `Producto` (solo **A** del owner) |
| Cantidad | `cantidad` **> 0** |
| Unidad | `unidad` (texto libre: g, taza, unidad…) |
| Costo línea | `costo_linea` (readonly, cache) |
| Acciones | Eliminar fila |

**Unicidad:** un producto por versión (`unique_together version + producto`).

**Cálculo** (servicio `cost_calculator`):

```
cantidad_normalizada → vía ConversionUnidad o unidad_base directa
costo_linea = cantidad_normalizada × producto.costo_por_unidad_base
```

Sin conversión → aviso en fila; `costo_linea` no calculable.

Botón **+ Agregar ingrediente** — fila nueva con selector de producto demo.

### Sección costos indirectos

Tabla editable de `RecetaCostoIndirecto`.

| Columna | Campo |
|---------|-------|
| Gasto indirecto | FK `CostoIndirecto` (solo **A** del owner) |
| Cantidad | `cantidad` **≥ 0** (unidades de `unidad_cobro`) |
| Unidad cobro | Solo lectura — `costo_indirecto.unidad_cobro` |
| Costo línea | `costo_linea` (readonly) = `cantidad × costo_por_unidad` |
| Notas | `notas` opcional (máx. 100) |
| Acciones | Eliminar fila |

**UI demo:** catálogo estático (Gas horno, Luz cocina, Mano de obra, Empaque porción, Flete semanal).

**Validación:** no repetir el mismo `CostoIndirecto` en la misma versión.

Botón **+ Agregar costo indirecto**.

### Sección pasos

Lista ordenada de `RecetaPaso`.

| Campo | Regla |
|-------|-------|
| `orden` | ≥ 1, único por versión |
| `instruccion` | Obligatorio (trim) |
| `tiempo_minutos` | Opcional; si se indica, **> 0** |

Botones: **+ Agregar paso**, subir/bajar orden (demo), eliminar.

**Sin impacto en costos.**

### Resumen de costos (readonly)

| Stat | Campo `RecetaVersion` |
|------|----------------------|
| Ingredientes | `costo_ingredientes` |
| Indirectos | `costo_indirectos` |
| Total | `costo_total` |
| Por porción | `costo_por_porcion` |
| Precio sugerido | `precio_venta_sugerido` — **editable** en formulación; override manual conservado al guardar |

Botón **Usar cálculo automático** → `costo_por_porcion × (1 + margen_aplicado_pct / 100)` desde perfil del usuario.

### Acciones

| Botón | Comportamiento |
|-------|----------------|
| Guardar formulación | Persistir líneas + recalcular costos cache |
| Cancelar | Volver a `receta_edit.html?receta_id=` |

---

## Nueva versión (`recetaversion_create.html`)

Servicio Django previsto: `create_new_version(receta, notas_cambio)`.

| Campo / control | Regla |
|-----------------|-------|
| Versión origen | Solo lectura — `version_actual` (ej. v2) |
| `notas_cambio` | **Obligatorio** — motivo del cambio |
| Copiar ingredientes | Default marcado — clona `RecetaIngrediente` |
| Copiar pasos | Default marcado — clona `RecetaPaso` |
| Copiar indirectos | Default marcado — clona `RecetaCostoIndirecto` |
| `numero_version` | `max + 1` automático |

Tras crear vN: `receta.version_actual` → vN; versiones anteriores **inmutables**.

---

## Historial (`recetaversion_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Default página | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | `numero_version` desc |

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Versión | `numero_version` → «vN» |
| 1 | Fecha | `created_at` |
| 2 | Rendimiento | `rendimiento_cantidad` + `rendimiento_unidad` |
| 3 | Costo total | `costo_total` |
| 4 | Costo / porción | `costo_por_porcion` |
| 5 | Notas cambio | `notas_cambio` |
| 6 | Vigente | Badge si `receta.version_actual_id == pk` |
| 7 | Acciones | Ver · (Editar solo si vigente) |

---

## Detalle histórico (`recetaversion_detail.html`)

Solo lectura. Misma estructura que formulación sin controles de edición. Versiones pasadas no se modifican.

---

## Enlaces con cabecera Receta

| Origen | Destino |
|--------|---------|
| `receta_edit.html` | `version/recetaversion_edit.html?receta_id=` |
| `receta_list.html` (acciones) | Formulación → `recetaversion_edit.html?receta_id=` |
| `recetaversion_edit.html` | Historial, Nueva versión, Cabecera |

---

## Política de precio y margen

| Concepto | Regla |
|----------|-------|
| `margen_aplicado_pct` | Copiado del perfil del usuario al crear versión; **readonly** en formulación |
| Precio automático | `costo_por_porcion × (1 + margen_aplicado_pct / 100)` |
| Override manual | El usuario puede editar `precio_venta_sugerido`; badge «precio manual» |
| «Usar cálculo automático» | Restaura fórmula desde costo/porción y margen de la versión |
| Al recalcular costos | Si hay override manual, **conservar** precio salvo que el usuario pulse «Usar cálculo automático» |
| Nueva versión | Copia `margen_aplicado_pct` y precio de la versión origen (o recalcula si no había override — decisión Django) |

---

## Limitaciones del prototipo

Aceptadas para cerrar diseño; no bloquean **Conforme** del bloque:

1. Selectores de producto e indirecto: listas **fijas en JS** (`recetaversion_edit.js`); no leen CRUD en tiempo real.
2. Demo completo solo con **`?receta_id=1`** (Brownie); otras filas del listado sin carga JS.
3. **Guardar formulación** no recalcula costos en vivo; muestra modal de confirmación únicamente.
4. Listado y cabecera no sincronizan precio tras editar formulación en la misma sesión del navegador.
5. Catálogo `CostoIndirecto` y formulación usan datos demo independientes (sin enlace dinámico).

---

## Reglas de negocio (referencia)

1. Costos del listado de recetas siempre desde `version_actual`.
2. Nueva versión cuando cambia formulación y debe preservarse historial de costos.
3. Versiones con `OrdenProduccion` asociadas → **PROTECT** (no borrar).
4. Receta `P` puede tener 0 pasos; para marcar `A` se recomienda al menos un paso o documentar en `notas_cambio`.
5. Costos indirectos opcionales; si no hay líneas, `costo_indirectos = 0`.
6. Catálogo `CostoIndirecto` — CRUD en `/app/costos-indirectos/`; asignación en formulación.

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `version/recetaversion_edit.html` | Formulación vigente |
| `version/js/recetaversion_edit.js` | Demo Brownie + validación |
| `version/recetaversion_create.html` | Alta vN+1 |
| `version/js/recetaversion_create.js` | Validación `notas_cambio` |
| `version/recetaversion_list.html` | Historial |
| `version/js/recetaversion_list.js` | DataTables |
| `version/recetaversion_detail.html` | Lectura v histórica |
| `version/css/recetaversion.css` | Estilos submódulo |
