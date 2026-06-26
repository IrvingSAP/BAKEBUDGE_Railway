# Checklist Conforme — Usuarios Master (`apps.administration`)



**Estado global: CERRADO — Conforme v1 (2026-06-16).**



Lista de verificación para cerrar **diseño, reglas e implementación Django** del módulo **Administración → Usuarios** (`auth.User` + `UserProfile`). Solo Master.



**Reglas:** [`usuarios-reglas.md`](usuarios-reglas.md)  

**Checklist prototipo (fase 1b):** [`usuarios-checklist-conforme.md`](usuarios-checklist-conforme.md)  

**Modelos:** [`BAKEBUDGE_MODELS.md#userprofile`](BAKEBUDGE_MODELS.md#userprofile) — `auth.User`, `accounts.UserProfile`  

**App Django:** `apps/administration/`



```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/app/administracion/usuarios/
# Requiere sesión Master (UserProfile.user_type = 'M')
```



| Bloque | URL prototipo | URL Django |

|--------|---------------|------------|

| Listado | `…/administracion/usuario_list.html?user_type=M` | `/app/administracion/usuarios/` |

| Alta | `…/administracion/usuario_create.html?user_type=M` | `/app/administracion/usuarios/nuevo/` |

| Ayuda alta | `…/administracion/usuario_create_help.html` | `/app/administracion/usuarios/nuevo/ayuda/` |

| Edición | `…/administracion/usuario_edit.html?id=<pk>` | `/app/administracion/usuarios/<id>/editar/` |

| Ayuda edición | `…/administracion/usuario_edit_help.html` | `/app/administracion/usuarios/<id>/editar/ayuda/` |

| Contraseña | `…/administracion/usuario_password.html?id=<pk>` | `/app/administracion/usuarios/<id>/contrasena/` |

| Seguridad / 2FA | `…/administracion/usuario_seguridad.html?id=<pk>` | `/app/administracion/usuarios/<id>/seguridad/` |

| Desactivación | `…/administracion/usuario_delete.html?id=<pk>` | `/app/administracion/usuarios/<id>/desactivar/` |



> **Nota URLs:** las reglas originales mencionaban prefijo `/app/admin/usuarios/`; la implementación Django usa `/app/administracion/usuarios/` (misma convención que Monedas). Comportamiento equivalente; redacción unificada en [`usuarios-reglas.md`](usuarios-reglas.md).



---



## Bloque A — Modelos y señales — **Conforme**



| # | Ítem | Estado |

|---|------|--------|

| A1 | `auth.User` — username, email, password, nombres, `is_active` | **Conforme** |

| A2 | `UserProfile` — `user_type`, `moneda`, `status`, campos seguridad | **Conforme** |

| A3 | Signal `post_save` crea `UserProfile` + `ensure_user_catalog_defaults` | **Conforme** |

| A4 | Alta manual: vista actualiza perfil tras `create_user` (signal previo) | **Conforme** |

| A5 | FK `moneda` → `core.Moneda` (`PROTECT`, default `COP`) | **Conforme** |

| A6 | Admin Django `UserProfile` conservado en `apps.accounts` | **Conforme** |



---



## Bloque B — Acceso e integración — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| B1 | Decorador `@master_access` (login + perfil + `is_master`) | ☑ demo `?user_type=M` | **Conforme** |

| B2 | Usuarios no Master → 403 / redirección | ☑ | **Conforme** (`dashboard:access_denied`) |

| B3 | Listado **global** — sin filtro `owner` | ☑ | **Conforme** |

| B4 | `apps.administration` en `INSTALLED_APPS` | — | **Conforme** |

| B5 | URLs en `config/urls.py` bajo `app/` | — | **Conforme** (8 rutas usuarios) |

| B6 | Menú **Usuarios** en sidebar Administración (solo Master) | ☑ | **Conforme** |

| B7 | Layout `/app/` — `app_base.html`, modal global, responsivo | ☑ | **Conforme** |



---



## Bloque C — Listado — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| C1 | DataTables 10 / 20 / 50, búsqueda global off | ☑ | **Conforme** |

| C2 | Orden inicial: fecha registro DESC (columna 7) | ☑ | **Conforme** |

| C3 | Columna acciones no ordenable | ☑ | **Conforme** |

| C4 | Filtros: usuario, tipo, estado cuenta, correo verificado + limpiar | ☑ | **Conforme** |

| C5 | Columnas: username, email, negocio, tipo, estado, moneda, verificado, registro | ☑ | **Conforme** |

| C6 | Badges tipo (`M` Master / `U` User) | ☑ | **Conforme** (`admin_extras`) |

| C7 | Badges estado cuenta (`A` Activo / `I` Inactivo) | ☑ | **Conforme** (`catalog_extras`) |

| C8 | Acciones: Editar · Contraseña · 2FA · Desactivar | ☑ | **Conforme** |

| C9 | Desactivar oculto si cuenta ya inactiva | ☑ | **Conforme** |

| C10 | Botón **+ Nuevo usuario** | ☑ | **Conforme** |



---



## Bloque D — Alta — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| D1 | Campos `User`: username, email, password, confirm, nombres, `is_active` | ☑ | **Conforme** |

| D2 | Campos `UserProfile`: negocio, tipo, moneda, status | ☑ | **Conforme** |

| D3 | Default alta: `user_type=U`, `status=A`, `is_active=True` | ☑ | **Conforme** |

| D4 | Validación: username/email únicos, sin espacios, contraseña ≥ 8 | ☑ demo JS | **Conforme** (servidor + política Django) |

| D5 | Botones **Guardar usuario** / **Guardar y activo** | ☑ | **Conforme** |

| D6 | Ayuda create + botón en formulario (nueva pestaña) | ☑ | **Conforme** |

| D7 | Errores: modal global + resaltado campo (`form_validation`) | ☑ | **Conforme** |

| D8 | Éxito vía `messages.success` + redirect al listado | ☑ demo modal | **Conforme** |

| D9 | Redirección a Facturación tras alta User (`?owner=<pk>`) | ☑ | **Conforme** |

| D10 | Validación JS cliente (`usuario_create.js`) | ☑ | Pendiente v1.1 |



---



## Bloque E — Edición — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| E1 | ID y `date_joined` solo lectura | ☑ | **Conforme** |

| E2 | Sin contraseña ni seguridad (pantallas dedicadas) | ☑ | **Conforme** |

| E3 | Username editable; único excluyendo registro actual | ☑ | **Conforme** |

| E4 | `user_type` editable; bloqueo degradar único Master activo | ☑ demo | **Conforme** |

| E5 | Botones Guardar / Guardar y activo | ☑ | **Conforme** |

| E6 | Ayuda edit + botón en formulario | ☑ | **Conforme** |

| E7 | Errores: modal + resaltado campo | ☑ | **Conforme** |

| E8 | Validación JS cliente (`usuario_edit.js`) | ☑ | Pendiente v1.1 |



---



## Bloque F — Contraseña — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| F1 | Contexto usuario / nombre / correo readonly | ☑ | **Conforme** |

| F2 | Contraseña + confirmación obligatorias | ☑ | **Conforme** |

| F3 | Mínimo 8 caracteres + política Django | ☑ demo | **Conforme** |

| F4 | Errores: modal + resaltado campo | ☑ | **Conforme** |

| F5 | `User.set_password` + hash persistido | ☑ demo | **Conforme** |

| F6 | Validación JS cliente (`usuario_password.js`) | ☑ | Pendiente v1.1 |



---



## Bloque G — Seguridad (correo y 2FA) — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| G1 | Referencia: username, email, nombre, apellido (readonly) | ☑ | **Conforme** |

| G2 | `email_confirmed`, `email_confirm_code`, `email_confirm_exp` | ☑ demo | **Conforme** |

| G3 | `tfa_verified`, `totp_secret` enmascarado, `last_totp_reset` | ☑ demo | **Conforme** |

| G4 | Edición manual checkboxes `email_confirmed` / `tfa_verified` | ☑ | **Conforme** |

| G5 | **Reenviar código correo** | ☑ demo modal | **Conforme** (`email_confirmation.send_confirmation_email`) |

| G6 | **Reset 2FA** | ☑ demo modal | **Conforme** (`totp_reset.reset_two_factor`) |

| G7 | Validación JS cliente (`usuario_seguridad.js`) | ☑ | Pendiente v1.1 |



---



## Bloque H — Desactivación — **Conforme**



| # | Ítem | Prototipo | Django |

|---|------|-----------|--------|

| H1 | Confirmación antes de desactivar (no borrado físico) | ☑ | **Conforme** |

| H2 | `UserProfile.status=I` + `User.is_active=False` | ☑ | **Conforme** |

| H3 | Bloqueo desactivar cuenta propia | ☑ `?blocked=self` | **Conforme** |

| H4 | Bloqueo desactivar único Master activo | ☑ demo | **Conforme** |

| H5 | Datos de negocio del usuario permanecen (owner intacto) | ☑ doc | **Conforme** |

| H6 | Modal error si acción bloqueada | ☑ | **Conforme** |



---



## Bloque I — Assets compartidos — **Conforme**



| Ítem | Prototipo | Django |

|------|-----------|--------|

| CSS módulo (`usuarios.css`) | `administracion/css/usuarios.css` | `apps/administration/static/administration/css/usuarios.css` |

| JS listado + filtros DataTables | `administracion/js/usuario_list.js` | `apps/administration/static/administration/js/usuario_list.js` |

| DataTables vendor + `datatables-init.js` | `assets/js/` | Reutiliza `apps/catalog/static/catalog/vendor/` |

| Icono ayuda | `assets/images/icon-help.svg` | Reutiliza `catalog/partials/form_help_link.html` |

| Partials: `form_help_link`, `form_validation` | — | **Conforme** |

| `admin_extras` (`user_type_label`, `user_type_badge`) | — | **Conforme** |

| `catalog_extras` (`status_label`, `status_badge`) en listado | — | **Conforme** |

| `services/usuario_helpers.py` (Master count, TOTP mask, bloqueos) | — | **Conforme** |

| `apps/core/form_validation.py` + `bakebudge-form-errors.js` | — | **Conforme** |



---



## Criterios globales (layout `/app/`)



- [x] Sidebar: Administración → Usuarios (solo Master)

- [x] Topbar **Usuario** + **Cerrar sesión**

- [x] Administración global — **sin** filtro `owner` en queryset

- [x] Modal global (`BakeBudgeModal`) — errores, éxito, avisos; no `alert()`

- [x] Errores de formulario: mensaje con nombre de campo + resaltado inline

- [x] Formularios HTML puros (sin `django.forms`)

- [x] DataTables: default **10**, opciones **10 · 20 · 50**, búsqueda global off

- [x] 8 rutas usuarios bajo `/app/administracion/usuarios/`

- [x] `@master_access` en todas las vistas del módulo

- [x] Integración real con `apps.security` (correo + reset 2FA)



---



## Fuera de alcance v1 (documentado)



| Ítem | Notas |

|------|-------|

| Enlace **Ir a Facturación** tras alta User tipo U | **Conforme** — ver [`administracion-facturacion-checklist-conforme.md`](administracion-facturacion-checklist-conforme.md) |

| Validación JS en formularios create/edit/password/seguridad | Prototipo sí; Django solo servidor en v1 |

| Tests automatizados del módulo | v1.1 |

| Filtros server-side en listado | v1 filtra en cliente con DataTables |

| Creación automática `PaymentControl` al alta User | No aplica v1 — Master registra manualmente en Facturación |

| Prefijo URL `/app/admin/usuarios/` en docs legacy | Unificado a `/app/administracion/usuarios/` |



---



## Cierre aplicado



1. ✅ Reglas módulo: `usuarios-reglas.md` → **Conforme** (diseño + URLs Django)

2. ✅ Checklist prototipo fase 1b: `usuarios-checklist-conforme.md` → **Conforme**

3. ✅ Implementación Django `apps.administration` (Usuarios) → **Conforme v1**

4. ✅ Integración `/app/`, sidebar, `apps.security` → **Conforme**

5. ✅ Pantallas de ayuda (2) + validación modal/campo → **Conforme**

6. ✅ `docs/README.md` → enlace a este checklist



---



## Registro de aprobaciones



| Fecha | Bloque | Notas |

|-------|--------|-------|

| 2026-06-16 | Diseño prototipo + reglas (`usuarios-reglas.md`) | Conforme — bloques A–G prototipo |

| 2026-06-16 | Implementación Django Usuarios Master v1 | Flujo revisado — **Conforme** (aprobación usuario) |


