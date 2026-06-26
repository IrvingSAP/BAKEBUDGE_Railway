# Reglas del módulo Usuarios — `User` + `UserProfile` (`apps.accounts`)

**Estado:** **Conforme** — reglas, prototipo e implementación Django v1 aprobados (2026-06-16).

Convenciones de UI, listado y CRUD para la **gestión de cuentas** de la plataforma (solo Master).

**Checklist prototipo:** [`usuarios-checklist-conforme.md`](usuarios-checklist-conforme.md)  
**Checklist Django v1:** [`administracion-usuarios-checklist-conforme.md`](administracion-usuarios-checklist-conforme.md)  
**Templates Django:** `apps/administration/templates/administration/` · **URL:** `/app/administracion/`  
**Modelos:** [`BAKEBUDGE_MODELS.md#userprofile`](BAKEBUDGE_MODELS.md#userprofile)  
**Relacionado:** [`dashboard-reglas.md`](dashboard-reglas.md), [`perfil-reglas.md`](perfil-reglas.md), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| Listado y gestión de `auth.User` + `UserProfile` | Autogestión del perfil propio — [`perfil-reglas.md`](perfil-reglas.md) |
| Alta manual de cuentas por Master | Registro público `/registro/` |
| Desactivación de cuentas | Autogestión de pago User — [`facturacion-reglas.md`](facturacion-reglas.md) |
| — | Flujos de correo, 2FA y reset — `apps.security` |

Acceso menú: **Administración → Usuarios** (solo `UserProfile.user_type = 'M'`).

> **v1 — única vía de alta:** el Master crea la cuenta aquí y registra la suscripción en **Administración → Facturación** antes de entregar credenciales. No hay registro público (anti-abuso). Ver [`acceso-reglas.md`](acceso-reglas.md).

---

## Regla fundamental: acceso Master

- Todas las vistas del módulo exigen `request.user.profile.user_type == "M"`.
- Listado: **todos** los usuarios de la plataforma (`User.objects.select_related("profile")`).
- **No** aplica filtro `owner` — es administración global.
- Usuario estándar (`U`) recibe 403 o redirección si intenta acceder por URL.
- Prototipo: menú y páginas visibles con `?user_type=M`; demo Master en `js/main.js`.

---

## Pantallas del módulo

Convención: **`usuario_{accion}.html`**

| Pantalla | URL Django | Prototipo |
|----------|------------|-----------|
| Listado | `/app/administracion/usuarios/` | `administracion/usuario_list.html` |
| Alta | `/app/administracion/usuarios/nuevo/` | `administracion/usuario_create.html` |
| Ayuda alta | `…/nuevo/ayuda/` | `administracion/usuario_create_help.html` |
| Edición | `/app/administracion/usuarios/<id>/editar/` | `administracion/usuario_edit.html` |
| Ayuda edición | `…/<id>/editar/ayuda/` | `administracion/usuario_edit_help.html` |
| Desactivación | `/app/administracion/usuarios/<id>/desactivar/` | `administracion/usuario_delete.html` |
| Contraseña | `/app/administracion/usuarios/<id>/contrasena/` | `administracion/usuario_password.html` |
| Seguridad / 2FA | `/app/administracion/usuarios/<id>/seguridad/` | `administracion/usuario_seguridad.html` |

---

## Listado (`usuario_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Registros por página (default) | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | Fecha registro DESC (columna 7) |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada — filtros propios |

### Filtros

| Filtro | Columna | Comportamiento |
|--------|---------|----------------|
| **Usuario** | 0 | Contiene (`username`), tiempo real |
| **Tipo** | 3 | Exacto: Master / User |
| **Estado cuenta** | 4 | Exacto sobre badge |
| **Correo verificado** | 6 | «Sí» / «No» / Todos |

Botón **Limpiar filtros**.

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Usuario | `User.username` |
| 1 | Correo | `User.email` |
| 2 | Negocio | `UserProfile.nombre_negocio` |
| 3 | Tipo | `UserProfile.user_type` |
| 4 | Estado cuenta | `UserProfile.status` |
| 5 | Moneda | `UserProfile.moneda` (código ISO) |
| 6 | Correo verificado | `UserProfile.email_confirmed` |
| 7 | Registro | `User.date_joined` |
| 8 | Acciones | Editar · Contraseña · 2FA · Desactivar |

### Badges tipo (`user_type`)

| Código | Etiqueta | Clase CSS |
|--------|----------|-----------|
| `M` | Master | `badge badge-type-master` |
| `U` | User | `badge badge-type-user` |

### Badges estado cuenta (`UserProfile.status`)

| Código | Etiqueta | Clase CSS |
|--------|----------|-----------|
| `A` | Activo | `badge badge-active` |
| `I` | Inactivo | `badge badge-inactive` |

### Cabecera

| Control | Destino |
|---------|---------|
| **+ Nuevo usuario** | `usuario_create.html` |

---

## Alta (`usuario_create.html`)

Crea `User` + `UserProfile` (signal o vista explícita). Es el **único** punto de alta en v1.

Tras guardar, el Master debe:

1. Crear `PaymentControl` activo en `/app/administracion/facturacion/nuevo/` (User tipo U).
2. Comunicar usuario/contraseña al cliente.
3. El User completa correo + 2FA en el primer login ([`acceso-reglas.md`](acceso-reglas.md)).

**Prototipo demo:** tras crear un User (`user_type = U`), el modal de éxito ofrece **Ir a Facturación** con el `owner` preseleccionado en `facturacion_create.html?owner=…&user_type=M`.

### Campos obligatorios — `User`

| Campo | Regla |
|-------|-------|
| `username` | Obligatorio. Único en plataforma. Máx. 150. Sin espacios. |
| `email` | Obligatorio. Formato válido. Único en plataforma. |
| `password` | Obligatorio en alta. Mín. 8 caracteres (política Django). |
| `password_confirm` | Debe coincidir con `password`. |

### Campos opcionales — `User`

| Campo | Regla |
|-------|-------|
| `first_name` | CharField opcional |
| `last_name` | CharField opcional |
| `is_active` | Default `True`. Checkbox en formulario. |

### Campos obligatorios — `UserProfile`

| Campo | Regla |
|-------|-------|
| `user_type` | Obligatorio. Default alta manual: **`U`**. Solo Master puede asignar **`M`**. |
| `moneda` | Obligatorio. FK a `core.Moneda` — selector COP, MXN, USD, EUR (demo). |
| `status` | Obligatorio. Default **`A`**. |

### Campos opcionales — `UserProfile`

| Campo | Regla |
|-------|-------|
| `nombre_negocio` | CharField(150) opcional |

### No editable / automático en alta

| Campo | Notas |
|-------|-------|
| `email_confirmed` | `False` hasta flujo de verificación |
| `tfa_verified` | `False` |
| `owner` de datos de negocio | N/A — el propio `User` es owner de sus productos |

### Validación (orden)

1. `username` y `email` únicos  
2. Contraseñas coinciden y cumplen política  
3. `user_type` ∈ {`M`, `U`}  
4. Persistir `User` + `UserProfile` en transacción  
5. Si `user_type = U`: crear `PaymentControl` inicial (futuro billing)

### Acciones

| Botón | Comportamiento |
|-------|----------------|
| **Guardar usuario** | Valida y crea cuenta |
| **Guardar y activo** | Fuerza `status=A` e `is_active=True` |
| **Cancelar** | Vuelve al listado |

---

## Edición (`usuario_edit.html`)

Datos de cuenta y perfil de negocio. **Sin contraseña ni seguridad** — pantallas dedicadas.

| Aspecto | Regla |
|---------|-------|
| `pk` / ID | Solo lectura |
| `username` | Editable; único excluyendo el registro actual |
| `user_type` | Editable por Master; no degradar al **último** Master |
| `date_joined` | Solo lectura |
| Contraseña | Pantalla [`usuario_password.html`](usuario_password.html) |
| Correo / 2FA | Pantalla [`usuario_seguridad.html`](usuario_seguridad.html) |

---

## Contraseña (`usuario_password.html`)

| Campo | Regla |
|-------|-------|
| Usuario / nombre / correo | Solo lectura — contexto del registro |
| `password` | Obligatorio. Mín. 8 caracteres |
| `password_confirm` | Debe coincidir |

Acceso desde listado → **Contraseña**.

---

## Seguridad — correo y 2FA (`usuario_seguridad.html`)

Campos de `UserProfile` — sección **Campos — seguridad** en [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#userprofile).

### Referencia usuario (solo lectura)

| Campo | Origen |
|-------|--------|
| Usuario | `User.username` |
| Correo | `User.email` |
| Nombre / Apellido | `User.first_name`, `User.last_name` |

### Campos editables (Master)

| Campo | Regla |
|-------|-------|
| `email_confirmed` | Checkbox — marcar verificado manualmente (excepcional) |
| `tfa_verified` | Checkbox — estado 2FA completado |

### Campos informativos (solo lectura en UI)

| Campo | Descripción |
|-------|-------------|
| `email_confirm_code` | Código 6 dígitos pendiente |
| `email_confirm_exp` | Caducidad (+5 min) |
| `totp_secret` | Secreto TOTP enmascarado |
| `last_totp_reset` | Último reset del autenticador |

### Acciones adicionales

| Botón | Comportamiento |
|-------|----------------|
| **Reenviar código correo** | Genera y envía nuevo `email_confirm_code` (demo) |
| **Reset 2FA** | Limpia `totp_secret` y flags según reglas de negocio |

Acceso desde listado → **2FA**.

---

## Desactivación (`usuario_delete.html`)

| Regla | Detalle |
|-------|---------|
| Acción | **Desactivar**, no borrado físico: `UserProfile.status=I` + `User.is_active=False` |
| Propio usuario | No puede desactivarse a sí mismo |
| Último Master | No desactivar si es el único `user_type=M` activo |
| Datos | Productos/recetas del usuario **permanecen** (owner intacto) |
| UI | Confirmación + modal éxito/error |

Mensaje bloqueo propio: «No puedes desactivar tu propia cuenta mientras estás conectado.»

---

## Mensajes al usuario

Errores, éxito y avisos → **modal global** (`BakeBudgeModal`). No `alert()`.

---

## Limitaciones del prototipo

1. Visibilidad Master en menú: demo con `?user_type=M` en URL (`js/main.js`).
2. Datos de listado y formularios: demo estático; carga parcial por `?id=` en edición, contraseña y seguridad.
3. Contraseña y seguridad: validación en cliente; no persiste entre recargas.
4. `totp_secret` mostrado enmascarado; no se expone el valor completo en UI.
5. Reenviar código / reset 2FA: modal demo; sin integración con `apps.security`.

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `administracion/usuario_list.html` | Listado |
| `administracion/js/usuario_list.js` | DataTables + filtros |
| `administracion/usuario_create.html` | Alta |
| `administracion/js/usuario_create.js` | Validación alta |
| `administracion/usuario_edit.html` | Edición cuenta + perfil |
| `administracion/js/usuario_edit.js` | Carga demo + edición |
| `administracion/usuario_password.html` | Cambio contraseña |
| `administracion/js/usuario_password.js` | Validación contraseña |
| `administracion/usuario_seguridad.html` | Correo + 2FA |
| `administracion/js/usuario_seguridad.js` | Demo seguridad |
| `administracion/usuario_delete.html` | Desactivación |
| `administracion/js/usuario_delete.js` | Demo bloqueos |
| `administracion/css/usuarios.css` | Estilos módulo |
| `apps/accounts/views.py` | Vistas Django (futuro) |
