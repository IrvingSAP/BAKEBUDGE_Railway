# Reglas del módulo Estadísticas — `ProduccionAnalytics` (`apps.analytics`)

**Estado:** **Conforme** — diseño aprobado; **Django v1 implementado** (2026-06-16).

**Implementación Django:** `/app/estadisticas/` — [`estadisticas-checklist-conforme.md`](estadisticas-checklist-conforme.md) bloque E.

Vista analítica de producciones **completadas**: márgenes, rankings y detalle de snapshots `ProduccionAnalytics`.

**Template Django:** `apps/analytics/templates/analytics/estadisticas_home.html` · **URL:** `/app/estadisticas/`  
**Modelos:** [`BAKEBUDGE_MODELS.md#produccionanalytics`](BAKEBUDGE_MODELS.md#produccionanalytics)  
**Relacionado:** [`BAKEBUDGE_ANALYTICS.md`](BAKEBUDGE_ANALYTICS.md), [`produccion-reglas.md`](produccion-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| KPIs agregados del periodo | `ResumenMensual` materializado |
| Rankings recetas, versiones, insumos | Analytics de órdenes canceladas |
| Tabla detalle por orden completada | Gráficos Chart.js (futuro) |
| Filtros periodo / receta / categoría insumo | `costo_real` vs estimado (**Pendiente**) |

Acceso menú: **Estadísticas** → `/app/estadisticas/` (`analytics:estadisticas_home`).

---

## Regla fundamental: datos del usuario conectado

- Consultas: `ProduccionAnalytics.objects.filter(owner=request.user)`
- Líneas insumo: vía `ProduccionAnalyticsProducto` del owner
- Solo órdenes con snapshot (estado `completada` en producción)

---

## Pantalla principal (`estadisticas_home.html`)

| Sección | Fuente |
|---------|--------|
| KPI cards | Agregados del periodo filtrado |
| Recetas más producidas | GROUP BY `receta_id` — COUNT, SUM(`unidades_producidas`) |
| Insumos más usados | `ProduccionAnalyticsProducto` SUM(`cantidad_normalizada_total`) |
| Versiones más productivas | GROUP BY `receta_version_id` |
| Evolución costo / porción | AVG(`costo_produccion_unitario`) por `periodo_mes` |
| Ratio indirectos / ingredientes | AVG(`costo_indirectos / costo_ingredientes`) |
| Tabla detalle | Filas `ProduccionAnalytics` |

---

## KPI cards

| Card | Cálculo |
|------|---------|
| Margen real (periodo) | `AVG(margen_real_pct)` vs `margen_objetivo_pct` (perfil) |
| Ganancia total | `SUM(ganancia_real)` |
| Órdenes completadas | `COUNT(*)` |
| Órdenes con pérdida | `COUNT` donde `perdida IS NOT NULL` |

---

## Filtros

| Filtro | Campo | Comportamiento |
|--------|-------|----------------|
| **Periodo** | `periodo_anio` + `periodo_mes` | Select mes (demo: Jun/May 2026, Todos) |
| **Receta** | `receta_id` | Exacto; «Todas» = sin filtro |
| **Categoría insumo** | `producto_categoria` en líneas | Afecta ranking insumos; «Todas» = sin filtro |

Botón **Limpiar filtros**. Los KPIs y rankings se recalculan en cliente (demo).

---

## Tabla detalle (`#tabla-analytics`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Default página | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | `fecha_produccion` desc |
| Búsqueda global DT | Desactivada — filtros propios |

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Código | `orden_codigo` |
| 1 | Receta | `receta_nombre` + «vN» |
| 2 | Unidades | `unidades_producidas` |
| 3 | Costo prod. | `costo_produccion_total` |
| 4 | Precio venta | `precio_venta_total` |
| 5 | Margen real | `margen_real_pct` |
| 6 | Ganancia | `ganancia_real` |
| 7 | Período | `periodo_mes` / `periodo_anio` |

Enlace opcional código → `produccion/orden_detail.html?id=` (demo).

---

## Enlaces cruzados

| Origen | Destino |
|--------|---------|
| `dashboard.html` | Stat «Margen promedio» → estadísticas (futuro) |
| `produccion/orden_detail.html` | Nota analytics generado |
| `estadisticas_home.html` | Código orden → detalle producción |

---

## Limitaciones del prototipo

1. Datos en `estadisticas-demo-data.js` — no leen `orden-demo-data.js` en tiempo real.
2. Filtros recalculan en JS; no persisten entre recargas.
3. Evolución de costos: barras simples (sin librería de charts).
4. Demo alineado a órdenes completadas OP-2026-008 (Brownie) y OP-2026-006 (Galletas).

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `estadisticas/estadisticas_home.html` | Vista principal |
| `estadisticas/js/estadisticas-demo-data.js` | Snapshots demo |
| `estadisticas/js/estadisticas.js` | Filtros + render |
| `estadisticas/css/estadisticas.css` | Filtros y widgets |
