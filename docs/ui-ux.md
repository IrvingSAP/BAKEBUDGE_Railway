# UI/UX — BAKEBUDGE

## Stack de interfaz

| Capa | Tecnología |
|------|------------|
| Marcado | **HTML** (templates Django) |
| Estilos | **CSS** propio (`tokens.css` + componentes) |
| Comportamiento | **JavaScript** en HTML/templates cuando se requiera |
| Tablas | [**DataTables**](https://datatables.net/manual/) |

Backend y persistencia: **Django** + **PostgreSQL** (ver [`arquitectura.md`](arquitectura.md)). No se usa SPA ni librerías React/Vue en v1.

## Templates y convenciones

La UI vive en **templates Django** (`apps/*/templates/`) y estáticos compartidos (`apps/core/static/`, `apps/dashboard/static/`, etc.).

1. Crear o editar pantallas en la app del módulo (p. ej. `apps/catalog/templates/catalog/productos/`).
2. Validar en local con `python manage.py runserver` → http://127.0.0.1:8000/.
3. Marcar **Conforme** en el checklist del módulo (índice en [`docs/README.md`](README.md)).

Los tokens de diseño están en `apps/core/static/css/tokens.css` y se aplican vía `bakebudge-home.css` / `bakebudge-app.css`.

### Nombres de archivos HTML (zona `/app/`)

Cada pantalla de una **app Django** usa el **nombre de la app en singular** como prefijo, seguido de la acción en snake_case (como en templates Django):

| Patrón | Ejemplo |
|--------|---------|
| `{app}_list.html` | `producto_list.html` |
| `{app}_create.html` | `producto_create.html` |
| `{app}_edit.html` | `producto_edit.html` |
| `{app}_delete.html` | `producto_delete.html` |

Los archivos se agrupan en subcarpeta del módulo: `apps/catalog/templates/catalog/productos/producto_list.html`.

Índice de apps y URLs: [`prototype/README.md`](../prototype/README.md) (archivo histórico; fuente activa = Django).

## Estilo visual

Pastel, limpio y aireado — pensado para repostería artesanal.

## Tokens de diseño

| Token | Valor | Uso |
|-------|-------|-----|
| Fondo | `#FFF9F5` | Crema cálido, base de página |
| Primario | `#E8B4BC` | Rosa polvoriento, botones y acentos |
| Secundario | `#B4D4E8` | Azul suave, links y badges |
| Acento | `#C4E8B4` | Menta, estados positivos |
| Texto | `#4A4039` | Cuerpo y títulos |
| Bordes | `#F0E6DE` | Cards, inputs, separadores |
| Radius | 12–16px | Cards, botones, inputs |

## Tipografía

Sans redondeada y legible — candidatas: **Nunito**, **DM Sans**.

## Diseño responsivo (obligatorio)

**Todas las páginas** del proyecto deben ser **responsivas**: funcionar y adaptarse correctamente a distintos tipos de pantalla (móvil, tablet y desktop).

### Requisitos

| Requisito | Detalle |
|-----------|---------|
| Viewport | `<meta name="viewport" content="width=device-width, initial-scale=1.0">` en todo HTML |
| Breakpoints mínimos | 480px (móvil pequeño), 768px (móvil/tablet), 900px (tablet), 1024px (desktop) |
| Navegación móvil | Menú colapsable en pantallas &lt; 768px; CTAs accesibles sin scroll horizontal |
| Grids y cards | `auto-fit` / `minmax()` o columnas que colapsen a 1 columna en móvil |
| Imágenes | `max-width: 100%`, `loading="lazy"`; alturas adaptables en cards |
| Tipografía | `clamp()` para títulos; sin overflow horizontal (`overflow-x: hidden` en body) |
| Formularios | Inputs y botones a ancho completo en móvil |
| Validación | Probar en al menos 375px, 768px y 1140px antes de marcar pantalla **Conforme** |

### Alcance

- **Zona pública:** `apps/public_site/templates/public_site/` (`home.html`, `servicios.html`, `contacto.html`)
- **Zona privada `/app/`:** `apps/core/templates/app_base.html` + templates por módulo
- **Acceso / 2FA:** `apps/security/templates/security/`

Referencia CSS responsivo landing: `apps/public_site/static/public_site/css/bakebudge-home.css`.  
Referencia CSS zona app: `apps/dashboard/static/dashboard/css/bakebudge-app.css`.

## Formularios: solo HTML (sin Django Forms)

**Regla de diseño obligatoria:** no usar la API de **`django.forms`** (`Form`, `ModelForm`, `forms.py`, `{{ form }}`, widgets Django) en BAKEBUDGE v1.

| Qué usar | Qué evitar |
|----------|------------|
| Markup **HTML** estándar: `<form>`, `<input>`, `<select>`, `<textarea>`, `<button>` | `django.forms.Form`, `ModelForm`, `form.as_p`, crispy-forms |
| Validación HTML5 (`required`, `type`, `min`, `max`, `pattern`) donde aplique | Generación automática de campos desde modelos |
| Procesamiento en **vistas Django** leyendo `request.POST` / `request.GET` | Dependencia de widgets y renderizado Django Forms |
| Mismos estilos CSS (`.form-field`, tokens pastel) en todos los templates | Mezclar lógica de presentación en clases Form |

**Flujo acordado:**

1. Definir markup HTML en el template del módulo.
2. La vista valida datos manualmente leyendo `request.POST` / `request.GET` (helpers ligeros propios, no `django.forms`).

El HTML del template es la fuente de verdad del layout de cada campo.

## Layout

### Landing (zona pública)

- Hero con ilustración y propuesta de valor.
- Grid de recetas destacadas (contenido marketing/estático).
- CTA prominentes: **Entrar** / **Solicitar acceso** (contacto; sin registro público en v1).
- Footer con marca y links básicos.

### App (zona privada)

- Sidebar izquierda: Dashboard, Productos, Recetas, Producción, Estadísticas, **Catálogo base** (submenú: Categorías, Conversiones de unidad, Costos indirectos), Perfil, Noticias, **Ayuda General** (guía del ciclo — [`ayuda-reglas.md`](ayuda-reglas.md)); línea en blanco y **Administración** (submenú: Usuarios, Facturación, Gestión noticias) solo si `UserProfile.user_type = 'M'`.
- **Usuario** arriba a la derecha (`User.username`); **Cerrar sesión** al final del sidebar.
- **Datos por usuario conectado:** toda información en `/app/` pertenece a `request.user`. Ver [`dashboard-reglas.md`](dashboard-reglas.md#regla-fundamental-datos-del-usuario-conectado).
- Reglas completas: [`dashboard-reglas.md`](dashboard-reglas.md).
- Área de contenido con cards y tablas suaves.
- Espaciado generoso (padding 24–32px en secciones).

## Componentes base

- **Cards** — fondo blanco, borde suave, sombra ligera.
- **Botones** — primario (rosa), secundario (outline), radius 12px.
- **Forms** — inputs HTML puros (ver [Formularios: solo HTML](#formularios-solo-html-sin-django-forms)); labels claros, mensajes de error en tono suave.
- **Tablas** — filas alternas muy sutiles, sin bordes duros; en listados CRUD usar **DataTables** (ver abajo).
- **Modal global** — mensajes de error, éxito, aviso e info (ver abajo).

## Modal global de mensajes

**Regla obligatoria:** toda pantalla (pública, `/app/`, seguridad) incluye **un único modal global** para feedback al usuario. No usar `alert()` del navegador ni modales Bootstrap.

### Mejoras respecto al patrón Bootstrap de referencia

| Antes (ejemplo) | BAKEBUDGE |
|-----------------|-----------|
| Bootstrap Modal + jQuery | CSS/JS propio (`bakebudge-modal.*`) |
| Títulos en inglés | Títulos en **español** |
| Solo `ER` y `OK` | `ER`, `OK`, `AV`, `IN` |
| `innerHTML` sin control | Texto seguro por defecto (`textContent`); HTML solo si se pide explícitamente |
| Dependencia DataTables 1.x + jQuery | DataTables 2.x: API `new DataTable()`; **jQuery obligatorio** como dependencia del paquete |

### Tipos de mensaje

| Código | Uso | Título por defecto | Botón |
|--------|-----|-------------------|-------|
| `ER` | Error de validación, datos incorrectos, fallo de negocio | Error de validación | Cerrar |
| `OK` | Operación exitosa (guardar, eliminar, completar orden) | Operación exitosa | Aceptar |
| `AV` | Advertencias al usuario (datos desactualizados, confirmaciones suaves) | Atención | Entendido |
| `IN` | Información del sistema (mantenimiento, tips) | Información | Aceptar |

Errores **técnicos internos** (500, excepciones): mensaje genérico al usuario vía `ER`; detalle solo en logs del servidor.

### Archivos compartidos

| Archivo | Rol |
|---------|-----|
| `apps/core/static/css/bakebudge-modal.css` | Estilos pastel del modal |
| `apps/core/static/js/bakebudge-modal.js` | API `BakeBudgeModal` |
| `apps/core/templates/partials/modal_global.html` | Markup incluido en bases |

### Markup obligatorio (final de `<body>`)

Incluir en **cada** template base (`base.html`, `app_base.html`). Ver `apps/core/templates/partials/modal_global.html`.

### API JavaScript

```javascript
BakeBudgeModal.showError("El costo debe ser mayor que cero.");
BakeBudgeModal.showSuccess("Producto guardado correctamente.");
BakeBudgeModal.showWarning("Algunos insumos tienen precios desactualizados.");
BakeBudgeModal.showInfo("Nueva versión disponible en Noticias.");

BakeBudgeModal.show({
  type: "ER",
  title: "No se pudo guardar",
  message: "Revisa los campos marcados.",
});
```

Cerrar programáticamente: `BakeBudgeModal.close()`.

### Integración Django (template base)

Variables de contexto (convención):

| Variable | Descripción |
|----------|-------------|
| `message_modal` | Texto del mensaje (cadena vacía = no mostrar) |
| `error_tipo` | `ER`, `OK`, `AV` o `IN` |

```html
<body
  data-modal-type="{{ error_tipo|default:'' }}"
  data-modal-message="{{ message_modal|default:'' }}"
>
```

El script `bakebudge-modal.js` muestra el modal automáticamente en `DOMContentLoaded` si `data-modal-message` no está vacío.

**Vista (ejemplo):**

```python
def producto_create(request):
    if not request.POST.get("nombre"):
        return render(request, "catalog/producto_form.html", {
            "error_tipo": "ER",
            "message_modal": "El nombre del producto es obligatorio.",
        })
    # ...
    return render(request, "catalog/producto_list.html", {
        "error_tipo": "OK",
        "message_modal": "Producto creado correctamente.",
    })
```

Alternativa: helper en `apps/core/messages.py` que devuelve el dict `{error_tipo, message_modal}`.

### Accesibilidad y UX

- Cierre con botón, clic en backdrop, tecla **Escape**
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- Bloqueo de scroll del body mientras está abierto
- Responsive: ancho completo en móvil

### Checklist por pantalla

- [ ] Incluye CSS + markup + JS del modal global
- [ ] Errores de formulario vía modal (no solo texto inline)
- [ ] Mensajes post-redirect/render con `message_modal` + `error_tipo`

## Tablas (DataTables)

Listados de **Productos**, **Recetas**, **Órdenes de producción** y **Estadísticas** usan [**DataTables**](https://datatables.net/manual/) **2.x**. La API de inicialización es JavaScript (`new DataTable(...)`); **jQuery sigue siendo dependencia obligatoria** del paquete estándar — cargar antes del script DataTables. Ver [manual de instalación](https://datatables.net/manual/installation).

**Assets locales:** `apps/core/static/js/jquery.min.js`, `dataTables.min.js`, `datatables-init.js`, `css/dataTables.dataTables.min.css`, `i18n/datatables-es-ES.json`.

**Patrón en template Django:**

1. Vista renderiza `<table id="...">` con filas desde el queryset (server-side HTML).
2. Incluir **jQuery** + DataTables CSS/JS + `datatables-init.js` desde `{% static %}`.
3. Bloque `{% block extra_js %}` inicializa con `BakeBudgeDataTables.init(...)` o `initMarked()` para tablas con `data-datatable`.

**Ejemplo mínimo (defaults BAKEBUDGE):**

```html
<table id="tabla-productos" class="table-bakebudge">
  <thead>...</thead>
  <tbody>...</tbody>
</table>

<script src="{% static 'js/jquery.min.js' %}"></script>
<script src="{% static 'js/dataTables.min.js' %}"></script>
<script src="{% static 'js/datatables-init.js' %}"></script>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    BakeBudgeDataTables.init("#tabla-productos", {
      order: [[0, "asc"]],
    });
  });
</script>
```

**Listados genéricos** (recetas, producción, estadísticas): añadir `data-datatable` a la tabla; `main.js` llama `BakeBudgeDataTables.initMarked()`.

**Convenciones BAKEBUDGE:**

| Tema | Decisión |
|------|----------|
| Referencia | [Manual DataTables](https://datatables.net/manual/) |
| Inicialización | `BakeBudgeDataTables` en `apps/core/static/js/datatables-init.js` — no duplicar opciones en cada pantalla |
| Clase CSS tabla | `table-bakebudge` + estilos en `datatables-theme.css` |
| Idioma | Español (`es-ES`) |
| **Registros por página (default)** | **10** |
| **Opciones de cantidad** | **10 · 20 · 50** (`pageLength` + `lengthMenu`) |
| Selector de cantidad | Visible (`layout.topStart: pageLength`) |
| Acciones por fila | Columna final con links Django (editar, ver); no AJAX en v1 salvo necesidad |
| Datos sensibles | Queryset ya filtrado por `owner` en vista; DataTables solo ordena/filtra en cliente |
| Listados muy grandes | Valorar [server-side processing](https://datatables.net/manual/server-side) en fase posterior |

Documentación oficial: https://datatables.net/manual/

## Copys de marca

**Tono:** cercano, práctico, orientado a emprendedoras de repostería.

**Ejemplos:**
- *"Conoce el costo real de cada postre"*
- *"Tus recetas, tus números"*
- *"De la masa al margen, en un solo lugar"*

## Archivos de implementación

- `apps/core/static/css/tokens.css` — variables CSS.
- `apps/core/static/css/bakebudge-modal.css` — modal global de mensajes.
- `apps/core/static/js/bakebudge-modal.js` — API `BakeBudgeModal`.
- `apps/core/static/css/datatables-theme.css` — DataTables alineado a tokens pastel.
- `apps/core/static/js/datatables-init.js` — defaults BAKEBUDGE (`pageLength: 10`, `lengthMenu: [10, 20, 50]`).
- `apps/core/templates/base.html` — layout base compartido; includes DataTables CSS/JS en zona `/app/`.
- Templates separados: `apps/public_site/` (landing) vs app privada.
