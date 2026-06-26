# Checklist Conforme — Facturación (prototipo fase 1b)

**Estado global: CERRADO — todos los bloques Conforme (2026-06-16).**

Lista de verificación para cerrar **diseño y reglas** del bloque **Administración → Facturación** (`PaymentControl`, `apps.billing`). Solo Master.

> **Implementación Django v1:** ver checklist separado [`administracion-facturacion-checklist-conforme.md`](administracion-facturacion-checklist-conforme.md) — **Conforme** (2026-06-16).

**Reglas:** [`facturacion-reglas.md`](facturacion-reglas.md)

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

| Bloque | URL de prueba |
|--------|----------------|
| A — Listado | http://127.0.0.1:8000/app/administracion/facturacion_list.html?user_type=M |
| B — Alta | http://127.0.0.1:8000/app/administracion/facturacion_create.html?user_type=M |
| C — Edición activo | http://127.0.0.1:8000/app/administracion/facturacion_edit.html?id=1&user_type=M |
| C — Edición pendiente | http://127.0.0.1:8000/app/administracion/facturacion_edit.html?id=3&user_type=M |
| C — Histórico consumido | http://127.0.0.1:8000/app/administracion/facturacion_edit.html?id=6&user_type=M |
| D — Suspender / cancelar | http://127.0.0.1:8000/app/administracion/facturacion_delete.html?id=1&user_type=M |
| E — Filtro por owner | http://127.0.0.1:8000/app/administracion/facturacion_list.html?owner=demo&user_type=M |

---

## Bloque A — Listado — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | DataTables 10/20/50, filtros usuario/estado/modalidad | **Conforme** |
| A2 | Columnas PaymentControl + badges estado/modalidad | **Conforme** |
| A3 | Acciones según estado (Editar · Suspender/Cancelar · Ver) | **Conforme** |
| A4 | Botón + Nuevo período | **Conforme** |
| A5 | Filtro `?owner=` desde URL | **Conforme** |

---

## Bloque B — Alta — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | Formulario owner (User U), modalidad, estado, período, pago | **Conforme** |
| B2 | Guardar pendiente vs Guardar y activar | **Conforme** |
| B3 | Validación demo + modal | **Conforme** |
| B4 | Ayuda en línea (`facturacion_create_help.html`) | **Conforme** |

---

## Bloque C — Edición — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | Carga demo por `?id=` | **Conforme** |
| C2 | Período consumido readonly + aviso | **Conforme** |
| C3 | Auditoría created/updated readonly | **Conforme** |
| C4 | Ayuda alineada (`facturacion_edit_help.html`) | **Conforme** |

---

## Bloque D — Suspender / cancelar — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Suspender activo / cancelar pendiente | **Conforme** |
| D2 | Bloqueo período consumido (`?blocked=consumido`) | **Conforme** |

---

## Bloque E — Documentación e integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| E1 | `facturacion-reglas.md` alineado a `PaymentControl` | **Conforme** |
| E2 | Nav Administración + Master (`?user_type=M`) | **Conforme** |
| E3 | Docs del módulo actualizados | **Conforme** |

---

## Limitaciones aceptadas

Documentadas en [`facturacion-reglas.md`](facturacion-reglas.md#limitaciones-del-prototipo).

---

## Cierre aplicado

1. ✅ `administracion/README.md` y `facturacion-reglas.md` → **Conforme**
2. ✅ `prototype/README.md`, `fase-1b-landing.md` → **Conforme**

**Fuera de este cierre (prototipo):** implementación Django → [`administracion-facturacion-checklist-conforme.md`](administracion-facturacion-checklist-conforme.md) (**Conforme v1**).

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | A–E | Cierre integral del bloque Facturación — todos Conforme |
