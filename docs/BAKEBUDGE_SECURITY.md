# BAKEBUDGE — Flujos de seguridad y accesos

Documento de **diseño funcional** alineado con la app **`apps.security`** (login, correo, TOTP) y el destino **`apps.dashboard`** (`/app/`).

> **Override v1 (2026-06):** no hay **registro público** `/registro/`. El Master crea cuentas y suscripciones; ver [`acceso-reglas.md`](acceso-reglas.md). Este documento conserva los flujos de seguridad post-alta.

**Modelos y campos:** ver [`modelos.md`](modelos.md) (`User` en `auth`, `UserProfile` en `apps.accounts`).

**Entrada autenticada al producto:** tras completar credenciales y segundo factor según aplique:

| Situación | Destino |
|-----------|---------|
| **Primer acceso** (`primer_acceso_app_completado = False`) | **`/app/noticias/`** — bienvenida y primeros pasos (contenido Master) |
| **Accesos siguientes** | **`/app/`** (`dashboard:home`, app **`apps.dashboard`**) |

Ver [`acceso-reglas.md`](acceso-reglas.md#primer-acceso--noticias--conforme-v11-aprobación-usuario-2026-06-20). La plantilla o módulos visibles pueden depender de `UserProfile.user_type` (`M` = Master, `U` = User).

---

## 1. Alcance

- **Registro público:** alta desde la landing (`/registro/`) con email, usuario y contraseña; crea `User` + `UserProfile` con flags de seguridad en `False`.
- **Usuario nuevo:** primer acceso tras alta Master (correo + alta 2FA) hasta **Noticias** (`/app/noticias/`); accesos siguientes al **dashboard** (`/app/`).
- **Usuario activo:** onboarding completado; login con contraseña + código TOTP.
- **Cambio / actualización 2FA:** usuario activo que perdió el factor TOTP; repite el ciclo completo tras contraseña correcta (sección **9**).
- La **implementación** (vistas, plantillas, servicios, SMTP/Resend, TOTP) queda en código; aquí solo el **contrato** del flujo y mensajes.

---

## 2. Criterio "Usuario nuevo"

Se considera que el usuario **aún no completó** el alta de seguridad cuando:

- `UserProfile.email_confirmed` **es `False`**, **y**
- `UserProfile.tfa_verified` **es `False`**.

Tras completar el flujo, ambos deben quedar en **`True`** para acceder a `/app/`. El **primer** ingreso completo redirige a **Noticias**; los posteriores al **dashboard**.

### 2.1 Rama intermedia (usuario a mitad de flujo)

Si **`email_confirmed = True`** y **`tfa_verified = False`** (confirmó correo pero no terminó 2FA):

- **No** repetir pasos 2.1–2.3 (correo ya validado).
- Entrar directamente en el **paso 3** (pantalla 2FA / QR).

---

## 3. Flujo principal (usuario nuevo)

### Paso 0 — Registro (solo primera vez)

1. Desde la landing, el usuario accede a **Registrarse**.
2. Ingresa **email**, **usuario** y **contraseña** (y confirmación).
3. Se crea `User` + `UserProfile` (`email_confirmed=False`, `tfa_verified=False`).
4. Redirección al login con mensaje: *«Cuenta creada. Ingresa para completar la configuración de seguridad.»*

> El registro **no** inicia sesión automáticamente; el onboarding de seguridad comienza en el primer login.

### Paso 1 — Credenciales

1. El usuario ingresa **usuario** y **contraseña**.
2. Se valida contra `auth_user` (`authenticate`) y debe existir `UserProfile` enlazado (`User.profile` / OneToOne).
3. Si `UserProfile.status = 'I'` (inactivo) o `locked_until` vigente → bloquear con mensaje acordado.

### Paso 2 — Validación por correo (caducidad 5 minutos)

**Condición de entrada:** `email_confirmed = False`.

| Subpaso | Comportamiento |
|---------|------------------|
| **2.1** | Pantalla informando que se envió un correo con un **código validador** que **vence en 5 minutos**. |
| **2.2** | El usuario ingresa el código recibido por correo. |
| **2.3** | Si el código es correcto y no ha vencido → paso **3 (2FA)**. |

**Campos `UserProfile`:** `email_confirm_code`, `email_confirm_exp` (+5 min), tras éxito `email_confirmed = True` (limpiar código/expiración).

**Origen del correo:** `User.email`. Si está vacío → bloquear con *«Tu cuenta no tiene correo configurado. Contacta soporte.»*

### Paso 3 — 2FA (TOTP + autenticador)

1. Pantalla con explicación de **primer ingreso**, instalar app **Autenticador**, y **código QR** (issuer: **BAKEBUDGE**).
2. Botón: **«Ya registré el código en mi app»**.
3. **3.1** Pantalla que solicita el **código 2FA**; al validar → `tfa_verified = True`.

**Campos:** `totp_secret` (generado para QR), `tfa_verified`, opcional `last_totp_reset`.

### Paso 4 — Fin de flujo

Si todo es correcto → `login()` completo y redirección:

- **Primer acceso:** `/app/noticias/` (`noticias:feed`) + mensaje de bienvenida.
- **Accesos siguientes:** `/app/` (`dashboard:home`).

---

## 4. Validaciones y mensajes (usuario nuevo)

| Id | Condición | Mensaje / acción |
|----|-----------|------------------|
| **a** | El usuario **no existe** | *«Usuario no encontrado»* |
| **b** | **Contraseña** incorrecta | *«Contraseña incorrecta. Si olvidaste tu contraseña, contacta soporte.»* |
| **c** | **Código de correo** incorrecto o caducado | *«Código inválido o expirado»* + **«Reenviar código»** y **«Cancelar»** |
| **d** | **Código 2FA** incorrecto | *«Código de autenticación incorrecto»* + **«Reintentar»** y **«Cancelar»** |
| **e** | Cuenta **inactiva** o **bloqueada** | *«Tu cuenta está temporalmente bloqueada. Intenta más tarde.»* |

### 4.1 Notas de comportamiento

- **Reenvío código (c):** nuevo código, nueva expiración, límite de frecuencia (anti-abuso).
- **Cancelar (c) y (d):** limpiar estado de sesión del wizard; volver al login.
- **Reintentos fallidos:** usar `locked_until` tras N intentos (p. ej. 5 en 15 min).
- Registro: validar email único y username único antes de crear `User`.

---

## 5. Referencia rápida de campos (`UserProfile` — seguridad)

| Campo | Uso en este flujo |
|-------|-------------------|
| `email_confirmed` | `False` hasta validar correo; `True` tras paso 2.3 |
| `email_confirm_code` | Código de 6 dígitos enviado por correo |
| `email_confirm_exp` | Caducidad del código (+5 min) |
| `totp_secret` | Secreto para QR / validar TOTP |
| `tfa_verified` | `False` hasta TOTP correcto; `True` al completar |
| `last_totp_reset` | Auditoría al forzar cambio 2FA |
| `locked_until` | Bloqueo temporal tras N fallos |
| `status` | `A` activo / `I` inactivo |

Campos de negocio (`nombre_negocio`, `moneda`, etc.) no participan en el wizard de seguridad.

---

## 6. Decisiones técnicas a fijar en implementación

1. **`UserProfile` obligatorio:** signal `post_save` al crear `User` (registro o admin).
2. **Sesión entre pasos:** clave `security_pending_user_id`; sin `login()` completo hasta TOTP válido.
3. **Código de correo:** valorar hash en lugar de texto plano (fase posterior).
4. **Correo:** `apps.core.services.email_delivery`; local en consola, producción Resend/SMTP.
5. **Aislamiento de datos:** tras login, todas las vistas privadas filtran por `request.user` (ver [`arquitectura.md`](arquitectura.md)).
6. **Registro vs admin:** v1 permite registro público; superusuarios se crean vía `createsuperuser`.

---

## 7. Diagrama de flujo (usuario nuevo)

```mermaid
flowchart TD
    reg[Registro publico]
    start[Login usuario y password]
    existsUser{Usuario existe}
    pwdOk{Password correcta}
    blocked{Cuenta bloqueada}
    profileExists{UserProfile existe}
    newUser{email_confirmed y tfa_verified False}
    emailOnly{email_confirmed True tfa_verified False}
    step2[Correo codigo 5 min]
    step3[2FA QR y TOTP]
    home[Dashboard /app/]

    reg --> start
    start --> existsUser
    existsUser -->|no| errA[Validacion a]
    existsUser -->|si| pwdOk
    pwdOk -->|no| errB[Validacion b]
    pwdOk -->|si| blocked
    blocked -->|si| errE[Validacion e]
    blocked -->|no| profileExists
    profileExists -->|no| errProfile[Politica perfil]
    profileExists -->|si| newUser
    newUser -->|si| step2
    newUser -->|no| emailOnly
    emailOnly --> step3
    step2 -->|ok| step3
    step2 -->|error| errC[Validacion c]
    step3 -->|ok| home
    step3 -->|error| errD[Validacion d]
```

---

## 8. Usuario activo

Usuario que **completó** el onboarding. Login habitual: contraseña + **TOTP** (sin correo ni QR).

### 8.1 Criterio "activo"

1. `UserProfile.totp_secret` no vacío.
2. `User.email` no vacío.
3. **`email_confirmed = True`** y **`tfa_verified = True`**.

Si no cumple → flujo **sección 3** (nuevo o rama intermedia).

### 8.2 Flujo principal

| Paso | Descripción |
|------|-------------|
| **1** | Usuario y contraseña. |
| **2** | Si cumple criterio activo → pantalla TOTP. |
| **3** | Pantalla TOTP con opción **«Cambio / Actualización 2FA»** (sección **9**). |
| **4** | TOTP correcto → `login()` → **Noticias** (primer acceso) o **dashboard** `/app/` (habitual). |

### 8.3 Validaciones (usuario activo)

| Id | Condición | Mensaje / acción |
|----|-----------|------------------|
| **a** | Contraseña incorrecta | *«Contraseña incorrecta…»* |
| **d** | TOTP incorrecto | *«Código de autenticación incorrecto»* + Reintentar / Cancelar |

### 8.4 Diagrama (usuario activo)

```mermaid
flowchart TD
    start[Login usuario y password]
    pwdOk{Password correcta}
    activeCheck{Criterio activo}
    totpScreen[Solicitar TOTP mas Cambio 2FA]
    home[Dashboard /app/]
    errB[Validacion b]
    errD[Validacion d]
    newFlow[Flujo usuario nuevo]
    reset2FA[Seccion 9 reset]

    start --> pwdOk
    pwdOk -->|no| errB
    pwdOk -->|si| activeCheck
    activeCheck -->|no| newFlow
    activeCheck -->|si| totpScreen
    totpScreen -->|TOTP ok| home
    totpScreen -->|TOTP error| errD
    totpScreen -->|Cambio 2FA| reset2FA
```

---

## 9. Cambio / actualización 2FA

Usuario **activo** que perdió acceso al autenticador. Desde la pantalla TOTP del activo puede solicitar reset.

### 9.1 Efectos del reset en `UserProfile`

| Campo | Efecto |
|-------|--------|
| `totp_secret` | Eliminar (NULL); nuevo secreto en siguiente ciclo |
| `tfa_verified` | `False` |
| `email_confirmed` | `False` (forzar correo + nuevo 2FA) |

Limpiar `email_confirm_code` y `email_confirm_exp`. Actualizar `last_totp_reset`.

### 9.2 Flujo post-reset

Repetir ciclo **sección 3** (pasos 2–4): correo → QR → TOTP → dashboard.

### 9.3 Riesgo

Quien tenga la **contraseña** puede resetear sin TOTP anterior. El **correo** actúa como segundo factor al re-enrolar. Valorar límites de frecuencia y confirmación por correo antes del reset en fases posteriores.

---

## 10. Integración con el sistema privado

Todas las vistas en `/app/` requieren:

1. `@login_required`
2. `email_confirmed = True` y `tfa_verified = True` (middleware o decorador `security_required`)
3. Querysets filtrados por `request.user` (productos, recetas, producción)

Patrón en vistas protegidas:

```python
try:
    profile = request.user.profile
except UserProfile.DoesNotExist:
    return redirect("security:login")
if not profile.is_security_complete:
    return redirect("security:email_code")  # o routing según flags
```

---

## 11. Mantenimiento

Al cambiar mensajes, pasos o campos → actualizar **este archivo** y [`modelos.md`](modelos.md).

Para implementación e inventario de archivos → [`BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md`](BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md).

---

*Documento de flujo de seguridad BAKEBUDGE — registro, usuario nuevo, usuario activo y cambio de 2FA.*
