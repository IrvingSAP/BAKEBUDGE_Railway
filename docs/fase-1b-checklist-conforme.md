# Checklist Conforme — Cierre Fase 1b (zona pública + zona privada `/app/`)

**Estado global: CERRADO — Conforme v1 (2026-06-16).** Incluye **Ayuda General** (`/app/ayuda/`) desde 2026-06-16.

Lista de verificación **única** que consolida el cierre de la Fase 1b: landing pública, acceso, layout `/app/`, catálogo, ciclo de negocio (recetas → producción → estadísticas), administración Master, noticias y perfil.

**Plan de seguimiento:** [`fase-1b-landing.md`](fase-1b-landing.md)  
**Roadmap:** [`roadmap.md`](roadmap.md)  
**Modelos v1:** [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md)

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py test --verbosity=0
# Esperado: System check OK · Ran 65 tests · OK
```

| Área | URL Django (referencia) |
|------|-------------------------|
| Landing | `/` · `/servicios/` · `/contacto/` |
| Acceso | `/ingresar/` |
| Dashboard | `/app/` |
| Catálogo | `/app/productos/` · categorías · conversiones · costos indirectos |
| Recetas | `/app/recetas/` |
| Producción | `/app/produccion/` |
| Estadísticas | `/app/estadisticas/` |
| Noticias | `/app/noticias/` |
| Perfil | `/app/perfil/` |
| Administración Master | `/app/administracion/…` |

---

## Bloque A — Zona pública — **Conforme**

**Checklist detallado:** [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md)

| # | Ítem | Estado |
|---|------|--------|
| A1 | Landing home, servicios, contacto (Django `apps.public_site`) | **Conforme v1** |
| A2 | Formulario contacto `POST` + modelo `MensajeContacto` | **Conforme** |
| A3 | Gestión Master mensajes contacto | **Conforme** |
| A4 | Modal global + responsive + tokens UI | **Conforme** |

---

## Bloque B — Acceso y seguridad — **Conforme**

**Checklist detallado:** [`acceso-checklist-conforme.md`](acceso-checklist-conforme.md)

| # | Ítem | Estado |
|---|------|--------|
| B1 | Login, confirmación correo, TOTP | **Conforme v1.2** |
| B2 | Primer acceso → Noticias | **Conforme v1.2** |
| B3 | Seguridad de la cuenta (contraseña + reset 2FA) | **Conforme v1** — [`cuenta-seguridad-checklist-conforme.md`](cuenta-seguridad-checklist-conforme.md) |

---

## Bloque C — Layout y dashboard — **Conforme**

**Checklists:** [`dashboard-checklist-conforme.md`](dashboard-checklist-conforme.md) · [`dashboard-reglas.md`](dashboard-reglas.md)

| # | Ítem | Estado |
|---|------|--------|
| C1 | `app_base.html` — sidebar, topbar, modal, logout | **Conforme** |
| C2 | Dashboard home con KPIs reales (`get_dashboard_summary`) | **Conforme v1** |
| C3 | Enlaces cruzados: catálogo, recetas, producción, estadísticas | **Conforme v1** |
| C4 | Producción reciente (últimas órdenes + enlace detalle) | **Conforme v1** |
| C5 | Regla datos por `request.user` activa en apps migradas | **Conforme** |

---

## Bloque D — Catálogo base — **Conforme**

**Checklist detallado:** [`catalog-checklist-conforme.md`](catalog-checklist-conforme.md)

| # | Ítem | Estado |
|---|------|--------|
| D1 | Productos, categorías, conversiones, costos indirectos | **Conforme v1** |
| D2 | CRUD + ayudas + DataTables | **Conforme v1** |

---

## Bloque E — Recetas — **Conforme**

**Checklist detallado:** [`recetas-checklist-conforme.md`](recetas-checklist-conforme.md) (bloque F Django)

| # | Ítem | Estado |
|---|------|--------|
| E1 | CRUD cabecera + versión inicial v1 | **Conforme v1** |
| E2 | Formulación RecetaVersion (ingredientes, indirectos, pasos, precio) | **Conforme v1** |
| E3 | Versionado + historial + detalle readonly | **Conforme v1** |
| E4 | Vista costos + enlace **Producir** | **Conforme v1** |
| E5 | Tests `apps.recipes` | **Conforme** |

---

## Bloque F — Producción — **Conforme**

**Checklist detallado:** [`produccion-checklist-conforme.md`](produccion-checklist-conforme.md) (bloque F Django)

| # | Ítem | Estado |
|---|------|--------|
| F1 | CRUD planificación + ayudas | **Conforme v1** |
| F2 | Ciclo borrador → en_proceso → completada/cancelada | **Conforme v1** |
| F3 | Costo estimado congelado al iniciar | **Conforme v1** |
| F4 | Detalle escalado + override precio al completar | **Conforme v1** |
| F5 | Tests `apps.production` | **Conforme** |

---

## Bloque G — Estadísticas (analytics) — **Conforme**

**Checklists:** [`estadisticas-checklist-conforme.md`](estadisticas-checklist-conforme.md) · [`BAKEBUDGE_ANALYTICS.md`](BAKEBUDGE_ANALYTICS.md)

| # | Ítem | Estado |
|---|------|--------|
| G1 | Modelos + snapshot al completar orden (signal) | **Conforme v1** |
| G2 | Vista `/app/estadisticas/` — KPIs, rankings, filtros, tabla | **Conforme v1** |
| G3 | Servicio `get_estadisticas_summary` | **Conforme v1** |
| G4 | Dashboard consume `AVG(margen_real_pct)` | **Conforme v1** |
| G5 | Tests `apps.analytics` | **Conforme** |

---

## Bloque H — Noticias — **Conforme**

**Checklists:** [`noticias-checklist-conforme.md`](noticias-checklist-conforme.md) · [`administracion-noticias-checklist-conforme.md`](administracion-noticias-checklist-conforme.md)

| # | Ítem | Estado |
|---|------|--------|
| H1 | Feed `/app/noticias/` | **Conforme v1.2** |
| H2 | CRUD Master + copiar noticia | **Conforme v1.2** |

---

## Bloque I — Perfil y administración Master — **Conforme**

| # | Ítem | Checklist | Estado |
|---|------|-----------|--------|
| I1 | Perfil negocio + unidades | [`perfil-checklist-conforme.md`](perfil-checklist-conforme.md) | **Conforme v1** |
| I2 | Usuarios Master | [`administracion-usuarios-checklist-conforme.md`](administracion-usuarios-checklist-conforme.md) | **Conforme v1** |
| I3 | Facturación / PaymentControl | [`administracion-facturacion-checklist-conforme.md`](administracion-facturacion-checklist-conforme.md) | **Conforme v1.1** |
| I4 | Monedas Master | [`administracion-monedas-checklist-conforme.md`](administracion-monedas-checklist-conforme.md) | **Conforme v1** |

---

## Bloque J — Infraestructura transversal — **Conforme**

| # | Ítem | Estado |
|---|------|--------|
| J1 | `INSTALLED_APPS`: core, accounts, security, public_site, dashboard, catalog, administration, billing, noticias, recipes, production, analytics | **Conforme** |
| J2 | URLs en `config/urls.py` para todos los módulos anteriores | **Conforme** |
| J3 | Sidebar activo: Dashboard → Estadísticas (sin `is-pending`) | **Conforme v1** |
| J4 | Modal global en zona pública y `/app/` | **Conforme** |
| J5 | Formularios HTML puro (sin `django.forms` en UI) | **Conforme** |
| J6 | DataTables en listados migrados | **Conforme** |
| J7 | Suite de tests automatizados (65 tests, jun 2026) | **Conforme** |

---

## Ayuda General — **CERRADA Conforme v1**

| # | Ítem | Estado |
|---|------|--------|
| X1 | Template `apps/ayuda/templates/ayuda/home.html` · `/app/ayuda/` | **Conforme v1** |
| X2 | Reglas cerradas | [`ayuda-reglas.md`](ayuda-reglas.md) — **Conforme** |
| X3 | App Django `apps.ayuda` + enlace sidebar | **Conforme v1** |

> Cierre documentado en Fase 1b; no quedan tareas pendientes de Ayuda General en v1.

---

## Fuera de alcance Fase 1b (backlog documentado)

| Ítem | Doc | Notas |
|------|-----|-------|
| Gate `can_access_app` completo | Fase 1c | Modelo `PaymentControl` ✓ |
| `costo_real` vs estimado | [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) | No prioritario |
| Inventario / stock | Extensiones futuras | — |
| `ResumenMensual` / Chart.js | [`BAKEBUDGE_ANALYTICS.md`](BAKEBUDGE_ANALYTICS.md) | Post-v1 |
| Email producción contacto / anti-spam | Zona pública v2 | — |
| Blog/recetas públicas SEO | Fase 5 | — |

---

## Cierre aplicado

1. ✅ Zona pública Django — [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md)
2. ✅ Acceso + primer acceso Noticias — [`acceso-checklist-conforme.md`](acceso-checklist-conforme.md)
3. ✅ Layout `/app/` + dashboard KPIs — [`dashboard-checklist-conforme.md`](dashboard-checklist-conforme.md)
4. ✅ Catálogo base — [`catalog-checklist-conforme.md`](catalog-checklist-conforme.md)
5. ✅ Recetas Django — [`recetas-checklist-conforme.md`](recetas-checklist-conforme.md)
6. ✅ Producción Django — [`produccion-checklist-conforme.md`](produccion-checklist-conforme.md)
7. ✅ Estadísticas Django — [`estadisticas-checklist-conforme.md`](estadisticas-checklist-conforme.md)
8. ✅ Noticias + administración Master — checklists v1.2
9. ✅ Perfil + seguridad cuenta — checklists v1
10. ✅ Modelos v1 implementados — [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md)
11. ✅ Ayuda General — [`ayuda-reglas.md`](ayuda-reglas.md)

---

## Registro de aprobaciones

| Fecha | Alcance | Notas |
|-------|---------|-------|
| 2026-06-16 | Prototipo zona privada (`prototype_app/`) | Conforme — bloques A–E por módulo |
| 2026-06-20 | Zona pública + acceso + catálogo + perfil + Master | Conforme v1 |
| 2026-06-16 | Recetas + Producción + Estadísticas Django | Conforme v1 — UI + servicios + tests |
| 2026-06-16 | **Cierre formal Fase 1b** | Conforme v1 (incluye Ayuda General) |
| 2026-06-16 | **Ayuda General Django** (`apps.ayuda`) | Conforme v1 — `/app/ayuda/` |
