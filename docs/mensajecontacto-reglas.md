# Requisito — `MensajeContacto` (`apps.public_site`)

**Estado:** **Conforme v1** — prototipo, reglas e implementación Django aprobados (2026-06-20). Checklists: [`mensajecontacto-checklist-conforme.md`](mensajecontacto-checklist-conforme.md), [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md).

Persistir las solicitudes enviadas desde el formulario público de **Contacto** (`/contacto/`) y permitir al **Master** consultarlas y gestionarlas desde `/app/administracion/mensajes-contacto/`.

**Checklist prototipo:** [`mensajecontacto-checklist-conforme.md`](mensajecontacto-checklist-conforme.md)  
**Checklist Django v1:** [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md)  
**Modelo:** [`BAKEBUDGE_MODELS.md#mensajecontacto`](BAKEBUDGE_MODELS.md#mensajecontacto)  
**Relacionado:** [`acceso-reglas.md`](acceso-reglas.md), [`fase-1b-landing.md`](fase-1b-landing.md), [`ui-ux.md`](ui-ux.md), [`dashboard-reglas.md`](dashboard-reglas.md)

**Implementación actual:** `POST` real en `/contacto/` → `MensajeContacto` en BD; gestión Master en `apps.administration`.  
**Template público:** [`apps/public_site/templates/public_site/contacto.html`](../apps/public_site/templates/public_site/contacto.html)

---

## Resumen del requisito

| Zona | Quién | Acción |
|------|-------|--------|
| **Pública** `/contacto/` | Visitante anónimo | Enviar nombre, correo y mensaje → crear `MensajeContacto` |
| **Privada** `/app/admin/...` | Solo Master | Listar, ver detalle, marcar leído, eliminar |

El envío **no crea** `User` ni activa registro automático. El Master sigue el flujo de [`acceso-reglas.md`](acceso-reglas.md): revisar mensaje → crear usuario manualmente si procede.

---

## Alcance v1

| Incluye | No incluye |
|---------|------------|
| Modelo `MensajeContacto` en PostgreSQL | Registro público `/registro/` |
| `POST` real en formulario `/contacto/` | CRUD de alta manual por Master |
| Listado Master con DataTables | Respuesta automática por email al visitante |
| Detalle + cambio de estado `P` → `L` | Edición del texto del mensaje por Master |
| Eliminación (confirmación modal) | Notificación push / badge en sidebar |
| Modal global ER/OK en envío público | Anti-spam avanzado (CAPTCHA, rate limit) — v2 |
| Entrada en menú **Administración** (Master) | App Django nueva (usa `apps.public_site`) |

---

## Modelo `MensajeContacto`

**App:** `apps.public_site`  
**Tabla sugerida:** `public_site_mensajecontacto`  
**Sin `owner`** — dato global del sistema (como `Noticia` en lectura global). Solo Master gestiona.

| Campo | Tipo | Obligatorio | Default | Notas |
|-------|------|-------------|---------|-------|
| `id` | BigAutoField | — | — | PK |
| `nombre` | CharField(150) | Sí | — | Del formulario público |
| `email` | EmailField | Sí | — | Del formulario público |
| `mensaje` | TextField | Sí | — | Del formulario público |
| `estado` | CharField(1) | Sí | `'P'` | `P` = Pendiente, `L` = Leído |
| `created_at` | DateTimeField | Sí | `auto_now_add` | Fecha de envío |
| `leido_at` | DateTimeField | No | `null` | Se setea al pasar a `L` |
| `ip_origen` | GenericIPAddressField | No | `null` | Opcional v1 — auditoría / anti-abuso futuro |

**Índices sugeridos:** `(estado, -created_at)`, `(-created_at,)`.

**Validaciones (vista pública):**

- `nombre`: no vacío, longitud máxima.
- `email`: formato válido.
- `mensaje`: no vacío, longitud mínima razonable (p. ej. 10 caracteres) y máxima (p. ej. 5000).

---

## Dos zonas de UI

| Zona | Menú / URL | Quién | Pantallas |
|------|------------|-------|-----------|
| **Envío público** | `/contacto/` | Todos (sin login) | `contacto.html` (ya existe) |
| **Gestión** | Administración → **Mensajes contacto** | Solo Master | `mensajecontacto_{list,detail,delete}.html` |

Templates Django: `apps/administration/templates/administration/mensajes_contacto/`  
Convención Django: `apps/public_site/templates/public_site/admin/mensajecontacto_*.html` (o `administracion/` según patrón final de migración).

---

## Pantallas — zona pública

| Pantalla | URL | Cambio respecto a hoy |
|----------|-----|------------------------|
| Contacto | `/contacto/` | `POST` → guardar `MensajeContacto`; modal **OK** si éxito, **ER** si validación falla |

**Formulario:** HTML puro ([`ui-ux.md`](ui-ux.md)); sin `django.forms`.  
**CSRF:** token obligatorio en `POST`.  
**Tras guardar:** `estado = 'P'`, `created_at` automático.

---

## Pantallas — gestión Master

Convención: **`mensajecontacto_{accion}.html`** (prefijo entidad en singular).

| # | Pantalla | URL Django | Prototipo |
|---|----------|------------|-----------|
| 1 | Listado | `/app/administracion/mensajes-contacto/` | `administracion/mensajecontacto_list.html` |
| 2 | Detalle | `/app/administracion/mensajes-contacto/<id>/` | `administracion/mensajecontacto_detail.html` |
| 3 | Eliminar | `/app/administracion/mensajes-contacto/<id>/eliminar/` | `administracion/mensajecontacto_delete.html` |

### Listado (`mensajecontacto_list.html`)

Estándar DataTables ([`ui-ux.md`](ui-ux.md#tablas-datatables)):

| Parámetro | Valor |
|-----------|-------|
| Paginación | 10 / 20 / 50 |
| Orden default | `-created_at` (más recientes primero) |
| Columnas | Fecha, Nombre, Email, Estado, Acciones |
| Filtro | Por `estado` (`P` / `L` / Todos) |
| Acciones | Ver detalle, Eliminar |

Badge estado: **Pendiente** (pastel warning) / **Leído** (pastel success).

**Sin alta manual** desde listado (los mensajes solo entran por el formulario público).

### Detalle (`mensajecontacto_detail.html`)

- Mostrar: `nombre`, `email`, `mensaje`, `created_at`, `estado`, `leido_at`.
- Acción **Marcar como leído** si `estado = 'P'` → `L` + `leido_at = now()`.
- Enlace **Eliminar** → pantalla delete.
- Enlace opcional `mailto:` al email del solicitante (fuera del sistema).
- Layout `/app/` + `[data-master-only]`.

### Eliminar (`mensajecontacto_delete.html`)

- Confirmación con resumen (nombre, email, fecha).
- Borrado **físico** v1 (mensaje transaccional, sin historial de negocio).
- POST + modal ER/OK según resultado.

**No hay** `mensajecontacto_create.html` ni `mensajecontacto_edit.html` (el texto del mensaje no se edita).

---

## Menú sidebar (Master)

Añadir en submenú **Administración** (después de Gestión noticias):

```text
Administración
  ├── Usuarios
  ├── Facturación
  ├── Gestión noticias
  └── Mensajes contacto    ← nuevo
```

Sidebar: `apps/core/templates/partials/app_sidebar.html`.

---

## Orden de trabajo

Ejecutar en este orden. **No saltar pasos** de diseño antes de implementación Django.

| Orden | Tarea | Entregable | Depende de |
|-------|-------|------------|------------|
| **1** | Completar especificación del modelo | Sección `MensajeContacto` en [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) + índice | **Completado** |
| **2** | Prototipo HTML — listado Master | `administracion/mensajecontacto_list.html` + CSS | **Completado** |
| **3** | Prototipo HTML — detalle Master | `administracion/mensajecontacto_detail.html` | **Completado** |
| **4** | Prototipo HTML — eliminar Master | `administracion/mensajecontacto_delete.html` | **Completado** |
| **5** | Nav + datos demo JS | `update-nav.py`, `mensajecontacto_store.js` + JS pantallas | **Completado** |
| **6** | Checklist diseño prototipo | `mensajecontacto-checklist-conforme.md` (revisión usuario) | **Completado** |
| **7** | Modelo Django + migración | `apps/public_site/models.py`, `migrate` | 1, 6 | **Completado** |
| **8** | Vista pública `POST` contacto | `views.contacto` (GET + POST), validación, modal | 7 | **Completado** |
| **9** | Vistas Master (list, detail, delete, marcar leído) | URLs bajo `/app/administracion/mensajes-contacto/` | 7, 6 | **Completado** |
| **10** | Protección Master | `@master_access` en vistas; sidebar solo Master | 9 | **Completado** |
| **11** | Pruebas funcionales | `apps/public_site/tests.py` — 8 casos | 8–10 | **Completado** |
| **12** | Marcar **Conforme** | [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md), `roadmap.md`, `fase-1b-landing.md` | 11 | **Completado** |

---

## Criterios de aceptación (v1)

- [x] Visitante envía formulario en `/contacto/` y el registro aparece en BD con `estado = P`.
- [x] Master ve listado ordenado por fecha con DataTables 10/20/50.
- [x] Master abre detalle y puede marcar **Leído** (`leido_at` guardado).
- [x] Master puede eliminar un mensaje con confirmación.
- [x] User estándar **no** accede a URLs de gestión.
- [x] Errores de validación en público usan **modal global** (`ER`), no `alert()`.
- [x] Éxito en público usa modal **OK** (mensaje tipo «Recibimos tu mensaje…»).

---

## Fuera de alcance (documentado para v2+)

| Ítem | Notas |
|------|-------|
| Email al equipo al recibir mensaje | `apps.core.services.email_delivery` |
| Email de acuse al visitante | Resend / SMTP |
| Rate limiting / CAPTCHA | Anti-spam |
| Export CSV | Reportes |
| Crear `User` desde detalle del mensaje | Flujo manual Master permanece |

---

## Referencias de estándar a replicar

| Patrón | Documento / ejemplo |
|--------|---------------------|
| Listado DataTables | [`productos-reglas.md`](productos-reglas.md), [`ui-ux.md`](ui-ux.md) |
| CRUD Master en Administración | [`noticias-reglas.md`](noticias-reglas.md), [`usuarios-reglas.md`](usuarios-reglas.md) |
| Formulario público HTML | [`ui-ux.md`](ui-ux.md#formularios-solo-html-sin-django-forms) |
| Modal global | [`ui-ux.md`](ui-ux.md#modal-global-de-mensajes) |
| Flujo solicitud acceso | [`acceso-reglas.md`](acceso-reglas.md) |

---

## Registro

| Fecha | Evento |
|-------|--------|
| 2026-06-19 | Requisito documentado — pendiente diseño prototipo gestión y modelo en `BAKEBUDGE_MODELS.md` |
| 2026-06-19 | Modelo en `BAKEBUDGE_MODELS.md` + prototipos gestión Master — checklist **Conforme** |
| 2026-06-20 | Implementación Django v1 — [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md) **Conforme** (aprobación usuario) |
