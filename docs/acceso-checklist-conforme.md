# Checklist Conforme — Módulo Acceso (`apps.security`)

**Estado global: CERRADO — Conforme v1.2 (2026-06-20).**

Validación OK del flujo **UserProfile** (seguridad): login, correo, TOTP, reset 2FA, **primer acceso → Noticias** y **Seguridad de la cuenta** desde Perfil. Alta de cuentas solo por Master (v1).

**Reglas:** [`acceso-reglas.md`](acceso-reglas.md)

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/ingresar/
```

| Bloque | URL de prueba |
|--------|----------------|
| Login | `http://127.0.0.1:8000/ingresar/` |
| Onboarding | `?flow=nuevo` → correo → QR → TOTP |
| Usuario activo | `?flow=activo` → TOTP |
| Reset 2FA | `acceso_actualizar_2fa.html` |
| Primer acceso Django | TOTP ok → `/app/noticias/` |
| Seguridad cuenta | `/app/seguridad/cuenta/` (desde Perfil) |

---

## Pantallas activas (prototipo)

| Pantalla | Archivo | Revisado | Conforme |
|----------|---------|----------|----------|
| Login | `acceso_login.html` | ☑ | **Conforme** |
| Código correo | `acceso_email_code.html` | ☑ | **Conforme** |
| Configurar 2FA | `acceso_totp_setup.html` | ☑ | **Conforme** |
| Validar TOTP | `acceso_totp.html` | ☑ | **Conforme** |
| Actualizar 2FA | `acceso_actualizar_2fa.html` | ☑ | **Conforme** |

## Fuera de alcance v1 (documentadas)

| Pantalla | Archivo | Conforme |
|----------|---------|----------|
| Acceso por invitación | `acceso_register.html` | **Conforme** (informativa; `/registro/` off) |
| Espera de pago | `acceso_espera_pago.html` | N/A v1 (referencia diseño) |

---

## Bloque Django — Post-login — **Conforme v1.1**

| # | Ítem | Estado |
|---|------|--------|
| D1 | Campo `UserProfile.primer_acceso_app_completado` + migración | **Conforme** |
| D2 | `post_login_routing.resolve_post_security_redirect` | **Conforme** |
| D3 | Primer acceso → `/app/noticias/` tras TOTP en `_finalize_access` | **Conforme** |
| D4 | Accesos siguientes → `/app/` (Dashboard) | **Conforme** |
| D5 | Flag marcado una sola vez; no resetea con Seguridad cuenta | **Conforme** |
| D6 | Usuarios existentes → flag `True` (data migration) | **Conforme** |
| D7 | Tests `apps/security/tests.py` (routing + flujo TOTP) | **Conforme** |
| D8 | Contenido bienvenida vía Noticias (Master) | **Conforme** (proceso operativo) |

---

## Bloque E — Seguridad de la cuenta (Perfil) — **Conforme v1**

Ver [`cuenta-seguridad-checklist-conforme.md`](cuenta-seguridad-checklist-conforme.md).

| # | Ítem | Estado |
|---|------|--------|
| E1 | Vista `/app/seguridad/cuenta/` + validaciones | **Conforme** |
| E2 | Reset 2FA + cambio contraseña + logout | **Conforme** |
| E3 | Re-login wizard correo/TOTP → Dashboard | **Conforme** |
| E4 | Validación manual usuario nuevo | **Conforme** |

---

## Criterios globales

- [x] Tokens pastel y tipografía Nunito ([`ui-ux.md`](ui-ux.md))
- [x] Responsivo 375px / 768px / 1140px
- [x] Modal global (`bakebudge-modal`)
- [x] Formularios HTML puro (sin django.forms)
- [x] Landing: **Entrar** → login; **Solicitar acceso** → contacto
- [x] Flujos demo: alta Master → login → correo → 2FA; activo; reset 2FA
- [x] Sin registro público; provisión Master + Facturación
- [x] Copy alineado a [`BAKEBUDGE_SECURITY.md`](BAKEBUDGE_SECURITY.md)
- [x] CTA **Ir a Facturación** tras alta usuario (demo)
- [x] **Primer acceso → Noticias**; siguientes → Dashboard
- [x] **Seguridad de la cuenta** desde Perfil (validación manual OK)

---

## Cierre aplicado

1. ✅ `acceso-reglas.md` → **Conforme**
2. ✅ Templates `apps/security/` + reglas [`acceso-reglas.md`](acceso-reglas.md) → **Conforme**
3. ✅ `prototype/README.md`, `fase-1b-landing.md` → actualizados
4. ✅ Implementación Django `apps.security` + primer acceso Noticias → **Conforme v1.1**
5. ✅ Seguridad de la cuenta (`apps.accounts`) → **Conforme v1** — [`cuenta-seguridad-checklist-conforme.md`](cuenta-seguridad-checklist-conforme.md)

**Pendiente v2:** hash de código correo. Resend producción ✓ — [`deploy-railway-plan.md`](deploy-railway-plan.md).

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Acceso / UserProfile seguridad (prototipo) | Validación OK — Conforme |
| 2026-06-20 | **Primer acceso → Noticias** (Django) | **Conforme v1.1** — confirmado y aprobado por usuario |
| 2026-06-20 | **Seguridad de la cuenta** desde Perfil | **Conforme v1** — validación manual OK (usuario nuevo) |
