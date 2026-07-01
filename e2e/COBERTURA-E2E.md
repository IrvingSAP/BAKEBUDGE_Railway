# BAKEBUDGE — Cobertura de pruebas E2E (Playwright)

**Estado:** todas las pruebas ejecutadas **OK** (junio 2026).  
**Herramienta:** [Playwright](https://playwright.dev/) — suite en `BAKEBUDGE/e2e/`.  
**Total aproximado:** **166 casos** repartidos en **14 archivos** `.spec.ts`.

**Trazabilidad documentación:** [`docs/README.md`](../docs/README.md) · [`docs/setup-desarrollo-checklist.md`](../docs/setup-desarrollo-checklist.md) (Fase 10) · [`docs/setup.md`](../docs/setup.md)

---

## Ejecución

```powershell
cd BAKEBUDGE\e2e
npm install          # primera vez
npm test             # suite completa
npm test tests/catalog.spec.ts   # un módulo
npm run report       # informe HTML
```

### Variables de entorno

| Variable | Obligatoria | Uso |
|----------|-------------|-----|
| `PLAYWRIGHT_E2E_USER` | Sí (tests `/app/`) | Usuario **Master** con acceso a `/app/` |
| `PLAYWRIGHT_E2E_PASSWORD` | Sí | Contraseña del usuario E2E |
| `PLAYWRIGHT_E2E_TOTP_SECRET` | Sí | Secreto TOTP (2FA ya configurado) |
| `PLAYWRIGHT_BASE_URL` | No | URL base (default `http://127.0.0.1:8000`) |
| `PLAYWRIGHT_SKIP_WEBSERVER` | No | `1` si Django ya corre en otra terminal |

Plantilla: `e2e/.env.example`.

### Tipos de prueba

- **Anónimas:** zona pública (`/`, `/servicios/`, `/contacto/`, smoke).
- **Autenticadas:** requieren login + TOTP vía `helpers/auth.ts`.
- **Condicionales:** usan `test.skip` cuando no hay filas en tablas (p. ej. sin órdenes de producción).

---

## Resumen por app Django

| App Django | Archivo(s) spec | Casos | Rutas / pantallas principales |
|------------|-----------------|------:|--------------------------------|
| `apps.accounts` | `accounts.spec.ts` | 14 | `/app/perfil/`, `/app/seguridad/cuenta/` |
| `apps.administration` | `administration.spec.ts` | 11 | Monedas, usuarios, facturación, gestión noticias, mensajes contacto |
| `apps.analytics` | `analytics.spec.ts` | 9 | `/app/estadisticas/` |
| `apps.ayuda` | `ayuda.spec.ts` | 10 | `/app/ayuda/` |
| `apps.billing` | `billing.spec.ts` | 12 | `/app/administracion/facturacion/` (`PaymentControl`) |
| `apps.catalog` | `catalog.spec.ts` | 21 | Productos, categorías, conversiones, costos indirectos |
| `apps.core` | `core.spec.ts` | 17 | Layout `app_base`, modal, validación, toggle contraseña, `Moneda` |
| `apps.dashboard` | `dashboard.spec.ts` | 11 | `/app/`, `/app/acceso-denegado/` |
| `apps.noticias` | `noticias.spec.ts` + bloque en `administration.spec.ts` | 11 + 2 | Feed `/app/noticias/`, detalle; gestión Master en administración |
| `apps.production` | `production.spec.ts` | 13 | `/app/produccion/` (listado, alta, detalle, edición) |
| `apps.public_site` | `public_site.spec.ts`, `landing.spec.ts`, `smoke.spec.ts` | 22 | `/`, `/servicios/`, `/contacto/` |
| `apps.recipes` | `recipes.spec.ts` | 15 | `/app/recetas/`, formulación, costos, versiones |
| `apps.security` | `smoke.spec.ts` (+ login en todos los specs autenticados) | 1 explícito | `/ingresar/` |

---

## Detalle por archivo

### `smoke.spec.ts` (2) — humo general

- Landing carga con título BAKEBUDGE.
- Página de ingreso `/ingresar/` accesible.

### `landing.spec.ts` (7) — `public_site` home

- Hero, CTA «Solicitar acceso», estadísticas del hero.
- Sección servicios (6 tarjetas).
- Sección «cómo funciona» (4 pasos).
- Galería `#recetas`.
- CTA final `#contacto`.
- Cabecera global (Inicio, Servicios, Contacto, Entrar).
- Navegación hero → contacto con formulario visible.

### `public_site.spec.ts` (13)

- Footer, modal global, menú móvil.
- `data-page` en home.
- **Servicios:** cabecera, 6 capacidades, CTA inferior.
- **Contacto:** cabecera, mailto, formulario, validación error, envío éxito.
- Navegación cabecera (Servicios ↔ Inicio, Entrar → ingreso).

### `accounts.spec.ts` (14) — `apps.accounts`

- Acceso sin sesión → login (perfil, seguridad).
- **Perfil:** cabecera, datos del negocio, unidades, guardar, enlace seguridad.
- **Seguridad cuenta:** aviso 2FA, campos contraseña, toggles, confirmación, volver al perfil.

### `administration.spec.ts` (11) — `apps.administration` (Master)

- Acceso sin sesión.
- Sidebar Administración (monedas, usuarios, facturación, noticias, mensajes).
- **Monedas:** listado, alta.
- **Usuarios:** listado, alta + ayuda.
- **Facturación:** listado, alta (resumen; detalle en `billing.spec.ts`).
- **Gestión noticias:** listado, alta.
- **Mensajes contacto:** listado.

### `analytics.spec.ts` (9) — `apps.analytics`

- Acceso sin sesión.
- Cabecera, filtros GET (periodo, receta, categoría).
- KPIs, widgets ranking/evolución, tabla detalle.
- Estado vacío o filas, limpiar filtros, sidebar Estadísticas.

### `ayuda.spec.ts` (10) — `apps.ayuda`

- Acceso sin sesión.
- Cabecera, panorama 3 fases, enlaces saltar, scroll interno.
- Secciones 1–4 (catálogo, recetas, análisis, noticias) con enlaces a módulos.
- Sidebar Ayuda General.

### `billing.spec.ts` (12) — `apps.billing`

- Acceso sin sesión.
- Sidebar Facturación.
- Listado: cabecera, filtros, tabla, limpiar, query `?owner=`.
- Alta: formulario completo, ayuda.
- Edición, ayuda edición, acción suspender/cancelar (si hay datos).

### `catalog.spec.ts` (21) — `apps.catalog`

- Acceso sin sesión (4 rutas: productos, categorías, conversiones, costos indirectos).
- Sidebar Productos y submenú Catálogo base.
- Por módulo: listado (cabecera, filtros, tabla, limpiar), alta + ayuda, edición; productos incluye eliminar.

### `core.spec.ts` (17) — `apps.core`

- Acceso `/app/` sin sesión.
- Layout `app_base`: sidebar, topbar, modal, `data-page`, logout, toggle móvil.
- `BakeBudgeModal`: error, éxito, cierre.
- `BakeBudgeFormErrors`: campos inválidos.
- Password toggle (seguridad cuenta).
- **Moneda (`core_moneda`):** selector en perfil, CRUD administración (listado, alta, edición COP, eliminar).

### `dashboard.spec.ts` (11) — `apps.dashboard`

- Acceso sin sesión.
- Post-login en dashboard, cabecera, 4 KPIs con enlaces.
- Navegación KPI → productos / estadísticas.
- Primeros pasos, producción reciente, sidebar Dashboard.
- Acceso denegado (sin sesión y con sesión).

### `noticias.spec.ts` (11) — `apps.noticias` (usuario)

- Acceso feed y detalle sin sesión.
- Feed: cabecera, vacío o tarjetas, «Leer más», sidebar.
- Detalle: 404, cabecera/cuerpo/volver, enlaces opcionales.
- Tarjetas sin detalle: enlace externo/interno.

### `production.spec.ts` (13) — `apps.production`

- Acceso listado, nueva orden, detalle sin sesión.
- Listado: cabecera, filtros, tabla, limpiar, sidebar Producción.
- Alta: formulario, vista previa, ayuda.
- Detalle (Ver), acciones por estado, edición borrador, ayuda edición.

### `recipes.spec.ts` (15) — `apps.recipes`

- Acceso listado y alta sin sesión.
- Listado: cabecera, filtros, tabla, limpiar, sidebar Recetas.
- Alta cabecera v1 + ayuda; edición; eliminar (inactivar/permanente).
- Formulación vigente + ayuda; costos; historial versiones; detalle versión; nueva versión; enlace Producir.

---

## Matriz app → URL probada

| App | URLs E2E |
|-----|----------|
| accounts | `/app/perfil/`, `/app/seguridad/cuenta/` |
| administration | `/app/administracion/monedas/`, `…/usuarios/`, `…/facturacion/`, `…/noticias/`, `…/mensajes-contacto/` |
| analytics | `/app/estadisticas/` |
| ayuda | `/app/ayuda/` |
| billing | `/app/administracion/facturacion/` (+ alta/edición/acción) |
| catalog | `/app/productos/`, `/app/categorias/`, `/app/conversiones/`, `/app/costos-indirectos/` |
| core | Layout en `/app/*`, monedas en `/app/administracion/monedas/` |
| dashboard | `/app/`, `/app/acceso-denegado/` |
| noticias | `/app/noticias/`, `/app/noticias/<id>/` |
| production | `/app/produccion/`, `…/nueva/`, `…/<pk>/`, `…/<pk>/editar/` |
| public_site | `/`, `/servicios/`, `/contacto/` |
| recipes | `/app/recetas/`, `…/nuevo/`, `…/<pk>/editar/`, `…/costos/`, `…/version/`, `…/versiones/` |
| security | `/ingresar/` (smoke); flujo login+TOTP en specs autenticados |

---

## Notas

1. **`administration.spec.ts`** y **`billing.spec.ts`** / **`core.spec.ts`** se solapan en Monedas y Facturación: administration cubre flujos resumidos; billing y core profundizan `PaymentControl` y `core_moneda`.
2. **`landing.spec.ts`** y **`public_site.spec.ts`** comparten la home: landing prueba secciones de marketing; public_site prueba layout y rutas secundarias.
3. Los tests **no sustituyen** los tests unitarios Django (`apps/*/tests.py`); complementan la UI en navegador real (Chromium).
4. Re-ejecutar `npm test` tras cambios de plantillas, sidebar o flujos de login antes de desplegar.

---

*Última actualización: junio 2026 — suite E2E completa por app, todas las pruebas OK.*
