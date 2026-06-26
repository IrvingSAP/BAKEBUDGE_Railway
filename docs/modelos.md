# Modelos de datos — BAKEBUDGE

> **Documento maestro:** [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md) — inventario completo de modelos, campos y relaciones. Este archivo es un resumen rápido.

## Relaciones principales

```
User ──1:1── UserProfile
User ──1:N── PaymentControl
User ──1:N── Producto
User ──1:N── CostoIndirecto
User ──1:N── ConversionUnidad
User ──1:N── Receta
User ──1:N── OrdenProduccion
User ──1:N── ProduccionAnalytics
User ──1:N── Noticia (created_by / updated_by — solo Master)

Producto ──1:N── ConversionUnidad
Producto ──1:N── ProduccionAnalyticsProducto
Receta ──1:N── RecetaVersion
Receta ──o|── RecetaVersion : version_actual
RecetaVersion ──1:N── RecetaIngrediente
RecetaVersion ──1:N── RecetaPaso
RecetaVersion ──1:N── OrdenProduccion
RecetaVersion ──1:N── ProduccionAnalytics
OrdenProduccion ──1:1── ProduccionAnalytics
ProduccionAnalytics ──1:N── ProduccionAnalyticsProducto
Producto ──1:N── RecetaIngrediente
Moneda ──1:N── UserProfile
Moneda ──1:N── PaymentControl
```

---

## accounts.UserProfile (`apps.accounts`)

### Campos de negocio

| Campo | Tipo | Notas |
|-------|------|-------|
| `user` | OneToOne → User | |
| `user_type` | CharField(1) | `M` = Master, `U` = User (default `U`) |
| `nombre_negocio` | CharField | Nombre de la repostería |
| `moneda` | FK → `core.Moneda` | Moneda para costos (catálogo global) |
| `avatar` | ImageField | Opcional |
| `margen_objetivo_pct` | DecimalField(5,2) | Default `40.00`; margen para precio sugerido |

### Campos de seguridad (2FA)

| Campo | Tipo | Default | Notas |
|-------|------|---------|-------|
| `email_confirmed` | BooleanField | `False` | Correo verificado en onboarding |
| `email_confirm_code` | CharField(6) | null | Código enviado por correo |
| `email_confirm_exp` | DateTimeField | null | Caducidad (+5 min) |
| `totp_secret` | CharField(64) | null | Secreto TOTP (pyotp) |
| `tfa_verified` | BooleanField | `False` | 2FA completado |
| `last_totp_reset` | DateTimeField | null | Auditoría de reset |
| `status` | CharField(1) | `'A'` | A=activo, I=inactivo |
| `locked_until` | DateTimeField | null | Bloqueo temporal |

**Flujos de seguridad:** ver [`BAKEBUDGE_SECURITY.md`](BAKEBUDGE_SECURITY.md).

---

## billing.PaymentControl (`apps.billing`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#paymentcontrol).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | Usuario que paga (tipo User) |
| `estado` | CharField | pendiente, activo, suspendido, consumido |
| `start_date` / `end_date` | DateField | Período de servicio |
| `payment_date` | DateField | Fecha del pago |
| `payment_method` | CharField | banco, transferencia, pagomovil, efectivo, otros |
| `payment_voucher` | CharField(50) | Comprobante / referencia |
| `monto` | DecimalField | Monto pagado |
| `moneda` | FK → Moneda | Moneda del pago |
| `modalidad` | CharField(1) | M mensual, A anual |
| `created_by` / `updated_by` | FK → User | Auditoría (típ. Master) |

---

## catalog.ProductCategory (`apps.catalog`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#productcategory).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `nombre` | CharField(50) | Único por owner |
| `codigo` | CharField(30) | Opcional; único por owner si se usa |
| `descripcion` | TextField | Opcional |
| `orden` | PositiveSmallIntegerField | Orden en UI |
| `color` | CharField(7) | Hex opcional para badge |
| `status` | CharField(1) | `P` / `A` / `I` (default `A`) |
| `es_predeterminada` | BooleanField | Categorías seed al registrarse |

---

## catalog.Producto (`apps.catalog`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#producto).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `nombre` | CharField(150) | |
| `categoria` | FK → ProductCategory | Mismo owner; PROTECT on delete |
| `unidad_base` | CharField | Desde `ConversionUnidad.hacia_unidad` distintos del owner |
| `costo_por_unidad_base` | DecimalField | Precio por unidad base |
| `status` | CharField(1) | `P` En proceso (default), `A` Activo, `I` Inactivo |
| `proveedor` | CharField | Opcional |
| `notas` | TextField | Opcional |

---

## catalog.CostoIndirecto (`apps.catalog`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#costoindirecto).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `nombre` | CharField(50) | Nombre libre |
| `unidad_cobro` | CharField | hora, minuto, lote, porcion, mes, fijo |
| `costo_por_unidad` | DecimalField | Tarifa por unidad de cobro |
| `status` | CharField(1) | `P` / `A` / `I` |
| `notas` | TextField | Opcional |

---

## catalog.ConversionUnidad (`apps.catalog`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#conversionunidad).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `producto` | FK → Producto | Opcional; null = genérica |
| `nombre` | CharField(50) | Etiqueta opcional |
| `desde_unidad` | CharField(20) | Texto libre (taza, cdta, oz…) |
| `hacia_unidad` | CharField(10) | Alinear con `producto.unidad_base` |
| `factor` | DecimalField | `1 × desde = factor × hacia` |
| `notas` | TextField | Opcional |

---

## recipes.Receta (`apps.recipes`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#receta).

Cabecera de receta; costos y detalle en `RecetaVersion` (`version_actual`).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `nombre` | CharField(100) | |
| `descripcion_corta` | CharField(255) | Opcional |
| `imagen` | ImageField | Opcional |
| `status` | CharField(1) | `P` / `A` / `I` (default `P`) |
| `version_actual` | FK → RecetaVersion | Nullable; versión vigente |
| `notas` | TextField | Opcional |

---

## recipes.RecetaVersion (`apps.recipes`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#recetaversion).

| Campo | Tipo | Notas |
|-------|------|-------|
| `receta` | FK → Receta | |
| `numero_version` | PositiveIntegerField | 1, 2, 3… único por receta |
| `notas_cambio` | TextField | Opcional |
| `rendimiento_cantidad` | DecimalField | Default 1 |
| `rendimiento_unidad` | CharField(30) | Texto libre (porciones, molde…) |
| `costo_ingredientes` | DecimalField | Cache calculado |
| `costo_indirectos` | DecimalField | Cache calculado |
| `costo_total` | DecimalField | Cache calculado |
| `costo_por_porcion` | DecimalField | `costo_total / rendimiento` |
| `precio_venta_sugerido` | DecimalField | Cache: costo + margen del perfil |
| `margen_aplicado_pct` | DecimalField(5,2) | Margen usado al calcular sugerido |

## recipes.RecetaCostoIndirecto (`apps.recipes`)

> Detalle: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#recetacostoindirecto).

| Campo | Tipo | Notas |
|-------|------|-------|
| `version` | FK → RecetaVersion | |
| `costo_indirecto` | FK → CostoIndirecto | |
| `cantidad` | DecimalField | Según `unidad_cobro` del indirecto |
| `costo_linea` | DecimalField | Calculado |
| `orden` | PositiveIntegerField | |
| `notas` | CharField(100) | Opcional |

---

## recipes.RecetaIngrediente (`apps.recipes`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#recetaingrediente).

| Campo | Tipo | Notas |
|-------|------|-------|
| `version` | FK → RecetaVersion | |
| `producto` | FK → Producto | Mismo owner que la receta |
| `cantidad` | DecimalField | |
| `unidad` | CharField(20) | Texto libre (taza, g, unidad…) |
| `orden` | PositiveIntegerField | |
| `notas` | CharField(100) | Opcional |
| `cantidad_normalizada` | DecimalField | Cache en unidad_base del producto |
| `costo_linea` | DecimalField | Calculado vía ConversionUnidad |

**Unicidad:** `unique_together = ('version', 'producto')` — un insumo por versión.

---

## recipes.RecetaPaso (`apps.recipes`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#recetapaso).

| Campo | Tipo | Notas |
|-------|------|-------|
| `version` | FK → RecetaVersion | |
| `orden` | PositiveIntegerField | 1, 2, 3… único por versión |
| `instruccion` | TextField | Procedimiento del paso |
| `tiempo_minutos` | PositiveIntegerField | Opcional; no afecta costos |

**Unicidad:** `unique_together = ('version', 'orden')`.

---

## production.OrdenProduccion (`apps.production`)

> Detalle completo: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#ordenproduccion).

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `receta_version` | FK → RecetaVersion | PROTECT |
| `codigo` | CharField(20) | Referencia legible; auto si vacío |
| `cantidad_lotes` | DecimalField | Multiplicador del rendimiento (1 = tanda completa) |
| `fecha_programada` | DateField | Opcional |
| `estado` | CharField | borrador, en_proceso, completada, cancelada |
| `costo_estimado` | DecimalField | `cantidad_lotes × receta_version.costo_total` |
| `precio_venta_unitario` | DecimalField | Opcional al completar |
| `precio_venta_total` | DecimalField | Opcional; alternativa a unitario |
| `fecha_inicio` | DateTimeField | Al pasar a en_proceso |
| `fecha_completada` | DateTimeField | Al completar o cancelar |
| `notas` | TextField | Opcional |

**Precio venta:** `precio_venta_unitario` / `precio_venta_total` (opcional al completar).

**Costo:** recalculable en `borrador`; congelado al pasar a `en_proceso`. Al `completada` → `ProduccionAnalytics`.

---

## analytics.ProduccionAnalytics (`apps.analytics`)

> Detalle: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#produccionanalytics).

Snapshot inmutable al completar orden: costos, precios, márgenes, período.

| Campo | Tipo | Notas |
|-------|------|-------|
| `owner` | FK → User | |
| `orden_produccion` | OneToOne → OrdenProduccion | PROTECT |
| `receta` / `receta_version` | FK | PROTECT + snapshots nombre/costos |
| `unidades_producidas` | DecimalField | lotes × rendimiento |
| `costo_produccion_total` | DecimalField | De orden congelada |
| `precio_venta_total` | DecimalField | Ingreso real o sugerido |
| `ganancia_real` / `margen_real_pct` | DecimalField | Márgenes |
| `periodo_anio` / `periodo_mes` | SmallInteger | Índices para dashboard |

---

## analytics.ProduccionAnalyticsProducto (`apps.analytics`)

> Detalle: [`BAKEBUDGE_MODELS.md`](BAKEBUDGE_MODELS.md#produccionanalyticsproducto).

Líneas por insumo escaladas → rankings de productos más usados.

| Campo | Tipo | Notas |
|-------|------|-------|
| `analytics` | FK → ProduccionAnalytics | |
| `producto` | FK → Producto | SET_NULL |
| `producto_nombre` / `producto_categoria` | CharField | Snapshots (`producto_categoria` = nombre de `ProductCategory`) |
| `cantidad_normalizada_total` | DecimalField | Uso escalado por lotes |
| `costo_linea_total` | DecimalField | Costo insumo en la orden |

---

## noticias.Noticia (`apps.noticias`) — pendiente

> Diseño completo: [`BAKEBUDGE_NOTICIAS.md`](BAKEBUDGE_NOTICIAS.md). **Implementación pendiente.**

Noticias **globales** del sistema (no por `owner`). Master publica; usuarios leen en `/app/noticias/`.

| Campo | Tipo | Notas |
|-------|------|-------|
| `titulo` | CharField(200) | |
| `slug` | SlugField | URL detalle (opcional v1) |
| `resumen` | CharField(300) | Tarjeta en listado |
| `contenido` | TextField | Cuerpo |
| `tipo` | CharField | nueva_funcion, mejora, aviso, mantenimiento |
| `publicada` | BooleanField | Solo publicadas visibles |
| `fecha_publicacion` | DateTimeField | Orden del feed |
| `created_by` / `updated_by` | FK → User | Master |
