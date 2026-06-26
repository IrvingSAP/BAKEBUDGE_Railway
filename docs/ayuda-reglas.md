# Reglas del módulo Ayuda General — guía del ciclo (`apps.ayuda`)

**Estado:** **Conforme v1** — Django en `/app/ayuda/`.

Guía **contextual y paso a paso** para que cualquier usuario autenticado entienda el **ciclo completo** de BakeBudge: catálogo base → recetas y producción → análisis y estadísticas, más el feed de **noticias**.

**Contenido base (fuente para HTML):** [`ayuda-contenido.md`](ayuda-contenido.md)  
**Relacionado:** [`flujos.md`](flujos.md), [`dashboard-reglas.md`](dashboard-reglas.md), [`ui-ux.md`](ui-ux.md)

---

## Alcance

| Incluye | No incluye |
|---------|------------|
| Menú lateral **Ayuda General** (User + Master) | Formularios ni campos editables |
| Tres secciones de ciclo + **Noticias** | Detalle de campos (cada `*_reglas.md` y `*_help.html`) |
| Flujo, apps, orden de pasos y enlaces al menú | CRUD, validaciones ni lógica de negocio |
| Vista de solo lectura bajo `/app/ayuda/` | Tutoriales en video o chat de soporte |
| | Contenido editable por Master en v1 |

---

## Estructura de contenido (4 secciones)

Definida en [`ayuda-contenido.md`](ayuda-contenido.md):

| # | Sección | Temas | Apps |
|---|---------|-------|------|
| **1** | **Catálogo base** | Perfil, Categorías, Conversiones, Costos indirectos | `accounts`, `catalog` |
| **2** | **Recetas y producción** | Productos, Recetas (versiones), Producción (órdenes) | `catalog`, `recipes`, `production` |
| **3** | **Análisis y estadísticas** | Snapshots, KPIs, márgenes, rankings, dashboard | `analytics`, `dashboard` |
| **4** | **Noticias** | Feed de comunicados, primer acceso, alcance global/personal | `noticias` |

---

## Diferencia con «Ayuda» de formularios

| | Ayuda de formulario (`*_help.html`) | Ayuda General |
|--|-------------------------------------|---------------|
| **Objetivo** | Cómo llenar esta pantalla | Cómo encaja todo el sistema |
| **Formato** | Página estática ligada al formulario | Guía por fases del ciclo |
| **Acceso** | Botón **Ayuda** en create/edit | Ítem fijo del sidebar |
| **Contenido** | Campos y reglas del módulo | Flujo, dependencias, orden recomendado |
| **Estado** | Conforme por módulo | **Prototipo conforme** |

---

## Acceso y menú

| Regla | Detalle |
|-------|---------|
| Visibilidad | Todos los usuarios con acceso a `/app/` |
| Ubicación sidebar | Después de **Noticias**, antes del separador **Administración** |
| Etiqueta | **Ayuda General** |
| URL Django (propuesta) | `/app/ayuda/` |
| Template Django | `apps/ayuda/templates/ayuda/home.html` · `/app/ayuda/` |
| `data-nav` | `ayuda-general` |

---

## Naturaleza de la pantalla

**Solo lectura.** Sin `<form>`, sin POST, sin DataTables de datos del usuario.

Patrones UI (decisión en prototipo):

- Tres bloques (secciones 1–3): acordeón, cards o timeline
- Pasos numerados dentro de cada bloque
- Diagramas de flujo estáticos (ver [`ayuda-contenido.md`](ayuda-contenido.md))
- Enlaces «Ir a …» a rutas del menú
- Layout: `app_base` + `bakebudge-app.css`; CSS opcional `ayuda.css`

---

## Implementación Django — **Conforme v1**

| Capa | Propuesta |
|------|-----------|
| App | `apps.ayuda` — vista `ayuda_home`, template estático |
| Modelo BD | Ninguno en v1 — contenido en template |
| Auth | Misma cadena que resto `/app/` (`login` + acceso app) |
| Contenido | Portar secciones de [`ayuda-contenido.md`](ayuda-contenido.md) |

**Fuera de alcance v1:** CMS Master, tooltips contextuales, PDF, i18n.

---

## Checklist de diseño

- [x] Documento base de contenido — [`ayuda-contenido.md`](ayuda-contenido.md)
- [x] Prototipo HTML confirmado
- [x] `ayuda_home.html` (solo lectura)
- [x] Sidebar + `update-nav.py`
- [x] CSS mínimo (`ayuda.css`)
- [x] Django `apps.ayuda` + checklist conforme
- [x] Cierre documentado en [`fase-1b-checklist-conforme.md`](fase-1b-checklist-conforme.md)

---

## Archivos

| Archivo | Rol |
|---------|-----|
| `docs/ayuda-contenido.md` | **Contenido** — fuente para HTML |
| `docs/ayuda-reglas.md` | Reglas de módulo y alcance |
| `apps/ayuda/templates/ayuda/home.html` | **Conforme v1** |
| `apps/ayuda/` | App Django **Conforme v1** |
