# Checklist Conforme — Seguridad de la cuenta (`apps.accounts`)

**Estado global: CERRADO — Conforme v1 (2026-06-20).**

Lista de verificación para cerrar **implementación Django** del flujo **Seguridad de la cuenta**: cambio de contraseña + reset 2FA desde Perfil.

**Reglas:** [`cuenta-seguridad-reglas.md`](cuenta-seguridad-reglas.md)  
**Perfil:** [`perfil-reglas.md`](perfil-reglas.md)  
**Acceso relacionado:** [`acceso-reglas.md`](acceso-reglas.md)  
**App Django:** `apps.accounts` · reset 2FA: `apps.security.services.totp_reset`

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/app/perfil/ → Seguridad de la cuenta
# http://127.0.0.1:8000/app/seguridad/cuenta/
```

| Pantalla | URL Django |
|----------|------------|
| Perfil | `/app/perfil/` |
| Seguridad de la cuenta | `/app/seguridad/cuenta/` |

---

## Bloque A — Acceso — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| A1 | `@app_access_required` en vista `cuenta_seguridad` | **Conforme** |
| A2 | Entrada desde Perfil → enlace «Seguridad de la cuenta» | **Conforme** |
| A3 | User estándar con acceso `/app/` puede usar el flujo | **Conforme** |
| A4 | Cuenta bloqueada/inactiva → redirect Perfil con error | **Conforme** |

---

## Bloque B — Formulario y validación — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| B1 | Contraseña actual obligatoria (`authenticate`) | **Conforme** |
| B2 | Nueva: mín. 8, `validate_password`, ≠ anterior, ≠ username | **Conforme** |
| B3 | Confirmación debe coincidir | **Conforme** |
| B4 | Checkbox confirmación explícita | **Conforme** |
| B5 | Errores → modal ER + campos repoblados | **Conforme** |

---

## Bloque C — Efecto y post-acción — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| C1 | Transacción atómica: `set_password` + `reset_two_factor` | **Conforme** |
| C2 | Reset flags: `email_confirmed`, `tfa_verified`, `totp_secret`, códigos correo | **Conforme** |
| C3 | `last_totp_reset = now()` | **Conforme** |
| C4 | No modifica negocio, moneda, unidades, `user_type` | **Conforme** |
| C5 | `logout` + limpiar `security_session` | **Conforme** |
| C6 | Redirect `/ingresar/` + mensaje informativo | **Conforme** |
| C7 | Re-login → wizard correo → TOTP → `/app/` (Dashboard) | **Conforme** |
| C8 | `primer_acceso_app_completado` **no** se resetea | **Conforme** |

---

## Bloque D — Tests automatizados — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Validación: nueva = anterior / nueva = username | **Conforme** |
| D2 | POST inválido no resetea perfil | **Conforme** |
| D3 | POST ok: reset flags, logout, nueva contraseña login | **Conforme** |
| D4 | `apps/accounts/tests.py` — casos cuenta seguridad | **Conforme** |

---

## Bloque E — Validación manual — **Conforme**

| # | Escenario | Resultado |
|---|-----------|-----------|
| E1 | Usuario nuevo: Perfil → Seguridad → cambio contraseña | **OK** — aprobación usuario |
| E2 | Re-login con nueva contraseña + wizard correo/2FA | **OK** |
| E3 | Acceso restaurado a `/app/` (Dashboard) | **OK** |
| E4 | Datos de negocio en Perfil conservados | **OK** |

---

## Criterios globales

- [x] Formulario HTML puro + validación servidor
- [x] Modal global (OK / ER)
- [x] Layout `/app/` (`app_base.html`)
- [x] Sin recuperación «olvidé contraseña» sin sesión (v1)

---

## Fuera de alcance v1

Recuperación sin sesión, invalidar otras sesiones, cambio email/username, avatar.

---

## Cierre aplicado

1. ✅ `cuenta-seguridad-reglas.md` → **Conforme v1**
2. ✅ `perfil-reglas.md` → enlace y alcance actualizados
3. ✅ `acceso-reglas.md` → § Seguridad de la cuenta desde Perfil
4. ✅ Validación manual con usuario nuevo → **Conforme**
5. ✅ `docs/README.md` → enlace a este checklist

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-20 | Implementación Django v1 | Flujo acordado e implementado |
| 2026-06-20 | Validación manual (usuario nuevo) | **Conforme** — probado y confirmado por usuario |
