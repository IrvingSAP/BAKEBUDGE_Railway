# Checklist Conforme — Producción (prototipo fase 1b)

**Estado global: CERRADO (prototipo) · Django v1 implementado (2026-06-16).**

Lista de verificación para cerrar **diseño y reglas** del bloque Producción (`apps.production`).

**Implementación Django:** `apps/production/` — URLs `/app/produccion/`, templates, servicios (`order_cost`, `state_transitions`), tests (`apps.production.tests`).
**Vista previa:**

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

| Bloque | URL de prueba |
|--------|----------------|
| A — Listado | http://127.0.0.1:8000/app/produccion/orden_list.html |
| B — Alta | http://127.0.0.1:8000/app/produccion/orden_create.html?receta_id=1 |
| C — Edición borrador | http://127.0.0.1:8000/app/produccion/orden_edit.html?id=4 |
| D — Detalle / ejecución | http://127.0.0.1:8000/app/produccion/orden_detail.html?id=1 |

---

## Bloque A — Listado (`produccion/`) — **Conforme**

**Reglas:** [`produccion-reglas.md`](produccion-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| A1 | DataTables 10/20/50, filtros código/receta y estado | **Conforme** |
| A2 | Columnas y badges de estado | **Conforme** |
| A3 | Acciones Ver / Editar (solo borrador) | **Conforme** |
| A4 | Botón + Nueva orden | **Conforme** |

---

## Bloque B — Alta planificación — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | Selector receta + versión vigente | **Conforme** |
| B2 | Lotes, fecha programada, notas | **Conforme** |
| B3 | Preview costo estimado y rendimiento | **Conforme** |
| B4 | Entrada `?receta_id=` desde recetas | **Conforme** |
| B5 | Validación modal + ayuda | **Conforme** |

---

## Bloque C — Edición borrador — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | Solo editable en estado borrador | **Conforme** |
| C2 | Recalculo costo al cambiar lotes | **Conforme** |
| C3 | Ayuda alineada | **Conforme** |

---

## Bloque D — Detalle y ciclo de estados — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Ingredientes escalados + pasos + costos | **Conforme** |
| D2 | Iniciar producción (borrador → en_proceso) | **Conforme** |
| D3 | Completar con precio sugerido editable | **Conforme** |
| D4 | Cancelar orden (borrador / en_proceso) | **Conforme** |
| D5 | Vista readonly completada / cancelada | **Conforme** |

---

## Bloque E — Documentación e integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| E1 | `produccion-reglas.md` completo | **Conforme** |
| E2 | Nav actualizado (`produccion/` + redirect legacy) | **Conforme** |
| E3 | Enlace **Producir** desde listado recetas | **Conforme** |
| E4 | Docs del módulo actualizados | **Conforme** |

---

## Limitaciones aceptadas del prototipo

Documentadas en [`produccion-reglas.md`](produccion-reglas.md#limitaciones-del-prototipo).

---

## Cierre aplicado

1. ✅ `produccion/README.md` y `produccion-reglas.md` → **Conforme**
2. ✅ `prototype/README.md`, `fase-1b-landing.md` → **Conforme**

**Fuera de este cierre:** `costo_real` vs estimado (pendiente), descuento stock.

---

## Bloque F — Django v1 (`apps.production`) — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| F1 | Modelo `OrdenProduccion` + migración | **Conforme** |
| F2 | Listado, alta, edición borrador, detalle + ayudas | **Conforme** |
| F3 | Ciclo borrador → en_proceso → completada/cancelada | **Conforme** |
| F4 | Costo estimado congelado al iniciar | **Conforme** |
| F5 | Detalle con ingredientes/pasos/indirectos escalados | **Conforme** |
| F6 | Enlace desde recetas + sidebar activo | **Conforme** |
| F7 | Nota analytics en orden completada | **Conforme** |
| F8 | Tests + aislamiento por owner | **Conforme** |
---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | A–E | Cierre integral del bloque Producción — todos Conforme |
| 2026-06-16 | F | Django v1 `apps.production` — implementación y tests |