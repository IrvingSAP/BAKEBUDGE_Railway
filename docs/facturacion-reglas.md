# Reglas del módulo Facturación — `PaymentControl` (`apps.billing`)

**Estado:** **Conforme v1.1** — reglas, prototipo e implementación Django aprobados (2026-06-16).

Convenciones de UI, listado y CRUD para **suscripciones y pagos** de usuarios tipo User. Solo Master.

**Checklist prototipo:** [`facturacion-checklist-conforme.md`](facturacion-checklist-conforme.md)  
**Checklist Django v1:** [`administracion-facturacion-checklist-conforme.md`](administracion-facturacion-checklist-conforme.md)  
**Templates Django:** `apps/administration/templates/administration/` · **URL:** `/app/administracion/`  
**Modelo:** [`BAKEBUDGE_MODELS.md#paymentcontrol`](BAKEBUDGE_MODELS.md#paymentcontrol)  
**Relacionado:** [`usuarios-reglas.md`](usuarios-reglas.md), [`dashboard-reglas.md`](dashboard-reglas.md), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| CRUD de `PaymentControl` (histórico 1:N por `owner`) | Pasarela de pago automática |
| Confirmación manual de pago por Master | Facturación de usuarios Master (`user_type = M`) |
| Suspensión / cancelación de períodos | Imagen de comprobante (`voucher_image` — fase 2) |
| — | Autogestión de pago por el User |

Acceso menú: **Administración → Facturación** (solo `UserProfile.user_type = 'M'`).

---

## Regla fundamental: acceso Master y alcance User

- Vistas exigen `request.user.profile.user_type == "M"`.
- Listado: todos los `PaymentControl` con `select_related("owner", "moneda", "created_by")`.
- **Solo aplica a usuarios `user_type = U`** — al crear, el selector de `owner` filtra Users estándar.
- Master no requiere filas de pago para operar.
- Prototipo: `?user_type=M` en URL.

**Relaciones clave:**

| Campo | Modelo | Notas |
|-------|--------|-------|
| `owner` | `auth.User` | Usuario que paga (N:1) |
| `moneda` | `core.Moneda` | Moneda del `monto` |
| `created_by` / `updated_by` | `auth.User` | Típ. Master que registra |

No duplicar estado en `UserProfile`: `status` (A/I) es bloqueo de cuenta; `PaymentControl.estado` es ciclo de suscripción.

### Provisión v1 (Master → User)

| Paso | Acción |
|------|--------|
| 1 | Alta en **Usuarios** (`usuario_create`) |
| 2 | Registro de pago en **Facturación** (`facturacion_create`) — estado `activo` antes del primer login |
| 3 | User ingresa en `/ingresar/` y completa wizard de seguridad |
| 4 | Acceso a `/app/` con `can_access_app = True` |

No hay cola «esperando pago» visible para el User en v1. La facturación es operación interna del Master, no autogestión del cliente.

---

## Pantallas del módulo

Convención: **`facturacion_{accion}.html`**

| Pantalla | URL Django | Prototipo |
|----------|------------|-----------|
| Listado | `/app/administracion/facturacion/` | `administracion/facturacion_list.html` |
| Alta | `/app/administracion/facturacion/nuevo/` | `administracion/facturacion_create.html` |
| Ayuda alta | `…/nuevo/ayuda/` | `administracion/facturacion_create_help.html` |
| Edición | `/app/administracion/facturacion/<id>/editar/` | `administracion/facturacion_edit.html` |
| Ayuda edición | `…/<id>/editar/ayuda/` | `administracion/facturacion_edit_help.html` |
| Suspender / cancelar | `/app/administracion/facturacion/<id>/accion/` | `administracion/facturacion_delete.html` |

---

## Listado (`facturacion_list.html`)

### DataTables

| Parámetro | Valor |
|-----------|--------|
| Registros por página (default) | **10** |
| Opciones | **10 · 20 · 50** |
| Orden inicial | `payment_date` DESC, luego `start_date` DESC (columna 7) |
| Columna acciones | No ordenable |
| Búsqueda global DT | Desactivada — filtros propios |

### Filtros

| Filtro | Columna | Comportamiento |
|--------|---------|----------------|
| **Usuario** | 0 | Contiene (`owner.username`), tiempo real |
| **Estado** | 2 | Exacto sobre badge |
| **Modalidad** | 1 | Exacto: Mensual / Anual |

Botón **Limpiar filtros**.

### Columnas

| # | Columna | Origen |
|---|---------|--------|
| 0 | Usuario | `PaymentControl.owner` → `User.username` |
| 1 | Modalidad | `PaymentControl.modalidad` |
| 2 | Estado | `PaymentControl.estado` |
| 3 | Inicio | `PaymentControl.start_date` |
| 4 | Fin | `PaymentControl.end_date` |
| 5 | Monto | `PaymentControl.monto` + `moneda.codigo` |
| 6 | Método | `PaymentControl.payment_method` |
| 7 | Fecha pago | `PaymentControl.payment_date` |
| 8 | Acciones | Editar · Suspender/Cancelar |

### Badges estado (`estado`)

| Valor | Etiqueta | Clase CSS |
|-------|----------|-----------|
| `pendiente` | Pendiente | `badge badge-draft` |
| `activo` | Activo | `badge badge-active` |
| `suspendido` | Suspendido | `badge badge-inactive` |
| `consumido` | Consumido | `badge badge-system` |

### Badges modalidad (`modalidad`)

| Código | Etiqueta |
|--------|----------|
| `M` | Mensual |
| `A` | Anual |

### Cabecera

| Control | Destino |
|---------|---------|
| **+ Nuevo período** | `facturacion_create.html` |

Enlace contextual desde listado: `facturacion_list.html?owner=demo`. Tras alta User en Django: redirección a `facturacion/nuevo/?owner=<pk>`.

---

## Alta (`facturacion_create.html`)

### Campos obligatorios

| Campo | Regla |
|-------|-------|
| `owner` | Obligatorio. User con `user_type = U` |
| `modalidad` | Obligatorio. `M` (Mensual) o `A` (Anual). Default `M` |
| `estado` | Obligatorio. Default alta: **`pendiente`** |

### Campos opcionales (alta pendiente)

| Campo | Regla |
|-------|-------|
| `start_date`, `end_date` | Vacíos en registro inicial |
| `plazo_de_gracia` (`plazoDeGracia`) | Default **0**. Entero 0–30 — días extra tras `end_date` |
| `payment_date`, `payment_method`, `monto`, `moneda` | Completar al confirmar pago |
| `payment_voucher` | Máx. 50 — referencia bancaria |
| `other_data` | Máx. 100 |

### Confirmar pago (botón **Guardar y activar**)

Master completa pago y activa período:

1. `payment_date` obligatorio  
2. `payment_method` obligatorio  
3. `monto` > 0 y `moneda` obligatorios  
4. `start_date` obligatorio; `end_date` según `modalidad` (+1 mes / +1 año) o manual  
5. `estado = activo`  
6. Validar: máximo **un** `activo` por `owner` (sin contar vigencia por fechas)
7. `created_by = request.user` (Master)

### Validación cliente (Django v1.1)

`facturacion_form.js` — patrón `data-bb-validate-form` + `BakeBudgeFormErrors` + modal:

| Regla | Comportamiento |
|-------|----------------|
| Alta | `owner` obligatorio |
| `plazo_de_gracia` | Entero 0–30 (default 0 si vacío) |
| **Guardar y activar** | Mismas reglas que servidor: pago, monto, moneda, `start_date` |
| `end_date` vacío | Sugiere +1 mes (M) o +1 año (A) desde `start_date` |

La validación servidor sigue siendo la fuente de verdad; el JS evita envíos inválidos.

### Acciones

| Botón | Comportamiento |
|-------|----------------|
| **Guardar período** | Crea registro (típ. `pendiente`) |
| **Guardar y activar** | Confirma pago + `estado=activo` |
| **Cancelar** | Vuelve al listado |

---

## Edición (`facturacion_edit.html`)

| Aspecto | Regla |
|---------|-------|
| `pk` | Solo lectura |
| `owner` | Solo lectura (no reasignar período) |
| `estado = consumido` | Editable por Master — aviso informativo; acción «Suspender/Cancelar» sigue bloqueada |
| `created_by`, `created_at`, `updated_by`, `updated_at` | Solo lectura |
| Cambio `pendiente` → `activo` | Mismas reglas que confirmar pago en alta |
| Cambio manual de estado | Master puede pasar entre `pendiente`, `activo`, `suspendido` y `consumido` vía formulario |

---

## Suspender / cancelar (`facturacion_delete.html`)

| `estado` actual | Acción UI | Resultado |
|-----------------|-----------|-----------|
| `activo` | **Suspender** | `estado = suspendido` |
| `pendiente` | **Cancelar** | `estado = suspendido` |
| `consumido` | Bloqueado | No eliminar — histórico auditoría |
| `suspendido` | Info | Ya suspendido; sin acción destructiva |

No borrado físico de registros históricos.

---

## Vigencia, plazo de gracia y acceso

| Concepto | Regla |
|----------|-------|
| Fecha efectiva de fin | `end_date + plazo_de_gracia` días (`effective_end_date`) |
| Período vigente | `estado = activo` **y** `start_date ≤ hoy ≤ effective_end_date` (`is_vigente`) |
| Suscripción activa | `UserProfile.has_active_subscription` → al menos un `PaymentControl` activo **vigente** |
| Vencimiento automático | Al login (y al finalizar acceso), `expire_overdue_payments(user)` marca `activo → consumido` si `hoy > effective_end_date` |

El campo `plazo_de_gracia` (0–30, default 0) extiende el acceso tras `end_date` sin cambiar la fecha almacenada.

**Un solo activo por owner:** al activar un período nuevo, debe no existir otro registro con `estado = activo` (independiente de fechas). La vigencia por fechas controla el acceso del User.

---

## Choices de referencia

**`payment_method`:** `banco`, `transferencia`, `pagomovil`, `efectivo`, `otros`

**Flujo de estados:** ver diagrama en [`BAKEBUDGE_MODELS.md#paymentcontrol`](BAKEBUDGE_MODELS.md#paymentcontrol).

---

## Mensajes al usuario

Errores, éxito y avisos → **modal global** (`BakeBudgeModal`).

---

## Limitaciones del prototipo

1. Visibilidad Master: `?user_type=M`.
2. Selector `owner`: lista fija de Users demo en JS.
3. Cálculo `end_date` por modalidad: demo simplificado en cliente.
4. Validación «un solo activo vigente»: demo JS, no persiste.
5. Sin integración con middleware `has_active_subscription`.

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `administracion/facturacion_list.html` | Listado |
| `administracion/js/facturacion_list.js` | DataTables + filtros |
| `administracion/facturacion_create.html` | Alta |
| `administracion/js/facturacion_create.js` | Validación + activar |
| `administracion/facturacion_edit.html` | Edición |
| `administracion/js/facturacion_edit.js` | Carga demo |
| `administracion/js/facturacion_form.js` (Django) | Validación cliente alta/edición |
| `administracion/facturacion_delete.html` | Suspender / cancelar |
| `administracion/js/facturacion_delete.js` | Demo bloqueos |
| `administracion/css/facturacion.css` | Estilos módulo |
