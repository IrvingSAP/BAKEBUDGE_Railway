# Checklist Conforme — Usuarios (prototipo fase 1b)

**Estado global: CERRADO — todos los bloques Conforme (2026-06-16).**

Lista de verificación para cerrar **diseño y reglas** del bloque **Administración → Usuarios** (`auth.User` + `UserProfile`). Solo Master.

> **Implementación Django v1:** ver checklist separado [`administracion-usuarios-checklist-conforme.md`](administracion-usuarios-checklist-conforme.md) — **Conforme** (2026-06-16).

**Reglas:** [`usuarios-reglas.md`](usuarios-reglas.md)

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

| Bloque | URL de prueba |
|--------|----------------|
| A — Listado | http://127.0.0.1:8000/app/administracion/usuario_list.html?user_type=M |
| B — Alta | http://127.0.0.1:8000/app/administracion/usuario_create.html?user_type=M |
| C — Edición | http://127.0.0.1:8000/app/administracion/usuario_edit.html?id=2&user_type=M |
| D — Contraseña | http://127.0.0.1:8000/app/administracion/usuario_password.html?id=2&user_type=M |
| E — Seguridad / 2FA | http://127.0.0.1:8000/app/administracion/usuario_seguridad.html?id=4&user_type=M |
| F — Desactivar | http://127.0.0.1:8000/app/administracion/usuario_delete.html?id=2&user_type=M |

---

## Bloque A — Listado — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | DataTables 10/20/50, filtros usuario/tipo/estado/correo verificado | **Conforme** |
| A2 | Columnas User + UserProfile + badges tipo/estado | **Conforme** |
| A3 | Acciones: Editar · Contraseña · 2FA · Desactivar | **Conforme** |
| A4 | Botón + Nuevo usuario | **Conforme** |
| A5 | Menú Administración solo Master (`?user_type=M`) | **Conforme** |

---

## Bloque B — Alta — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | Formulario `User` + `UserProfile` | **Conforme** |
| B2 | Validación demo + modal | **Conforme** |
| B3 | Ayuda en línea (`usuario_create_help.html`) | **Conforme** |

---

## Bloque C — Edición cuenta y perfil — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | Sin contraseña ni seguridad (pantallas dedicadas) | **Conforme** |
| C2 | Carga demo por `?id=` | **Conforme** |
| C3 | Ayuda alineada (`usuario_edit_help.html`) | **Conforme** |

---

## Bloque D — Contraseña — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Contexto usuario/nombre/correo readonly | **Conforme** |
| D2 | Contraseña + confirmación obligatorias | **Conforme** |
| D3 | Validación demo + modal | **Conforme** |

---

## Bloque E — Seguridad (correo y 2FA) — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| E1 | Referencia usuario: username, email, nombre, apellido | **Conforme** |
| E2 | Campos `email_confirmed`, `email_confirm_code`, `email_confirm_exp` | **Conforme** |
| E3 | Campos `tfa_verified`, `totp_secret` (enmascarado), `last_totp_reset` | **Conforme** |
| E4 | Acciones demo: guardar, reenviar código, reset 2FA | **Conforme** |
| E5 | Valores demo por usuario (`?id=`) | **Conforme** |

---

## Bloque F — Desactivación — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| F1 | Confirmación desactivar (no borrado físico) | **Conforme** |
| F2 | Demo bloqueo cuenta propia (`?blocked=self`) | **Conforme** |

---

## Bloque G — Documentación e integración — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| G1 | `usuarios-reglas.md` completo | **Conforme** |
| G2 | Nav Administración en `update-nav.py` | **Conforme** |
| G3 | Docs del módulo actualizados | **Conforme** |

---

## Limitaciones aceptadas

Documentadas en [`usuarios-reglas.md`](usuarios-reglas.md#limitaciones-del-prototipo).

---

## Cierre aplicado

1. ✅ `administracion/README.md` y `usuarios-reglas.md` → **Conforme**
2. ✅ `prototype/README.md`, `fase-1b-landing.md` → **Conforme**

**Fuera de este cierre (prototipo):** implementación Django → [`administracion-usuarios-checklist-conforme.md`](administracion-usuarios-checklist-conforme.md) (**Conforme v1**).

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | A–G | Cierre integral del bloque Usuarios — todos Conforme |
