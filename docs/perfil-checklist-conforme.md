# Checklist Conforme — Perfil (prototipo fase 1b)

**Estado global: CERRADO — todos los bloques Conforme (2026-06-16).**

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

---

## Bloque A — Datos del negocio — **Conforme**

**Reglas:** [`perfil-reglas.md`](perfil-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| A1 | Nombre repostería | **Conforme** |
| A2 | Selector moneda | **Conforme** |
| A3 | Margen objetivo (%) + hint | **Conforme** |
| A4 | Guardar cambios + modal demo | **Conforme** |

---

## Bloque B — Unidades por defecto — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | Peso (g/kg) | **Conforme** |
| B2 | Volumen (ml/L) | **Conforme** |
| B3 | Conteo (unidad) | **Conforme** |

---

## Bloque C — Cuenta e integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | Resumen usuario/correo readonly | **Conforme** |
| C2 | Nota seguridad fuera de alcance | **Conforme** |
| C3 | Nav + sidebar footer perfil | **Conforme** |
| C4 | `perfil-reglas.md` documentado | **Conforme** |

---

## Limitaciones aceptadas

Documentadas en [`perfil-reglas.md`](perfil-reglas.md#limitaciones-del-prototipo).

---

## Cierre aplicado

1. ✅ `perfil-reglas.md` → **Conforme**
2. ✅ `prototype/README.md`, `fase-1b-landing.md` → **Conforme**

**Fuera de este cierre:** avatar, recuperación contraseña sin sesión.

**Django v1 (2026-06-20):** `/app/perfil/` — **Conforme**. Seguridad de la cuenta — **Conforme v1** ([`cuenta-seguridad-checklist-conforme.md`](cuenta-seguridad-checklist-conforme.md)).

---

## Bloque D — Django Perfil + Seguridad cuenta — **Conforme v1**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Vista `/app/perfil/` + validación negocio/unidades | **Conforme** |
| D2 | Enlace Seguridad de la cuenta | **Conforme** |
| D3 | Flujo `/app/seguridad/cuenta/` (ver checklist dedicado) | **Conforme** |
| D4 | Validación manual usuario nuevo (seguridad cuenta) | **Conforme** |

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | A–C | Cierre integral del bloque Perfil — todos Conforme |
| 2026-06-20 | D — Django Perfil + Seguridad cuenta | **Conforme v1** — validación manual OK |
