# Reglas del módulo Acceso — `apps.security`

**Estado:** **Conforme v1.3** — reglas y diseño prototipo aprobados (2026-06-16); implementación Django incl. **primer acceso → Noticias** confirmada (2026-06-20); **idle timeout 40 min en `/app/`** (2026-06-16).

Convenciones de UI y flujos para **login, verificación de correo y 2FA (TOTP)**. Zona pública previa a `/app/`.

> **Decisión v1:** no hay **registro público** (`/registro/` deshabilitado). El **Master** crea la cuenta en **Administración → Usuarios** y registra la suscripción en **Administración → Facturación** antes del primer ingreso del User. Evita altas masivas automatizadas que comprometan la estabilidad del sistema.

**Checklist:** [`acceso-checklist-conforme.md`](acceso-checklist-conforme.md)  
**Templates Django:** `apps/security/templates/security/` · **URL:** `/ingresar/`  
**Flujos funcionales:** [`BAKEBUDGE_SECURITY.md`](BAKEBUDGE_SECURITY.md)  
**Guía implementación:** [`BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md`](BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md)  
**Modelo:** [`BAKEBUDGE_MODELS.md#userprofile`](BAKEBUDGE_MODELS.md#userprofile)  
**Relacionado:** [`facturacion-reglas.md`](facturacion-reglas.md), [`usuarios-reglas.md`](usuarios-reglas.md), [`cuenta-seguridad-reglas.md`](cuenta-seguridad-reglas.md), [`perfil-reglas.md`](perfil-reglas.md), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| Login con routing según flags de perfil | **Registro público** `/registro/` (v1 deshabilitado) |
| Verificación correo (código 6 dígitos, 5 min) | Recuperación de contraseña por email (v1: contactar soporte) |
| Alta y validación TOTP (QR + código) | Pasarela de pago |
| Reset / actualización 2FA (usuario activo, wizard login) | Autogestión de facturación por User |
| Cambio contraseña + reset 2FA desde `/app/` (Perfil) | Hash del código de correo (fase posterior) |
| **Primer acceso → Noticias** (`post_login_routing`) | — |
| Onboarding post-alta Master | Pantalla «Esperando confirmación de pago» (v1 no aplica) |

---

## Regla v1: alta de cuentas solo por Master

El flujo de acceso **no** incluye autoregistro ni cola de pago visible para el User.

| Paso | Quién | Dónde |
|------|-------|-------|
| 1. Crear `User` + `UserProfile` | Master | `/app/administracion/usuarios/nuevo/` |
| 2 | Registrar suscripción (`PaymentControl`) | Master | `/app/administracion/facturacion/nuevo/` — CTA desde alta usuario |
| 3. Entregar credenciales al cliente | Master | Fuera del sistema (correo, etc.) |
| 4. Primer login + correo + 2FA | User | `acceso_login.html` → wizard seguridad |
| 5. Primer panel | User / Master | **`/app/noticias/`** (primer acceso) · **`/app/`** (siguientes) |

**Motivo:** impedir que terceros maliciosos disparen registros masivos contra `/registro/` y sobrecarguen correo, base de datos o revisión manual.

**Landing pública:** CTAs de alta apuntan a **Contacto** («Solicitar acceso»), no a formulario de registro.

**Reglas relacionadas:** [`usuarios-reglas.md`](usuarios-reglas.md) · [`facturacion-reglas.md`](facturacion-reglas.md)

---

## Regla fundamental: acceso al producto

Tras credenciales y segundo factor válidos:

| Situación | Destino |
|-----------|---------|
| **Primer acceso** a `/app/` (`primer_acceso_app_completado = False`) | `/app/noticias/` — bienvenida y primeros pasos (contenido creado por Master) |
| **Accesos siguientes** | `/app/` (`dashboard:home`) |

El flag `UserProfile.primer_acceso_app_completado` se marca `True` al completar el primer ingreso. Usuarios existentes antes de la migración quedan con el flag en `True` (sin redirección forzada).

Re-enrolamiento por **Seguridad de la cuenta** no resetea este flag: el usuario ya recibió la bienvenida.

### Primer acceso → Noticias — **Conforme v1.1** (aprobación usuario 2026-06-20)

Tras completar el wizard de seguridad (TOTP correcto en `_finalize_access`), si `can_access_app` y `primer_acceso_app_completado = False`:

| Aspecto | Regla |
|---------|--------|
| Destino | `/app/noticias/` (`noticias:feed`) — no Dashboard |
| Mensaje | Modal OK: bienvenida + invitación a revisar noticias del sistema |
| Flag | `primer_acceso_app_completado = True` al redirigir (una sola vez) |
| Contenido | Master publica en **Gestión noticias**: bienvenida, primeros pasos, flujo del sistema |
| Alcance noticias | Global y/o **Personal** por destinatario (acción **Copiar** para plantillas) |
| Accesos siguientes | `/app/` (`dashboard:home`) |
| Re-login tras **Seguridad cuenta** | Dashboard (flag no se resetea) |
| Usuarios pre-migración | `primer_acceso_app_completado = True` por data migration |

Implementación: `apps/security/services/post_login_routing.py` · campo en `UserProfile` · migración `accounts.0002_…` · tests en `apps/security/tests.py`.

Ver también: [`BAKEBUDGE_NOTICIAS.md`](BAKEBUDGE_NOTICIAS.md) · [`noticias-reglas.md`](noticias-reglas.md)

| Propiedad / condición | Efecto |
|----------------------|--------|
| `is_security_complete` | `email_confirmed` ∧ `tfa_verified` ∧ `totp_secret` no vacío |
| `is_active_account` | `UserProfile.status = 'A'` y sin `locked_until` vigente |
| `has_active_subscription` | `PaymentControl` con `estado = activo` y fechas vigentes (solo `user_type = U`) |
| `can_access_app` | Seguridad completa ∧ cuenta activa ∧ suscripción (User U) |

**Master (`user_type = M`):** no requiere `PaymentControl` activo; primer acceso → Noticias; siguientes → `/app/`.

**User (`user_type = U`):** en v1 el Master ya registró un `PaymentControl` **activo** antes del primer login. Tras completar seguridad → **Noticias** (primer acceso) o **`/app/`** (habitual). La pantalla `acceso_espera_pago.html` queda **reservada** para una fase futura con autogestión; **no aplica** en v1.

Sesión parcial entre pasos del wizard: clave **`security_pending_user_id`** — sin `login()` completo hasta TOTP correcto.

### Cierre por inactividad en `/app/` — **Conforme v1.3**

Tras el login completo, la sesión permanece activa mientras el usuario navega en **`/app/`**. Si no hay actividad durante **40 minutos**, el sistema cierra la sesión y redirige a **`/ingresar/?idle=1`** con el mensaje *«Sesión cerrada por inactividad.»*

| Aspecto | Regla |
|---------|--------|
| Ámbito | Rutas bajo `/app/` (dashboard, catálogo, recetas, producción, estadísticas, ayuda, perfil, noticias en app, etc.) |
| Timeout | `APP_IDLE_TIMEOUT_SECONDS = 2400` (40 min) en `config/settings/base.py` |
| Actividad | Cualquier petición autenticada a `/app/` actualiza la marca `app_last_activity_at` en sesión |
| Marca inicial | Se guarda al completar login (TOTP OK) en `_finalize_access` |
| Efecto | `logout()` + redirect a login; el usuario debe volver a ingresar (contraseña + TOTP) |
| **`/ingresar/`** | Si la cookie de sesión sigue viva pero la marca falta o superó 40 min, **no** se salta el formulario: se cierra sesión y se muestra login |
| Fuera de `/app/` | Zona pública no actualiza la marca; el wizard de seguridad parcial no aplica este timeout |
| Implementación | `AppIdleTimeoutMiddleware` · `session_idle.py` · comprobación en `login_view` |

**Nota:** apagar el equipo sin «Cerrar sesión» no equivale a logout. Al pulsar **Entrar** en la landing con sesión expirada por inactividad, el sistema pide usuario y contraseña de nuevo.

---

## Pantallas del módulo

Convención templates: **`security/{accion}.html`** en `apps/security/templates/security/`.

| Pantalla | URL Django (futuro) | Prototipo | Flujo |
|----------|---------------------|-----------|-------|
| Ingresar | `/ingresar/` | `acceso_login.html` | Todos |
| ~~Registrarse~~ | ~~`/registro/`~~ | `acceso_register.html` | **Deshabilitado v1** — ver § Alta Master |
| Código correo | `/seguridad/correo/` | `acceso_email_code.html` | Primer ingreso / post-reset 2FA |
| Configurar 2FA (QR) | `/seguridad/totp-config/` | `acceso_totp_setup.html` | Onboarding / post-reset |
| Validar TOTP | `/seguridad/totp/` | `acceso_totp.html` | Onboarding + usuario activo |
| Actualizar 2FA (wizard) | `/seguridad/actualizar-2fa/` | `acceso_actualizar_2fa.html` | Sesión parcial login/TOTP |
| Seguridad de la cuenta | `/app/seguridad/cuenta/` | — (Django `/app/`) | Usuario logueado desde Perfil |
| ~~Espera de pago~~ | — | `acceso_espera_pago.html` | **No aplica v1** (referencia futura) |
| Cancelar wizard | `/seguridad/cancelar/` | (redirect en demo) | Limpia sesión → login |

Layout: **sin sidebar** de app; shell centrado con marca BAKEBUDGE, card de formulario y enlace «Volver al inicio».

---

## `acceso_login.html`

### Campos

| Campo | Tipo | Validación |
|-------|------|------------|
| Usuario | `text` | `required`, maxlength 150 |
| Contraseña | `password` | `required` |

### Acciones

| Elemento | Comportamiento |
|----------|----------------|
| **Ingresar** | POST → routing según perfil (ver § Routing) |
| **¿No tienes cuenta?** | Enlace a contacto — *«Solicitar acceso»* (no hay registro público) |
| **¿Olvidaste tu contraseña?** | Texto informativo: contactar soporte (v1) |

### Mensajes

Banner opcional si `?provisioned=1` (demo): *«Tu cuenta fue creada por un administrador. Ingresa para completar la configuración de seguridad.»*

Modal de aviso si `?idle=1`: *«Sesión cerrada por inactividad.»* (tras timeout de 40 min sin uso en `/app/`).

### Validaciones demo (JS)

| Condición | Mensaje modal |
|-----------|---------------|
| Usuario vacío | *«Ingresa tu usuario.»* |
| Contraseña vacía | *«Ingresa tu contraseña.»* |
| Demo `?demo=fail` | *«Contraseña incorrecta. Si olvidaste tu contraseña, contacta soporte.»* |
| Demo `?demo=blocked` | *«Tu cuenta está temporalmente bloqueada. Intenta más tarde.»* |

---

## `acceso_register.html` (deshabilitado v1)

**Propósito:** pantalla informativa; la ruta `/registro/` **no debe estar activa** en Django v1.

### Comportamiento

- Explica que el acceso es **por invitación** del administrador.
- CTA: **Contactar** → landing contacto.
- Enlace secundario: **Ingresar** si ya tiene credenciales.

No crea `User` ni `UserProfile`. Reservado para una fase futura si se habilita registro público con rate limiting y revisión.

---

## `acceso_email_code.html`

**Entrada:** `email_confirmed = False` (primer ingreso tras alta Master o tras reset 2FA).

### UI

| Elemento | Detalle |
|----------|---------|
| Indicador de paso | Paso 1 de 2 — Correo |
| Email enmascarado | `demo@***.com` (desde `User.email`) |
| Aviso caducidad | *«El código vence en 5 minutos.»* |
| Campo código | 6 dígitos, `inputmode="numeric"`, `pattern="[0-9]{6}"`, `maxlength=6` |

### Acciones

| Botón | Efecto |
|-------|--------|
| **Verificar** | Código correcto y no expirado → `acceso_totp_setup.html` |
| **Reenviar código** | Nuevo código + nueva expiración (modal confirmación demo) |
| **Cancelar** | Limpia wizard → `acceso_login.html` |

### Validaciones

| Id | Mensaje |
|----|---------|
| c | *«Código inválido o expirado»* + reenviar / cancelar |
| Sin email en User | *«Tu cuenta no tiene correo configurado. Contacta soporte.»* |

**Campos perfil:** `email_confirm_code`, `email_confirm_exp`; tras éxito `email_confirmed=True`, limpiar código/exp.

---

## `acceso_totp_setup.html`

**Entrada:** correo confirmado, `tfa_verified=False`.

### UI

| Elemento | Detalle |
|----------|---------|
| Indicador de paso | Paso 2 de 2 — Autenticador |
| Instrucciones | Instalar app Autenticador (Google, Microsoft, etc.) |
| QR | Imagen demo / placeholder; issuer **BAKEBUDGE** |
| Secreto manual | Texto copiable (accesibilidad) |
| CTA principal | **«Ya registré el código en mi app»** → `acceso_totp.html?mode=setup` |

---

## `acceso_totp.html`

Usada en **onboarding** (tras QR) y **login recurrente** (usuario activo).

### Campos

| Campo | Tipo |
|-------|------|
| Código 2FA | 6 dígitos TOTP |

### Acciones según contexto

| Contexto | Acciones extra |
|----------|----------------|
| Onboarding (`?mode=setup`) | Solo Verificar + Cancelar |
| Usuario activo (default) | Enlace **«Cambio / Actualización 2FA»** → `acceso_actualizar_2fa.html` |

### Post-validación (demo)

Tras TOTP correcto → **`/app/`** o **`/app/noticias/`** (primer acceso).

Validación **d**: *«Código de autenticación incorrecto»* + Reintentar / Cancelar.

---

## `acceso_actualizar_2fa.html`

Usuario **activo** que perdió el autenticador.

### UI

| Elemento | Detalle |
|----------|---------|
| Advertencia | Perderá el factor actual; repetirá correo + QR |
| Confirmación | Contraseña actual (`required`) |
| CTA | **«Confirmar actualización»** |

### Efecto en perfil (backend)

Reset: `email_confirmed=False`, `tfa_verified=False`, `totp_secret=NULL`; limpiar `email_confirm_*`; actualizar `last_totp_reset`.

Redirección → `acceso_email_code.html`.

> **Nota:** este flujo aplica solo con sesión parcial (`pending_user`) durante el wizard de login. Para usuarios ya en `/app/`, ver § Seguridad de la cuenta desde Perfil.

---

## Seguridad de la cuenta (desde Perfil) — **Conforme v1**

Usuario **logueado** en `/app/` que cambia contraseña y reinicia correo + 2FA.

**Doc detallada:** [`cuenta-seguridad-reglas.md`](cuenta-seguridad-reglas.md) · **Checklist:** [`cuenta-seguridad-checklist-conforme.md`](cuenta-seguridad-checklist-conforme.md)

### URL

| Pantalla | URL Django |
|----------|------------|
| Seguridad de la cuenta | `/app/seguridad/cuenta/` (`accounts:cuenta_seguridad`) |

Entrada: **Perfil** → enlace «Seguridad de la cuenta».

### UI

| Elemento | Detalle |
|----------|---------|
| Advertencia | Pérdida TOTP; revalidar correo; cierre de sesión |
| Readonly | Usuario, correo, nombre repostería |
| Contraseña actual | Obligatoria (`authenticate`) |
| Nueva + confirmar | Mín. 8; ≠ anterior; ≠ username; `validate_password` |
| Checkbox | Confirmación explícita |
| CTA | **Confirmar cambio de seguridad** |

### Efecto (solo tras POST exitoso, transacción atómica)

1. `User.set_password(nueva)`
2. `reset_two_factor(profile)` — mismos campos que § `acceso_actualizar_2fa`
3. `logout` + limpiar `security_session`
4. Redirect `/ingresar/` → wizard estándar correo → TOTP → `/app/`

**No resetea:** `status`, `locked_until`, datos de negocio, `primer_acceso_app_completado`.

**Validación manual:** probada con usuario nuevo — **Conforme** (2026-06-20).

---

## `acceso_espera_pago.html` (no aplica v1)

Pantalla **reservada** para una fase futura con autogestión de pago. En v1 el Master registra `PaymentControl` activo **antes** del primer login; el User no debe llegar aquí.

El HTML permanece como referencia de diseño. No enlazar desde flujos activos del prototipo.

---

## Routing tras contraseña correcta

Lógica equivalente a `apps/security/services/profile_routing.py`:

| Condición | Siguiente pantalla |
|-----------|-------------------|
| Sin `User.email` | Error soporte (bloqueo) |
| `email_confirmed` + `tfa_verified` + `totp_secret` | `acceso_totp.html` (activo) |
| `email_confirmed` + not `tfa_verified` | `acceso_totp_setup.html` |
| not `email_confirmed` | `acceso_email_code.html` |
| Resto | `acceso_totp_setup.html` |

Tras TOTP correcto:

1. `login(request, user)`
2. Si `can_access_app` y **primer acceso** → `/app/noticias/` (marca `primer_acceso_app_completado`)
3. Si `can_access_app` y acceso habitual → `/app/`
4. Si User U sin suscripción → **403 o mensaje soporte** (v1); no mostrar cola de espera pública

---

## Estilos y componentes

| Recurso | Uso |
|---------|-----|
| `security/css/acceso.css` | Shell auth, cards, pasos, QR placeholder |
| Tokens pastel | Alineados a [`ui-ux.md`](ui-ux.md) |
| `assets/css/bakebudge-modal.css` | Errores, éxito, confirmaciones |
| `assets/js/bakebudge-modal.js` | Modal global |
| Responsivo | 375px, 768px, 1140px |

Formularios: **solo HTML** — sin `django.forms` en implementación final.

---

## Parámetros demo (prototipo)

| URL | Simula |
|-----|--------|
| `acceso_login.html?provisioned=1` | Banner post-alta Master |
| `acceso_login.html?flow=nuevo` | Tras login → email_code |
| `acceso_login.html?flow=activo` | Tras login → totp |
| `acceso_login.html?flow=intermedio` | Tras login → totp_setup |
| `acceso_email_code.html?demo=expired` | Código expirado |

Servidor estático:

```bash
cd BAKEBUDGE
python manage.py runserver
# http://127.0.0.1:8000/app/
```

---

## Integración landing

Enlaces en landing Django (`apps.public_site`):

| Texto | Destino |
|-------|---------|
| Entrar | `../security/acceso_login.html` |
| Solicitar acceso / Comenzar / Crear cuenta | `contacto.html` (no hay registro público) |

---

## Escenarios de prueba (checklist funcional)

| # | Escenario | Resultado esperado |
|---|-----------|-------------------|
| 1 | Alta Master + facturación | User login → correo → QR → TOTP → **Noticias** (primer acceso) |
| 2 | Usuario activo | Login → TOTP → **Dashboard** |
| 3 | Código correo incorrecto | Error + reenviar / cancelar |
| 4 | TOTP incorrecto | Reintento / cancelar |
| 5 | Reset 2FA | Confirmar → correo → QR → TOTP |
| 6 | Intento `/registro/` | Deshabilitado — mensaje invitación / contacto |
| 7 | Master primer acceso | TOTP ok → **Noticias** |
| 8 | Acceso `/app/` sin 2FA | Redirige al paso pendiente |
| 9 | Segundo login mismo usuario | TOTP ok → **Dashboard** (flag ya marcado) |

---

## Registro

| Fecha | Evento |
|-------|--------|
| 2026-06-16 | Diseño prototipo acceso + reglas — **Conforme** |
| 2026-06-20 | Seguridad de la cuenta desde Perfil | **Conforme v1** — validación manual OK (usuario nuevo) |
| 2026-06-20 | **Primer acceso → Noticias** — **Conforme v1.1**, confirmado y aprobado por usuario |

---

## Mantenimiento

Al cambiar mensajes, pasos o campos → actualizar este archivo, [`BAKEBUDGE_SECURITY.md`](BAKEBUDGE_SECURITY.md) y [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md).

*Documento de reglas UI/UX — módulo Acceso BAKEBUDGE.*
