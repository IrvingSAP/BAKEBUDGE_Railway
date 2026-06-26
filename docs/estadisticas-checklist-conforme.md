# Checklist Conforme — Estadísticas (prototipo fase 1b)

**Estado global: CERRADO (prototipo) · Django v1 implementado (2026-06-16).**

Lista de verificación para cerrar **diseño y reglas** del bloque Estadísticas (`apps.analytics` vista UI).

**Implementación Django:** `apps/analytics/` — `/app/estadisticas/`, `services/summary.py`, `record_production.py`, signal al completar orden, tests (`apps.analytics.tests`).
```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

---

## Bloque A — KPIs del periodo — **Conforme**

**Reglas:** [`estadisticas-reglas.md`](estadisticas-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| A1 | Margen real vs objetivo | **Conforme** |
| A2 | Ganancia total | **Conforme** |
| A3 | Órdenes completadas | **Conforme** |
| A4 | Órdenes con pérdida | **Conforme** |

---

## Bloque B — Rankings y tendencias — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | Recetas más producidas (bar-list) | **Conforme** |
| B2 | Insumos más usados (bar-list) | **Conforme** |
| B3 | Versiones más productivas | **Conforme** |
| B4 | Evolución costo / porción por mes | **Conforme** |
| B5 | Ratio indirectos / ingredientes | **Conforme** |

---

## Bloque C — Tabla detalle — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | DataTables 10/20/50 | **Conforme** |
| C2 | Columnas snapshot analytics | **Conforme** |
| C3 | Enlace a orden de producción | **Conforme** |

---

## Bloque D — Filtros e integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Filtro periodo (mes) | **Conforme** |
| D2 | Filtro receta | **Conforme** |
| D3 | Filtro categoría insumo (ranking) | **Conforme** |
| D4 | Nav + redirect `estadisticas.html` | **Conforme** |
| D5 | `estadisticas-reglas.md` + README | **Conforme** |

---

## Limitaciones aceptadas

Documentadas en [`estadisticas-reglas.md`](estadisticas-reglas.md#limitaciones-del-prototipo).

---

## Cierre aplicado

1. ✅ `estadisticas/README.md` y `estadisticas-reglas.md` → **Conforme**
2. ✅ `prototype/README.md`, `fase-1b-landing.md` → **Conforme**

**Fuera de este cierre:** Chart.js, `ResumenMensual`, analytics de canceladas.

---

## Bloque E — Django v1 (`apps.analytics`) — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| E1 | Modelos + migraciones (`ProduccionAnalytics`, líneas producto) | **Conforme** |
| E2 | Snapshot al completar orden (signal + idempotencia) | **Conforme** |
| E3 | Vista `/app/estadisticas/` — KPIs, rankings, filtros, tabla | **Conforme** |
| E4 | Servicio `get_estadisticas_summary` | **Conforme** |
| E5 | Sidebar + enlace desde detalle orden | **Conforme** |
| E6 | Dashboard consume `AVG(margen_real_pct)` | **Conforme** |
| E7 | Tests + aislamiento por owner | **Conforme** |
---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | A–D | Cierre integral del bloque Estadísticas — todos Conforme |
| 2026-06-16 | E | Django v1 `apps.analytics` — implementación y tests |