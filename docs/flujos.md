# Flujos — BAKEBUDGE

## 0. Seguridad (login y acceso)

Detalle completo en [`BAKEBUDGE_SECURITY.md`](BAKEBUDGE_SECURITY.md).

1. **Registro** (`/registro/`) → crea cuenta.
2. **Primer login** → correo + código 2FA (TOTP con QR).
3. **Logins siguientes** → contraseña + TOTP.
4. Acceso al sistema solo con `is_security_complete = True`.

---

## 1. Registro → onboarding mínimo

1. Usuario se registra desde la landing.
2. En el primer login completa seguridad (correo + 2FA).
3. Redirección al dashboard (`/app/`) con checklist:
   - Crear primer producto (insumo).
   - Crear primera receta.

---

## 2. Catálogo de insumos

1. CRUD de `Producto` con costo y unidad base.
2. Conversiones opcionales en `ConversionUnidad`.
3. Listado con búsqueda y filtro por categoría.

---

## 3. Receta con versionado

1. Crear `Receta` → auto-crear `RecetaVersion` v1.
2. Agregar `RecetaIngrediente` y `RecetaPaso`.
3. Al guardar versión: recalcular costos.
4. Nueva versión al cambiar ingredientes (historial de costos preservado).

---

## 4. Cálculo de costos

```
costo_linea_ingrediente = cantidad_en_unidad_base × producto.costo_por_unidad_base
costo_linea_indirecto = cantidad × costo_indirecto.costo_por_unidad
costo_total = Σ costo_linea_ingrediente + Σ costo_linea_indirecto
costo_por_porcion = costo_total / rendimiento_cantidad
```

Implementación en `apps/recipes/services/cost_calculator.py`. Catálogo de indirectos: [`BAKEBUDGE_MODELS.md#costoindirecto`](BAKEBUDGE_MODELS.md#costoindirecto).

**Recálculo automático cuando:**
- Se edita un producto (precio/unidad).
- Se guarda una versión de receta.
- Se abre una receta con insumos desactualizados (aviso al usuario).

---

## 5. Orden de producción

1. Elegir receta + versión activa.
2. Indicar cantidad de lotes / unidades.
3. Ver costo estimado, precio sugerido y estado de la orden.
4. Cambiar estado: borrador → en_proceso → completada / cancelada.
5. Al **completar:** opcionalmente indicar precio de venta; si vacío → `RecetaVersion.precio_venta_sugerido`.
6. Trigger `record_production_analytics` → snapshot en `ProduccionAnalytics` + líneas por insumo.

---

## 6. Analytics y dashboard

Detalle de modelos: [`BAKEBUDGE_MODELS.md#métricas-del-dashboard`](BAKEBUDGE_MODELS.md#métricas-del-dashboard).  
Documento de diseño: [`BAKEBUDGE_ANALYTICS.md`](BAKEBUDGE_ANALYTICS.md).

**Cadena de precios (3 capas):**

```
UserProfile.margen_objetivo_pct
    → RecetaVersion.precio_venta_sugerido
    → OrdenProduccion.precio_venta (override opcional)
    → ProduccionAnalytics (snapshot inmutable)
```

**Métricas principales en `/app/`:**

| Widget | Fuente |
|--------|--------|
| Recetas más producidas | `ProduccionAnalytics` por `receta_id` |
| Versiones más usadas | por `receta_version_id` |
| Productos más usados | `ProduccionAnalyticsProducto` SUM cantidades |
| Evolución de costos | AVG `costo_produccion_unitario` por mes |
| Margen real vs objetivo | `margen_real_pct` vs `margen_objetivo_pct` |
| Órdenes con pérdida | `perdida IS NOT NULL` |

Solo órdenes **completadas** alimentan analytics. Canceladas no generan registro.

---

## Diagrama de navegación

```
Landing (pública)
    └── Registro / Login
            └── Wizard seguridad (correo + 2FA si aplica)
                    └── Dashboard /app/
                    ├── Productos (catálogo)
                    ├── Recetas
                    │       └── Detalle → ingredientes, pasos, costos
                    ├── Producción (órdenes)
                    ├── Estadísticas (analytics)
                    ├── Noticias (novedades del sistema)
                    ├── Ayuda General (guía del ciclo — ver ayuda-reglas.md)
                    └── Perfil (UserProfile)
```
