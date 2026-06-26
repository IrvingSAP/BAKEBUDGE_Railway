# Checklist Conforme — Recetas y derivados (prototipo fase 1b)

**Estado global: CERRADO (prototipo) · Django v1 implementado (2026-06-16).**

Lista de verificación para cerrar **diseño y reglas** del bloque Recetas (`apps.recipes`) y dependencias de catálogo.

**Implementación Django:** `apps/recipes/` — URLs `/app/recetas/`, templates, servicios (`cost_calculator`, `version_helpers`), tests (`apps.recipes.tests`).

**Vista previa base:**

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

| Bloque | URL de prueba |
|--------|----------------|
| A — Cabecera | http://127.0.0.1:8000/app/recetas/receta_list.html |
| B — Formulación | http://127.0.0.1:8000/app/recetas/version/recetaversion_edit.html?receta_id=1 |
| C — Versionado | http://127.0.0.1:8000/app/recetas/version/recetaversion_list.html?receta_id=1 |
| D — Costos indirectos | http://127.0.0.1:8000/app/costos_indirectos/costoindirecto_list.html |

---

## Bloque A — Cabecera `Receta` (`recetas/`) — **Conforme**

**Reglas:** [`recetas-reglas.md`](recetas-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| A1 | Listado: DataTables 10/20/50, filtros nombre/estado, columnas costo desde `version_actual` | **Conforme** |
| A2 | Alta: `Receta` + v1 (rendimiento), validación modal, ayuda | **Conforme** |
| A3 | Edición cabecera: nombre, notas, status, stats readonly, enlaces a formulación | **Conforme** |
| A4 | Eliminación: inactivar / borrar (demo) | **Conforme** |
| A5 | Ayudas create/edit alineadas con reglas actuales | **Conforme** |
| A6 | Acción **Formulación** en listado | **Conforme** |

---

## Bloque B — Formulación `RecetaVersion` (`recetas/version/`) — **Conforme**

**Reglas:** [`recetaversion-reglas.md`](recetaversion-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| B1 | Ingredientes: tabla, validación, aviso sin conversión | **Conforme** |
| B2 | Costos indirectos: asignación `RecetaCostoIndirecto` | **Conforme** |
| B3 | Pasos: orden, instrucción obligatoria | **Conforme** |
| B4 | Rendimiento editable + panel costos | **Conforme** |
| B5 | Precio sugerido editable + «Usar cálculo automático» + badge manual | **Conforme** |
| B6 | Guardar formulación: validación modal | **Conforme** |
| B7 | Ayuda formulación actualizada | **Conforme** |

---

## Bloque C — Versionado e historial — **Conforme**

**Reglas:** [`recetaversion-reglas.md`](recetaversion-reglas.md) (secciones nueva versión + historial)

| # | Ítem | Estado |
|---|------|--------|
| C1 | Nueva versión: `notas_cambio` obligatorio, copia ingredientes/pasos/indirectos | **Conforme** |
| C2 | Historial DataTables (v2 vigente, v1 histórica) | **Conforme** |
| C3 | Detalle histórico solo lectura (`recetaversion_detail`) | **Conforme** |
| C4 | Navegación cruzada (cabecera ↔ formulación ↔ historial) | **Conforme** |

---

## Bloque D — Catálogo `CostoIndirecto` (`costos_indirectos/`) — **Conforme**

**Reglas:** [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| D1 | Listado + filtros nombre/estado/unidad cobro | **Conforme** |
| D2 | Alta/edición: nombre, unidad cobro, costo > 0, status | **Conforme** |
| D3 | Eliminar: PROTECT demo (Gas horno en recetas) | **Conforme** |
| D4 | Enlace desde formulación al catálogo | **Conforme** |

---

## Bloque E — Documentación y reglas — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| E1 | `recetas-reglas.md` sin referencias obsoletas | **Conforme** |
| E2 | `recetaversion-reglas.md` — políticas precio/margen/recálculo | **Conforme** |
| E3 | `costos-indirectos-reglas.md` completo | **Conforme** |
| E4 | Ayudas HTML sin «próxima fase» | **Conforme** |
| E5 | `prototype/README.md` y `fase-1b-landing.md` actualizados | **Conforme** |

---

## Limitaciones aceptadas del prototipo (no bloquean Conforme)

Documentadas en [`recetaversion-reglas.md`](recetaversion-reglas.md#limitaciones-del-prototipo):

- Selectores de producto e indirecto en formulación: **listas fijas en JS** (no leen CRUD en tiempo real).
- Demo completo solo en **`receta_id=1`** (Brownie); otras filas del listado sin carga JS.
- Guardar no recalcula costos en vivo; mensaje modal únicamente.
- Listado y cabecera no sincronizan precio tras editar formulación en la misma sesión.

---

## Cierre aplicado

1. ✅ `recetas/README.md`, `recetas/version/README.md`, `costos_indirectos/README.md` → **Conforme**
2. ✅ `recetas-reglas.md`, `recetaversion-reglas.md`, `costos-indirectos-reglas.md` → **Conforme**
3. ✅ `prototype/README.md`, `fase-1b-landing.md` → **Conforme**

**Fuera de este cierre:** recálculo batch automático por cambio de precios en catálogo (servicio futuro).

---

## Bloque F — Django v1 (`apps.recipes`) — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| F1 | Modelos + migraciones (`Receta`, `RecetaVersion`, ingredientes, pasos, indirectos) | **Conforme** |
| F2 | CRUD cabecera + ayudas | **Conforme** |
| F3 | Formulación RecetaVersion (ingredientes, indirectos, pasos, precio) | **Conforme** |
| F4 | Versionado + historial + detalle readonly | **Conforme** |
| F5 | Vista costos (`/app/recetas/<id>/costos/`) | **Conforme** |
| F6 | Enlace **Producir** → producción | **Conforme** |
| F7 | Tests + aislamiento por owner | **Conforme** |

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06 | A (parcial) | Usuario: receta cabecera «lo veo OK» |
| 2026-06-16 | A–E | Cierre integral del bloque Recetas — todos Conforme |
| 2026-06-16 | F | Django v1 `apps.recipes` — implementación y tests |
