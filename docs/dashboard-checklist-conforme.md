# Checklist Conforme — Dashboard (`apps.dashboard`)

**Estado global: CERRADO — Conforme (prototipo 2026-06-16 · Django v1 2026-06-16).**

Validación OK de la pantalla home `/app/` y reglas de layout compartidas en la zona privada.

**Reglas:** [`dashboard-reglas.md`](dashboard-reglas.md)  
**Template Django:** `apps/dashboard/templates/dashboard/home.html` · **URL:** `/app/`

```bash
cd BAKEBUDGE
.venv\Scripts\python.exe manage.py runserver
# http://127.0.0.1:8000/app/
# Master demo: usuario con user_type=M
```

---

## Pantalla principal

| Ítem | Archivo | Revisado | Conforme |
|------|---------|----------|----------|
| Dashboard home | `dashboard.html` | ☑ | **Conforme** |
| Layout compartido | `css/bakebudge-app.css` | ☑ | **Conforme** |
| Nav / sidebar demo | `js/main.js` | ☑ | **Conforme** |

---

## Bloques de contenido (`dashboard.html`)

| Bloque | Origen modelo (Django) | Django v1 |
|--------|------------------------|-----------|
| KPI Productos activos | `Producto` (`owner`, activo) | `get_dashboard_summary` ☑ |
| KPI Recetas | `Receta` | `get_dashboard_summary` ☑ |
| KPI Órdenes del mes | `OrdenProduccion` | `get_dashboard_summary` ☑ |
| KPI Margen promedio | `ProduccionAnalytics` (`AVG(margen_real_pct)`) | `get_dashboard_summary` ☑ |
| Primeros pasos | Onboarding owner | Enlaces reales ☑ |
| Producción reciente | `OrdenProduccion` (últimas 5) | Tabla + enlace detalle ☑ |

> En Django los KPIs se calculan con `get_dashboard_summary(user)` en `apps/dashboard/services/summary.py`. Tarjetas y checklist enlazan a catálogo, recetas, producción y estadísticas.

---

## Criterios globales (layout `/app/`)

- [x] Sidebar orden fijo + Catálogo base + Noticias + Administración Master
- [x] Topbar **`nombre_negocio`** (chip pastel) + pie `UserProfile` + **Cerrar sesión** — **Conforme v1.1** (2026-06-26)
- [x] Regla **datos por `request.user`** documentada
- [x] Responsivo 375 / 768 / 1140 px
- [x] Modal global en pantalla
- [x] `[data-master-only]` + `?user_type=M` en demo
- [x] Navegación enlazada al resto de módulos Conforme

---

## Fuera de alcance v1 (documentado)

| Ítem | Notas |
|------|-------|
| KPIs dinámicos en JS prototipo | No requerido; demo estático OK |
| **Ayuda General** (sidebar) | Módulo aparte — [`ayuda-reglas.md`](ayuda-reglas.md) |
| Widget últimas noticias en dashboard | Opcional — fase posterior |

---

## Cierre aplicado

1. ✅ `dashboard-reglas.md` → **Conforme**
2. ✅ `prototype/README.md`, `fase-1b-landing.md` → actualizados

---

## Registro de aprobaciones

| Fecha | Bloque | Notas |
|-------|--------|-------|
| 2026-06-16 | Dashboard home + layout `/app/` | Validación OK — Conforme |
| 2026-06-16 | Django v1 KPIs reales + enlaces cruzados | `get_dashboard_summary` — Conforme |
| 2026-06-26 | Topbar `nombre_negocio` chip pastel — Conforme v1.1 |
