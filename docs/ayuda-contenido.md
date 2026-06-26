# BAKEBUDGE — Ayuda General (contenido base)

Documento **fuente de contenido** para la pantalla **Ayuda General** (`/app/ayuda/`).  
Orientado al **flujo del proceso**, las **apps** involucradas y el **orden recomendado** de trabajo.

> **No incluye** detalle de campos ni validaciones de formularios — eso vive en cada módulo (`*_reglas.md`, `*_help.html`).

**Estado:** **Conforme v1** — prototipo y Django [`/app/ayuda/`](../apps/ayuda/views.py).  
**Reglas de módulo:** [`ayuda-reglas.md`](ayuda-reglas.md)  
**Flujos técnicos:** [`flujos.md`](flujos.md)  
**Template Django:** `apps/ayuda/templates/ayuda/home.html` · **URL:** `/app/ayuda/`

---

## Cómo leer este documento

| Elemento | Uso en la futura pantalla |
|----------|---------------------------|
| **Sección** | Bloque principal (`h2`) — acordeón o tarjeta |
| **Paso** | Ítem numerado dentro del bloque (`h3` o lista ordenada) |
| **App** | Módulo Django responsable |
| **Menú** | Texto exacto del sidebar + URL Django |
| **Para qué** | Rol en el ciclo (explicación ampliada) |
| **Ejemplo** | Datos ilustrativos para cargar en la app |
| **Antes de** | Dependencias mínimas |
| **Después** | Qué módulos se habilitan o mejoran |

---

## Panorama del ciclo

BakeBudge organiza el negocio de repostería en tres grandes fases. Cada fase usa datos de la anterior.

```text
┌─────────────────────────────────────────────────────────────────┐
│  1. CATÁLOGO BASE                                               │
│     Perfil → Categorías → Conversiones → Costos indirectos      │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. RECETAS Y PRODUCCIÓN                                        │
│     Productos → Recetas (versiones) → Órdenes de producción     │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. ANÁLISIS Y ESTADÍSTICAS                                     │
│     Snapshots al completar → KPIs, márgenes, rankings           │
└─────────────────────────────────────────────────────────────────┘
```

**Regla transversal:** todo lo que ves en `/app/` pertenece a **tu cuenta** (`owner = usuario conectado`). No se mezclan datos entre usuarios.

**Dashboard** (`/app/`) resume el avance y enlaza a cada fase; no sustituye esta guía.

---

## Sección 1 — Catálogo base

Información de **referencia y configuración** que otras partes del sistema consumen. Conviene completarla **antes** de cargar productos y recetas con seriedad.

### Objetivo de la sección

Dejar definidos el **contexto del negocio** (perfil), la **clasificación** de insumos (categorías), las **reglas de unidad** (conversiones) y los **gastos no ligados a un producto** (costos indirectos). Sin esta base, los costos de recetas y producción serán incompletos o inconsistentes.

### Apps involucradas

| App | Modelos / ámbito |
|-----|------------------|
| `apps.accounts` | `UserProfile` |
| `apps.catalog` | `ProductCategory`, `ConversionUnidad`, `CostoIndirecto` |

### Orden recomendado de pasos

#### Paso 1.1 — Perfil

| | |
|--|--|
| **Menú** | **Perfil** → `/app/perfil/` |
| **App** | `apps.accounts` |
| **Para qué** | Configurar la identidad de tu negocio y los parámetros económicos globales. El nombre aparece en la app, la moneda unifica todos los montos y el **margen objetivo** define cuánto quieres ganar sobre el costo: el sistema lo usa para sugerir precios en recetas y para comparar tu margen real en estadísticas y dashboard. |
| **Antes de** | Nada — puede ser lo primero tras el primer acceso. |
| **Después** | Recetas (precio sugerido), estadísticas (margen real vs objetivo), dashboard (KPI margen). |
| **Ejemplo** | Nombre de la repostería «Dulces de Ana», moneda COP, margen objetivo **40 %**, unidades por defecto: peso **g**, volumen **ml**, conteo **un**. |

**Idea clave:** el margen objetivo no es un dato aislado; se propaga a formulaciones y al evaluar si una producción fue rentable.

---

#### Paso 1.2 — Categorías de producto

| | |
|--|--|
| **Menú** | **Catálogo base → Categorías** → `/app/categorias/` |
| **App** | `apps.catalog` |
| **Para qué** | Agrupar insumos por tipo para encontrarlos rápido en listados, asignar color en la interfaz y filtrar el consumo en estadísticas. Cada producto debe pertenecer a una categoría antes de usarlo en recetas. |
| **Antes de** | Perfil (recomendado). |
| **Después** | Productos — cada producto apunta a una categoría. |
| **Ejemplo** | Nombre «Harinas y polvos», código «harinas», descripción «Materia seca para masas», orden **10**, color **#E8F4EA**, estado Activo. |

**Idea clave:** las categorías no calculan costos por sí solas; estructuran el catálogo y los reportes de uso de insumos.

---

#### Paso 1.3 — Conversiones de unidad

| | |
|--|--|
| **Menú** | **Catálogo base → Conversiones de unidad** → `/app/conversiones/` |
| **App** | `apps.catalog` |
| **Para qué** | Cuando compras o almacenas un insumo en una unidad distinta a la que usas en la receta, BakeBudge necesita el factor de conversión para calcular bien el costo del ingrediente. Se define **por producto**, no como regla global. |
| **Antes de** | Productos (idealmente antes de usarlos en recetas con unidades distintas). |
| **Después** | Recetas — al agregar ingredientes en unidades distintas a la base del producto. |
| **Ejemplo** | Producto «Harina de trigo» — conversión de **kg** a **g**, factor **1000** (1 kg = 1000 g). Si en la receta usas 250 g, el costo se calcula con el precio por gramo. |

**Idea clave:** solo necesitas conversiones donde realmente compras o midas en una unidad distinta a la unidad base del producto. Si no aplica, puedes omitir este paso.

---

#### Paso 1.4 — Costos indirectos

| | |
|--|--|
| **Menú** | **Catálogo base → Costos indirectos** → `/app/costos-indirectos/` |
| **App** | `apps.catalog` |
| **Para qué** | Capturar gastos fijos o variables que no son un producto del catálogo pero sí entran al costo de elaborar: horno, gas, tiempo de trabajo, empaque genérico, etc. Se cargan una vez y luego se asignan y escalan en cada versión de receta. |
| **Antes de** | Perfil y categorías (recomendado). |
| **Después** | Recetas — asignación de indirectos en cada `RecetaVersion`. |
| **Ejemplo** | «Mano de obra horneado» — **$15 000/hora**; «Gas del horno» — **$3 500** por lote estándar. Luego, en la formulación, asignas cuánto aplica a cada receta. |

**Idea clave:** un costo indirecto no entra solo en una receta; se define en catálogo y luego se **asocia y escala** en la formulación de cada versión.

### Cierre de la Sección 1

Cuando Perfil, categorías, conversiones (si aplican) e indirectos están listos, el **catálogo base** está preparado para soportar productos y recetas con costos coherentes.

```text
Perfil ──► Categorías ──► [Conversiones] ──► Costos indirectos
                                              │
                                              ▼
                                    (listo para Sección 2)
```

---

## Sección 2 — Recetas y producción

Ciclo operativo del día a día: **insumos con precio**, **formulaciones versionadas** y **órdenes de trabajo** que materializan lo que produces.

### Objetivo de la sección

Pasar de «tengo insumos y reglas» a «sé cuánto cuesta cada receta» y «registro cada elaboración» con estados claros, hasta completar una orden que alimentará el análisis.

### Apps involucradas

| App | Modelos / ámbito |
|-----|------------------|
| `apps.catalog` | `Producto` |
| `apps.recipes` | `Receta`, `RecetaVersion`, ingredientes, pasos, indirectos en versión |
| `apps.production` | `OrdenProduccion` |

### Orden recomendado de pasos

#### Paso 2.1 — Productos (insumos)

| | |
|--|--|
| **Menú** | **Productos** → `/app/productos/` |
| **App** | `apps.catalog` |
| **Para qué** | Registrar cada materia prima con su precio de compra actualizado y unidad base. Es la fuente del costo de ingredientes en formulaciones y del desglose por insumo en producción y estadísticas. |
| **Antes de** | Sección 1 (categorías; conversiones si la unidad de compra difiere). |
| **Después** | Recetas — cada ingrediente de una versión apunta a un producto. |
| **Ejemplo** | «Harina de trigo» — categoría Harinas y polvos, unidad base **g**, costo **$0,012/g** (equivalente a $12/kg), proveedor «Molinos del Valle», estado Activo. |

**Idea clave:** sin productos con costo actualizado, el costo de receta y de producción será cero o desactualizado.

---

#### Paso 2.2 — Recetas y versiones

| | |
|--|--|
| **Menú** | **Recetas** → `/app/recetas/` |
| **App** | `apps.recipes` |
| **Para qué** | Documentar qué elaboras o vendes: nombre de receta, versión de formulación con ingredientes y cantidades, pasos, indirectos asignados, rendimiento (porciones o unidades) y precio de venta sugerido calculado con tu margen objetivo. |
| **Antes de** | Productos; costos indirectos del catálogo; perfil con margen objetivo. |
| **Después** | Producción — cada orden elige una receta y una versión concreta. |
| **Ejemplo** | Receta «Brownie clásico» v1 — 500 g harina, 300 g chocolate, 4 huevos; indirecto «Mano de obra horneado» 45 min; rendimiento **24 porciones**; precio sugerido **$4 500/porción**. |

**Subproceso recomendado (flujo, no campos):**

1. **Crear receta** — se genera la versión inicial (v1) con rendimiento.
2. **Abrir formulación** — agregar ingredientes (productos), indirectos y pasos; el sistema calcula costos de la versión.
3. **Revisar costos** — vista de desglose por receta (costo por porción, sugerido de venta).
4. **Nueva versión** — cuando cambia la formulación o precios de insumos de forma relevante: se crea v2, v3… la versión anterior queda como **historial** (no se pierde el costo pasado).

**Idea clave:** la **versión** es el corazón del costo teórico. La cabecera de receta es estable; las versiones guardan el detalle que cambia en el tiempo.

---

#### Paso 2.3 — Producción (órdenes)

| | |
|--|--|
| **Menú** | **Producción** → `/app/produccion/` |
| **App** | `apps.production` |
| **Para qué** | Registrar una elaboración concreta: qué receta y versión, cuántos lotes, fechas planificadas, avance por estados y, al completar, el precio de venta real. Es el puente entre la teoría de costos y el análisis histórico de tu negocio. |
| **Antes de** | Receta con versión vigente y costos calculados. |
| **Después** | Estadísticas — solo las órdenes **completadas** generan snapshot analítico. |
| **Ejemplo** | Orden #12 — Brownie clásico v1, **2 lotes** (48 porciones), fecha planificada 15/06, estado En proceso → Completada, precio de venta **$4 800/porción**. |

**Subproceso del ciclo de estados:**

```text
borrador ──► en_proceso ──► completada
    │              │
    └──────────────┴──► cancelada
```

| Estado | Qué representa en el flujo |
|--------|---------------------------|
| **Borrador** | Planificación: puedes ajustar lotes; el costo estimado puede recalcularse. |
| **En proceso** | Producción iniciada: el **costo estimado se congela** como referencia de esa orden. |
| **Completada** | Elaboración finalizada; se confirma precio de venta (o se usa el sugerido); se dispara el **registro analítico**. |
| **Cancelada** | Orden anulada; **no** alimenta estadísticas. |

**Idea clave:** producir no es solo «anotar que cociné» — es cerrar un ciclo con costo congelado y, al completar, precio de venta para medir ganancia real.

**Atajo:** desde el listado de recetas puedes ir directo a **Producir** una receta (preselección en alta de orden).

### Cierre de la Sección 2

```text
Productos ──► Receta + versiones ──► Orden (borrador → … → completada)
                                              │
                                              ▼
                                    (habilita Sección 3)
```

---

## Sección 3 — Análisis y estadísticas

Evaluación del negocio a partir de **producciones ya completadas**: ganancias, pérdidas, costos, rankings y tendencias.

### Objetivo de la sección

Responder preguntas del tipo: *¿qué receta me deja más margen?*, *¿estoy por debajo de mi margen objetivo?*, *¿qué insumos consumo más?*, *¿cómo evoluciona el costo por porción?*

### Apps involucradas

| App | Modelos / ámbito |
|-----|------------------|
| `apps.analytics` | `ProduccionAnalytics`, `ProduccionAnalyticsProducto` |
| `apps.dashboard` | Resumen KPIs en home (consume analytics) |
| `apps.production` | Origen: `OrdenProduccion` completada |

### Cuándo hay datos

| Situación | ¿Aparece en estadísticas? |
|-----------|---------------------------|
| Orden **completada** | Sí — se crea un snapshot inmutable (`ProduccionAnalytics`). |
| Orden borrador / en proceso | No — aún no hay hecho analítico. |
| Orden **cancelada** | No — excluida del análisis v1. |

El snapshot se genera **automáticamente** al completar la orden (no hay pantalla aparte de «generar analytics»).

### Paso 3.1 — Entender qué se guarda (concepto)

| | |
|--|--|
| **Para qué** | Cada vez que completas una orden, BakeBudge guarda una «foto» fija de esa producción: costos, márgenes e insumos usados en ese momento, sin recalcular si después cambias precios en el catálogo. Así el historial refleja lo que realmente ocurrió. |
| **Ejemplo** | Orden completada el 10/06 — 24 brownies, costo de producción **$72 000**, venta **$108 000**, margen real **33 %** (comparado con objetivo 40 % en tu perfil). |

Cada orden completada deja un **registro de cabecera** con, entre otros conceptos:

- Receta y versión usadas en ese momento (snapshot de nombres y números).
- Unidades producidas y **costo de producción** (el estimado congelado de la orden).
- Precio de venta (real o sugerido) y **márgenes** (estimado vs real).
- Periodo (año/mes) para filtrar y agrupar.

Además, **líneas por insumo** escaladas a esa producción — base para rankings de productos más usados.

**Idea clave:** las estadísticas leen **snapshots**, no recalculan en vivo desde el catálogo actual. Así el histórico sigue siendo fiel aunque hoy cambies el precio de la harina.

---

#### Paso 3.2 — Pantalla Estadísticas

| | |
|--|--|
| **Menú** | **Estadísticas** → `/app/estadisticas/` |
| **App** | `apps.analytics` |
| **Para qué** | Analizar el historial de producciones completadas: comparar ganancias, detectar qué recetas e insumos son más relevantes y ver si cumples tu margen objetivo en el periodo que elijas. |
| **Ejemplo** | Filtro «Últimos 3 meses» — margen real **38 %**, ganancia total **$1 240 000**, 28 órdenes completadas; insumo más usado: Harina de trigo, **12,5 kg** consumidos. |

**Bloques de la pantalla (contenido futuro HTML):**

| Bloque | Qué evalúa |
|--------|----------------|
| **KPIs del periodo** | Margen real promedio vs objetivo (perfil), ganancia total, órdenes completadas, órdenes con pérdida. |
| **Recetas más producidas** | Qué elaboras con más frecuencia (lotes / actividad). |
| **Insumos más usados** | Consumo agregado de productos en producciones del periodo. |
| **Versiones más productivas** | Qué versión de formulación rinde más unidades en la práctica. |
| **Evolución costo / porción** | Tendencia del costo unitario de producción por mes. |
| **Ratio indirectos / ingredientes** | Peso de los indirectos frente a ingredientes en el periodo. |
| **Tabla detalle** | Cada fila = una producción completada; enlace al detalle de la orden. |

**Filtros (flujo):** periodo, receta, categoría de insumo (afecta ranking de insumos). Sin filtros = vista global de tu historial.

---

#### Paso 3.3 — Dashboard como resumen

| | |
|--|--|
| **Menú** | **Dashboard** → `/app/` |
| **App** | `apps.dashboard` |
| **Para qué** | Punto de entrada diario con números resumidos de tu operación sin entrar a cada módulo: cuántos productos y recetas tienes, órdenes del mes, margen promedio reciente y accesos directos a lo que más usas. |
| **Relación** | El dashboard **orienta**; estadísticas **profundiza**. Ambos usan tus datos; el margen promedio del dashboard se alimenta de analytics cuando ya hay órdenes completadas. |
| **Ejemplo** | Dashboard muestra **45 productos** activos, **12 recetas**, **6 órdenes** este mes, margen promedio **36 %**; producción reciente: Brownie (completada), Torta red velvet (en proceso). |

### Cierre de la Sección 3

```text
Orden completada ──► Snapshot analytics ──► Estadísticas + Dashboard
                              │
                              ├── Ganancia / pérdida
                              ├── Margen real vs objetivo
                              └── Rankings y tendencias
```

---

## Sección 4 — Noticias

Comunicados del sistema para mantenerte al día con novedades, avisos y orientación sobre el uso de BakeBudge. Complementan esta guía con mensajes puntuales y actualizados.

### Objetivo de la sección

Saber **dónde leer** avisos oficiales y personalizados sin confundirlos con el flujo operativo del negocio (catálogo, recetas, producción, estadísticas).

### Apps involucradas

| App | Modelos / ámbito |
|-----|------------------|
| `apps.noticias` | `Noticia` — feed de lectura para User y Master |

### Orden recomendado de pasos

#### Paso 4.1 — Feed de noticias

| | |
|--|--|
| **Menú** | **Noticias** → `/app/noticias/` |
| **App** | `apps.noticias` |
| **Para qué** | Consultar comunicados oficiales y mensajes personalizados sobre novedades, mantenimiento, primeros pasos o recordatorios del flujo. No sustituye esta guía, pero te orienta en el momento con avisos puntuales. |
| **Antes de** | Nada — disponible desde el primer acceso. Tras completar seguridad, el **primer ingreso** puede redirigir aquí antes del dashboard. |
| **Después** | Continuar con catálogo base, recetas, producción o dashboard según lo que indiquen las noticias o tu prioridad del momento. |
| **Ejemplo** | Tarjeta destacada «Bienvenida a BakeBudge» (alcance global, vigente todo el mes); tarjeta personal «Completa tu perfil y crea tu primera categoría» (solo tu cuenta). |

**Elementos del feed (contenido futuro HTML):**

| Elemento | Qué significa |
|----------|----------------|
| **Destacadas** | Aparecen primero para no perder avisos importantes. |
| **Alcance global** | Visibles para todos los usuarios de la plataforma. |
| **Alcance personal** | Mensajes dirigidos solo a tu cuenta. |
| **Vigencia** | Solo se muestran noticias activas dentro de su periodo de visibilidad. |

**Idea clave:** las noticias **informan** en el momento; esta Ayuda General explica el **flujo completo**. Revisa el feed cuando quieras desde el menú lateral.

### Cierre de la Sección 4

```text
Primer acceso (opcional) ──► Noticias ──► Catálogo / recetas / dashboard
```

**Fuera de este documento:** **Administración → Gestión noticias** (solo Master; CRUD de publicaciones).

---

## Guía de redacción para el HTML (notas al prototipo)

Cuando se apruebe este contenido para HTML:

1. **Cuatro bloques visuales** alineados a las secciones 1, 2, 3 y 4 (acordeón, tabs o cards apiladas).
2. **Pasos numerados** dentro de cada bloque; cada paso incluye **Para qué** (ampliado), **Antes de** / **Después** cuando aplique, e **Ejemplo** con datos ilustrativos.
3. **Enlaces** «Ir a …» con `{% url %}` en Django (en prototipo, rutas relativas al menú).
4. **Diagramas** — reutilizar los ASCII de este doc o simplificar a flechas en CSS.
5. **Sin formularios**, sin tablas de datos del usuario, sin DataTables.
6. **Sin mapa menú → app** — esa información es de sistema, no de ayuda al usuario.
7. **Ayuda por formulario** — mencionar una sola vez que cada pantalla CRUD tiene su botón **Ayuda** propio; no duplicar ese contenido aquí.

### Estructura propuesta de la página

| Orden en pantalla | Origen en este doc |
|-------------------|-------------------|
| Título + intro | Panorama del ciclo |
| Bloque 1 | Sección 1 — Catálogo base (pasos 1.1–1.4) |
| Bloque 2 | Sección 2 — Recetas y producción (pasos 2.1–2.3) |
| Bloque 3 | Sección 3 — Análisis y estadísticas (pasos 3.1–3.3) |
| Bloque 4 | Sección 4 — Noticias (paso 4.1) |

---

## Documentos relacionados (detalle por módulo)

| Tema | Documento |
|------|-----------|
| Perfil | [`perfil-reglas.md`](perfil-reglas.md) |
| Categorías | [`categorias-reglas.md`](categorias-reglas.md) |
| Conversiones | [`conversiones-reglas.md`](conversiones-reglas.md) |
| Costos indirectos | [`costos-indirectos-reglas.md`](costos-indirectos-reglas.md) |
| Productos | [`productos-reglas.md`](productos-reglas.md) |
| Recetas | [`recetas-reglas.md`](recetas-reglas.md) · [`recetaversion-reglas.md`](recetaversion-reglas.md) |
| Producción | [`produccion-reglas.md`](produccion-reglas.md) |
| Estadísticas | [`estadisticas-reglas.md`](estadisticas-reglas.md) · [`BAKEBUDGE_ANALYTICS.md`](BAKEBUDGE_ANALYTICS.md) |
| Dashboard | [`dashboard-reglas.md`](dashboard-reglas.md) |
| Noticias | [`noticias-reglas.md`](noticias-reglas.md) |
| Modelos | [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) |

---

*Última actualización: contenido Ayuda General integrado en `apps/ayuda/templates/ayuda/home.html` — Conforme v1.*
