# Reglas del dashboard — zona `/app/`

**Estado:** **Conforme** — diseño aprobado; **Django v1 implementado** (2026-06-16).

Convenciones de layout, usuario, **aislamiento de datos** y cierre de sesión para la **zona privada** (dashboard y módulos autenticados).

**Checklist:** [`dashboard-checklist-conforme.md`](dashboard-checklist-conforme.md)  
**Template Django:** `apps/dashboard/templates/dashboard/home.html` · **URL:** `/app/`  
**Implementación Django:** `apps/core/templates/app_base.html`, `apps.dashboard`, `apps.accounts`  
**Relacionado:** [`ui-ux.md`](ui-ux.md), [`arquitectura.md`](arquitectura.md#aislamiento-de-datos), [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#userprofile)

---

## Regla fundamental: datos del usuario conectado

**Toda la información mostrada en pantallas bajo `/app/` pertenece al usuario autenticado** (`request.user`). Ningún listado, estadística, formulario ni detalle debe mezclar datos de otras cuentas.

| Capa | Regla |
|------|-------|
| **HTML / templates** | Solo renderizar variables del contexto ya filtradas por el usuario conectado |
| **Vistas Django** | Querysets con `owner=request.user` (o equivalente vía servicio) |
| **Formularios POST** | Al crear/editar, asignar `owner=request.user`; al editar/eliminar, comprobar que el registro pertenece al usuario |
| **Servicios** | Recibir `user` explícito; no consultar modelos sin filtro de owner |
| **DataTables** | Reciben filas ya acotadas al usuario; ordenan/filtran en cliente sobre ese subconjunto |
| **Templates Django** | Datos reales del usuario conectado (`request.user`) |

Esta regla aplica a **todos los procesos** de la zona privada: catálogo, recetas, producción, estadísticas, perfil y dashboard.

### Excepciones documentadas

| Contenido | Alcance | Motivo |
|-----------|---------|--------|
| **Noticias** (`/app/noticias/`) | Global (producto BAKEBUDGE) | Comunicaciones del sistema, no datos de negocio del usuario. Ver [`BAKEBUDGE_NOTICIAS.md`](BAKEBUDGE_NOTICIAS.md) |
| **Moneda** (catálogo de referencia) | Global de lectura | Tabla maestra; el usuario elige su preferida en `UserProfile` |
| **Landing pública** | Sin sesión / anónima | Fuera de `/app/` |

Todo lo demás en `/app/` es **privado por usuario**.

### Mapeo — `dashboard.html` (referencia)

En el prototipo los números son ficticios. En Django cada bloque se calcula solo con datos del usuario conectado:

| Bloque en pantalla | Origen (Django) | Filtro |
|--------------------|-----------------|--------|
| **Usuario** (topbar) | `User.username` | `request.user` |
| **Pie sidebar** (`nombre_negocio`, email) | `UserProfile`, `User.email` | `request.user` / `request.user.profile` |
| **Productos activos** | `Producto` | `owner=request.user`, `activo=True` |
| **Recetas** | `Receta` | `owner=request.user`; hint: versiones vigentes del mismo owner |
| **Órdenes del mes** | `OrdenProduccion` | `owner=request.user`, rango de fechas del mes actual |
| **Margen promedio** | `ProduccionAnalytics` o servicio dashboard | `owner=request.user`, agregación del periodo |
| **Primeros pasos** (checklist) | Lógica de onboarding | ¿Tiene productos? ¿Tiene recetas? — solo registros del owner |
| **Producción reciente** (tabla) | `OrdenProduccion` | `owner=request.user`, últimas N órdenes |

Misma regla en el resto de pantallas `/app/`:

| Pantalla | Template | Filtro owner |
|----------|----------|--------------|
| Productos | `catalog/productos/producto_list.html` | `Producto.owner` |
| Recetas | `recipes/receta_list.html` | `Receta.owner` |
| Producción | `production/orden_list.html` | `OrdenProduccion.owner` |
| Estadísticas | `analytics/estadisticas_home.html` | `ProduccionAnalytics.owner` (y derivados) |
| Perfil | `accounts/perfil.html` | `UserProfile.user` = `request.user` |
| Noticias | `noticias/feed.html` | **Sin owner** — noticias publicadas globalmente |

### Implementación Django (patrón obligatorio)

**Listados:**

```python
def producto_list(request):
    productos = Producto.objects.filter(owner=request.user, activo=True)
    return render(request, "catalog/producto_list.html", {"productos": productos})
```

**Detalle / edición / borrado** — nunca confiar solo en el ID de la URL:

```python
from django.shortcuts import get_object_or_404

producto = get_object_or_404(Producto, pk=pk, owner=request.user)
```

**Creación:**

```python
Producto.objects.create(owner=request.user, nombre=nombre, ...)
```

**Servicios** (recomendado para dashboard y estadísticas):

```python
# apps/dashboard/services/summary.py
def get_dashboard_summary(user):
    return {
        "productos_activos": ...,
        "recetas": ...,
        # OrdenProduccion, ProduccionAnalytics — ver summary.py
    }
```

**Prohibido:**

- Querysets sin filtro de owner en vistas `/app/`
- Mostrar totales globales de la plataforma al usuario estándar
- Editar un registro validando solo `pk` sin comprobar `owner`

Ver también [`arquitectura.md`](arquitectura.md#aislamiento-de-datos) y convención `owner → User` en [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md).

---

## Layout obligatorio

Toda pantalla bajo `/app/` comparte:

| Zona | Elemento | Descripción |
|------|----------|-------------|
| Izquierda | **Sidebar** | Navegación principal + pie con perfil + cerrar sesión |
| Superior derecha | **Usuario** | Identificador del usuario autenticado |
| Centro | **Contenido** | Título de página, cards, tablas |

Sidebar (orden fijo):

1. Dashboard  
2. Productos  
3. Recetas  
4. Producción  
5. Estadísticas  
6. **Catálogo base** (submenú desplegable)  
   - Categorías → `ProductCategory`  
   - Conversiones de unidad → `ConversionUnidad`  
7. Perfil  
8. Noticias  
9. **Ayuda General** — guía del ciclo y flujo del sistema ([`ayuda-reglas.md`](ayuda-reglas.md); **Conforme v1** — `/app/ayuda/`)  
10. *(línea en blanco)*  
11. **Administración** (submenú desplegable; **solo Master**)  
    - Usuarios  
    - Facturación  
    - Gestión noticias  
    - Mensajes contacto  

El submenú **Catálogo base** usa `<button>` + lista anidada (`.app-nav-group` / `.app-nav-sub`); se expande al clic y permanece abierto cuando la pantalla activa es categorías, conversiones o costos indirectos (`data-page` en `body`).

### Sección Administración (solo Master)

| Regla | Detalle |
|-------|---------|
| Visibilidad | Solo si `UserProfile.user_type = 'M'` (Master) |
| Ubicación | Después de **Noticias**, precedida por separador (`.app-nav-separator`) |
| Submenú | **Usuarios**, **Facturación**, **Gestión noticias**, **Mensajes contacto** — mismo patrón que Catálogo base |
| Prototipo | Elementos con `[data-master-only]` ocultos por defecto; demo Master con `?user_type=M` en la URL |
| Django | Renderizar el bloque solo cuando `request.user.profile.user_type == 'M'`; proteger URLs con la misma comprobación |
| Reglas Usuarios | [`usuarios-reglas.md`](usuarios-reglas.md) |
| Reglas Facturación | [`facturacion-reglas.md`](facturacion-reglas.md) |
| Reglas Noticias (CRUD) | [`noticias-reglas.md`](noticias-reglas.md) |
| Mensajes contacto (gestión) | [`mensajecontacto-reglas.md`](mensajecontacto-reglas.md) |
| Ayuda General (guía ciclo) | [`ayuda-reglas.md`](ayuda-reglas.md) — **Conforme v1** |

---

## Usuario (esquina superior derecha)

| Regla | Detalle |
|-------|---------|
| Etiqueta | Texto fijo **«Usuario»** (`.app-user-label`) |
| Valor mostrado | **`User.username`** de Django (`django.contrib.auth.models.User`) |
| Fuente en código | `request.user.username` |
| App | Cuenta en `auth.User`; perfil extendido en `apps.accounts.UserProfile` |
| Prototipo | `[data-user-username]` — demo en `js/main.js` |

**No confundir:**

- **Usuario (topbar)** → login `User.username`  
- **Pie del sidebar** → datos de negocio del `UserProfile` (ver abajo)

### Markup (prototipo / template)

```html
<div class="app-user">
  <span class="app-user-label">Usuario</span>
  <strong class="app-user-name" data-user-username>{{ user.username }}</strong>
</div>
```

En Django: `user` del context processor de auth o `request.user` en la vista.

---

## Pie del sidebar (UserProfile)

Debajo del menú, antes de **Cerrar sesión**:

| Campo mostrado | Origen | Modelo |
|----------------|--------|--------|
| Nombre del negocio | `UserProfile.nombre_negocio` | `apps.accounts.UserProfile` |
| Correo | `User.email` | `auth.User` (OneToOne con profile) |

### Markup

```html
<div class="app-sidebar-footer">
  <strong data-profile-business>{{ user.profile.nombre_negocio }}</strong>
  <span data-profile-email>{{ user.email }}</span>
  <a href="..." class="btn btn-outline btn-logout">Cerrar sesión</a>
</div>
```

Acceso en vistas: `request.user.profile` (signal post-registro crea el perfil).

---

## Cerrar sesión

| Regla | Detalle |
|-------|---------|
| Ubicación | **Final del menú lateral** (`.app-sidebar-footer`), último control visible |
| Texto del botón | **«Cerrar sesión»** |
| Clases CSS | `btn btn-outline btn-logout` |
| Django | POST a `{% url 'security:logout' %}` (p. ej. `/salir/`) → landing pública |

El botón debe estar presente en **todas** las pantallas `/app/` vía `app_base.html`.

### Template (referencia)

```html
<form method="post" action="{% url 'security:logout' %}">
  {% csrf_token %}
  <button type="submit" class="btn btn-outline btn-logout">Cerrar sesión</button>
</form>
```

Redirección post-logout: landing pública (`public_site:home` / `/`).

---

## Responsivo

| Viewport | Comportamiento |
|----------|----------------|
| Desktop | Sidebar fija; **Usuario** visible arriba a la derecha del contenido |
| Móvil (&lt; 768px) | Sidebar oculta (hamburguesa); topbar con marca + **Usuario**; cerrar sesión dentro del drawer lateral |

Ver [`ui-ux.md#diseño-responsivo-obligatorio`](ui-ux.md#diseño-responsivo-obligatorio).

---

## Archivos de referencia

| Archivo | Rol |
|---------|-----|
| `apps/dashboard/static/dashboard/css/bakebudge-app.css` | Estilos `.app-user`, `.btn-logout`, `.app-sidebar-footer` |
| `apps/dashboard/static/dashboard/js/main.js` | Nav activa; DataTables marcadas |
| `docs/dashboard-reglas.md` | Este documento |
| `docs/dashboard-checklist-conforme.md` | Checklist Conforme (cerrado 2026-06-16) |
| `apps/accounts/models.py` | `UserProfile` |
| `apps/core/templates/app_base.html` | Layout base Django |

---

## Checklist al añadir pantalla `/app/`

- [ ] Extiende layout con sidebar completo (ítems operativos + Catálogo base + Noticias + Ayuda General + footer)
- [ ] Incluye topbar con **Usuario** (`user.username`)
- [ ] Pie sidebar: `nombre_negocio` + email + **Cerrar sesión**
- [ ] **Datos de la pantalla filtrados por `request.user`** (owner o perfil del usuario conectado)
- [ ] POST de creación/edición asigna o valida owner antes de persistir
- [ ] Responsivo (sidebar colapsable en móvil)
- [ ] Sin `django.forms` en markup (solo HTML)
- [ ] Modal global (`bakebudge-modal`)
