# Roadmap — BAKEBUDGE

## Fases

| Fase | Entregable | Prioridad | Estado |
|------|------------|-----------|--------|
| **0 — Docs + Scaffold** | Docs ✓, [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) ✓, Django + PostgreSQL local ✓ | Inmediata | **Completado** — [`setup-desarrollo-checklist.md`](setup-desarrollo-checklist.md) |
| **1a — Seguridad** | App `security`: registro, login, correo, TOTP, reset 2FA | Alta | Docs ✓ |
| **1b — Pública + Dashboard** | Landing Django, layout `/app/`, modal global, módulos operativos v1 | Alta | **CERRADO Conforme v1** — [`fase-1b-checklist-conforme.md`](fase-1b-checklist-conforme.md) |
| **1c — Billing** | PaymentControl, gate `can_access_app`, Master confirma pago | Alta | Modelo ✓ · gate parcial |
| **2 — Catálogo** | Producto, ConversionUnidad, CRUD completo | Alta | **Conforme v1** — [`catalog-checklist-conforme.md`](catalog-checklist-conforme.md) |
| **3 — Recetas** | Receta, versiones, ingredientes, pasos, calculadora de costos | Alta | **Conforme v1** — [`recetas-checklist-conforme.md`](recetas-checklist-conforme.md) |
| **4 — Producción + Analytics** | OrdenProduccion, snapshots, estadísticas | Media | **Conforme v1** — [`produccion-checklist-conforme.md`](produccion-checklist-conforme.md) · [`estadisticas-checklist-conforme.md`](estadisticas-checklist-conforme.md) |
| **5 — Contenido** | Blog/recetas públicas, SEO, ilustraciones finales | Media | Pendiente |

## Pendientes documentados (backlog)

| Ítem | Entregable | Doc | Estado |
|------|------------|-----|--------|
| **Ayuda General** | Guía paso a paso del ciclo (`/app/ayuda/`), sidebar, solo lectura | [`ayuda-reglas.md`](ayuda-reglas.md) | **Conforme v1** |
| **App Noticias** | Modelo `Noticia`, feed, CRUD Master + Copiar, primer acceso → Noticias | [`BAKEBUDGE_NOTICIAS.md`](BAKEBUDGE_NOTICIAS.md) | **Conforme v1.2** |
| **Zona pública Django** | Landing + contacto + gestión Master | [`public-site-checklist-conforme.md`](public-site-checklist-conforme.md) | **Conforme v1** |
| **Recetas / Producción / Estadísticas Django** | UI completa bajo `/app/` + tests | [`fase-1b-landing.md`](fase-1b-landing.md) | **Conforme v1** (2026-06-16) |
| **`costo_real` en órdenes** | Costo real vs estimado con inventario | [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#ordenproduccion) | **Pendiente** — no prioritario |
| **Despliegue producción** | Railway Basic + PostgreSQL + Resend | [`deploy-railway-plan.md`](deploy-railway-plan.md) | **Pendiente** |

## Alcance "base del sistema"

Fases 0 + 1 + esqueleto de modelos (migraciones) de Fases 2–3, con UI mínima de prueba.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Conversiones de unidades incorrectas | Catálogo de unidades permitidas + validación; conversiones explícitas por producto |
| Costos desactualizados | Recalcular al editar producto o al abrir receta; aviso si precio del insumo cambió |
| Scope creep (blog, API) | Roadmap estricto; modelos según [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) |
| User sin pago en `/app/` | Gate `can_access_app` + PaymentControl |

## Próximos pasos

1. ~~Scaffold Django modular.~~ ✓
2. ~~PostgreSQL local + `.env`.~~ ✓
3. ~~Modelos v1 según [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md).~~ ✓
4. ~~App `security` — login, correo, TOTP.~~ ✓
5. ~~Catálogo, recetas, producción, analytics — UI Django.~~ ✓
6. ~~Ayuda General — app Django `/app/ayuda/`.~~ ✓ — [`ayuda-reglas.md`](ayuda-reglas.md)
7. App `billing` — gate `can_access_app` completo en runtime.
8. **Despliegue producción** — Railway + Resend ([`deploy-railway-plan.md`](deploy-railway-plan.md)).
