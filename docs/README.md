# BAKEBUDGE — Documentación

Repositorio central de documentación del proyecto **BAKEBUDGE**: web para gestionar recetas de repostería, costos de producción y órdenes.

## Índice

| Documento | Descripción |
|-----------|-------------|
| [arquitectura.md](arquitectura.md) | Estructura Django modular, apps y aislamiento por usuario |
| [modelos.md](modelos.md) | Resumen de entidades (legacy / índice rápido) |
| [BAKEBUDGE_MODELS.md](BAKEBUDGE_MODELS.md) | **Documento maestro** de modelos y relaciones |
| [BAKEBUDGE_ANALYTICS.md](BAKEBUDGE_ANALYTICS.md) | **Analytics de producción**: snapshots, márgenes, métricas dashboard |
| [BAKEBUDGE_SECURITY.md](BAKEBUDGE_SECURITY.md) | Flujos de registro, login, correo, 2FA y validaciones |
| [BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md](BAKEBUDGE_SECURITY_PORTABLE_GUIDE.md) | Guía técnica de implementación de seguridad |
| [flujos.md](flujos.md) | Flujos de registro, recetas, costos y producción |
| [ui-ux.md](ui-ux.md) | Sistema de diseño pastel, layout y copys de marca |
| [roadmap.md](roadmap.md) | Fases, prioridades y entregables |
| [deploy-railway-plan.md](deploy-railway-plan.md) | **Plan de tareas — despliegue Railway + Resend** (producción) |
| [dashboard-reglas.md](dashboard-reglas.md) | **Reglas del dashboard** — sidebar, Usuario, datos por usuario, Cerrar sesión |
| [ayuda-reglas.md](ayuda-reglas.md) | **Ayuda General** — reglas del módulo (**Conforme v1**) |
| [ayuda-contenido.md](ayuda-contenido.md) | **Ayuda General** — contenido de la guía en `/app/ayuda/` |
| [mensajecontacto-reglas.md](mensajecontacto-reglas.md) | **MensajeContacto** — requisito formulario contacto + gestión Master (**Conforme v1**) |
| [mensajecontacto-checklist-conforme.md](mensajecontacto-checklist-conforme.md) | **Checklist cerrado** — diseño prototipo gestión Master |
| [public-site-checklist-conforme.md](public-site-checklist-conforme.md) | **Checklist cerrado** — Zona pública (`apps.public_site` + gestión Master) v1 |
| [cuenta-seguridad-reglas.md](cuenta-seguridad-reglas.md) | **Seguridad de la cuenta** — cambio contraseña + reset 2FA desde Perfil (**Conforme v1**) |
| [cuenta-seguridad-checklist-conforme.md](cuenta-seguridad-checklist-conforme.md) | **Checklist cerrado** — Seguridad de la cuenta (`apps.accounts`) v1 |
| [perfil-reglas.md](perfil-reglas.md) | **Perfil** — negocio, unidades y enlace seguridad (**Conforme v1**) |
| [catalog-checklist-conforme.md](catalog-checklist-conforme.md) | **Checklist cerrado** — catálogo base (`apps.catalog`) v1 |
| [administracion-monedas-checklist-conforme.md](administracion-monedas-checklist-conforme.md) | **Checklist cerrado** — Monedas Master (`apps.administration`) v1 |
| [administracion-usuarios-checklist-conforme.md](administracion-usuarios-checklist-conforme.md) | **Checklist cerrado** — Usuarios Master (`apps.administration`) v1 |
| [administracion-facturacion-checklist-conforme.md](administracion-facturacion-checklist-conforme.md) | **Checklist cerrado** — Facturación Master (`apps.billing` + `apps.administration`) v1 |
| [fase-1b-checklist-conforme.md](fase-1b-checklist-conforme.md) | **Checklist cerrado** — Cierre formal Fase 1b (incluye Ayuda General) |
| [fase-1b-landing.md](fase-1b-landing.md) | Plan Fase 1b — landing y zona privada (**CERRADO Conforme v1**) |
| [recetas-checklist-conforme.md](recetas-checklist-conforme.md) | **Checklist cerrado** — Recetas (`apps.recipes`) Django v1 |
| [produccion-checklist-conforme.md](produccion-checklist-conforme.md) | **Checklist cerrado** — Producción (`apps.production`) Django v1 |
| [estadisticas-checklist-conforme.md](estadisticas-checklist-conforme.md) | **Checklist cerrado** — Estadísticas (`apps.analytics`) Django v1 |
| [dashboard-checklist-conforme.md](dashboard-checklist-conforme.md) | **Checklist cerrado** — dashboard home y layout `/app/` |
| [BAKEBUDGE_NOTICIAS.md](BAKEBUDGE_NOTICIAS.md) | **Noticias del sistema** — app, modelo y flujos (**Conforme v1.2**) |
| [noticias-checklist-conforme.md](noticias-checklist-conforme.md) | **Checklist cerrado** — diseño prototipo Noticias |
| [administracion-noticias-checklist-conforme.md](administracion-noticias-checklist-conforme.md) | **Checklist cerrado** — Noticias (`apps.noticias` + gestión Master) v1.2 |
| [acceso-checklist-conforme.md](acceso-checklist-conforme.md) | **Checklist cerrado** — Acceso / seguridad (`apps.security` + cuenta desde Perfil) v1.2 |
| [setup.md](setup.md) | Entorno local, PostgreSQL y variables de entorno |
| [setup-desarrollo-checklist.md](setup-desarrollo-checklist.md) | **Checklist inicio desarrollo** — fases 0–8, completado vs pendiente |
| [../prototype/README.md](../prototype/README.md) | Nota histórica: prototipos HTML archivados fuera del repo |

**Referencia externa (origen del patrón):** [`CODAS_SECURITY.md`](CODAS_SECURITY.md), [`CODAS_SECURITY_PORTABLE_GUIDE.md`](CODAS_SECURITY_PORTABLE_GUIDE.md).

## Convenciones

- Un tema por archivo; nombres en minúsculas.
- Actualizar la documentación cuando cambien decisiones de arquitectura o modelo.
- El código fuente no duplica specs: `docs/` es la fuente de verdad.

## Stack de desarrollo (v1 — oficial)

Por el momento **todo el desarrollo** de BAKEBUDGE utiliza exclusivamente este stack:

| Capa | Tecnología |
|------|------------|
| Lenguaje | **Python** 3.12+ |
| Framework web | **Django** 5.x (server-rendered) |
| Base de datos | **PostgreSQL** 16 (motor único en v1; no SQLite/MySQL) |
| Frontend | **HTML**, **CSS**, **JavaScript** en templates cuando se requiera |
| Tablas en UI | [**DataTables**](https://datatables.net/manual/) |

Sin SPA ni framework JavaScript pesado (no React/Vue). Detalle: [`arquitectura.md`](arquitectura.md), [`ui-ux.md`](ui-ux.md), [`setup.md`](setup.md).
