"""Formulación RecetaVersion: guardado, nueva versión, parseo POST."""

from decimal import Decimal

from django.db import transaction
from django.db.models import Max, Q

from apps.catalog.constants import Status as CatalogStatus
from apps.catalog.models import CostoIndirecto, ConversionUnidad, Producto
from apps.recipes.models import (
    Receta,
    RecetaCostoIndirecto,
    RecetaIngrediente,
    RecetaPaso,
    RecetaVersion,
)
from apps.recipes.services.cost_calculator import recalcular_totales_version


def get_receta_for_user(user, pk):
    return Receta.objects.select_related("version_actual").get(pk=pk, owner=user)


def _normalize_unit(value: str) -> str:
    return (value or "").strip().lower()


def list_unidades_desde_conversiones(owner):
    """Unidades `desde_unidad` distintas del catálogo de conversiones del usuario."""
    seen = {}
    for desde in (
        ConversionUnidad.objects.filter(owner=owner)
        .values_list("desde_unidad", flat=True)
        .distinct()
    ):
        key = _normalize_unit(desde)
        if key:
            seen[key] = desde.strip()
    return sorted(seen.values(), key=str.lower)


def unidades_para_producto(owner, producto):
    """
    Unidades válidas en receta para un producto:
    su unidad_base + `desde_unidad` de conversiones hacia esa base.
    """
    if producto is None:
        return list_unidades_desde_conversiones(owner)

    result = {}
    base_key = _normalize_unit(producto.unidad_base)
    if base_key:
        result[base_key] = producto.unidad_base.strip()

    conversiones = ConversionUnidad.objects.filter(owner=owner).filter(
        Q(producto=producto) | Q(producto__isnull=True)
    )
    for conv in conversiones:
        if _normalize_unit(conv.hacia_unidad) == base_key:
            desde = conv.desde_unidad.strip()
            result[_normalize_unit(desde)] = desde

    return sorted(result.values(), key=str.lower)


def unidad_permitida_para_producto(owner, producto, unidad):
    permitidas = {_normalize_unit(u) for u in unidades_para_producto(owner, producto)}
    return _normalize_unit(unidad) in permitidas


def _parse_decimal(raw, field_key, errors, required=True, min_value=None):
    if raw in (None, ""):
        if required:
            errors[field_key] = "Este campo es obligatorio."
        return None
    try:
        value = Decimal(str(raw).replace(",", "."))
    except Exception:
        errors[field_key] = "Ingresa un número válido."
        return None
    if min_value is not None and value < min_value:
        errors[field_key] = f"El valor debe ser al menos {min_value}."
    return value


def parse_formulacion_post(post):
    return {
        "rendimiento_cantidad": post.get("rendimiento_cantidad", "").strip(),
        "rendimiento_unidad": post.get("rendimiento_unidad", "").strip(),
        "precio_venta_sugerido": post.get("precio_venta_sugerido", "").strip(),
        "precio_override_manual": post.get("precio_override_manual") in {"1", "true", "on"},
        "ingredientes_producto": post.getlist("ingrediente_producto"),
        "ingredientes_cantidad": post.getlist("ingrediente_cantidad"),
        "ingredientes_unidad": post.getlist("ingrediente_unidad"),
        "ingredientes_notas": post.getlist("ingrediente_notas"),
        "indirectos_gasto": post.getlist("indirecto_gasto"),
        "indirectos_cantidad": post.getlist("indirecto_cantidad"),
        "indirectos_notas": post.getlist("indirecto_notas"),
        "pasos_instruccion": post.getlist("paso_instruccion"),
        "pasos_tiempo": post.getlist("paso_tiempo"),
    }


def validate_formulacion_header(data, errors):
    rendimiento = _parse_decimal(
        data["rendimiento_cantidad"],
        "rendimiento_cantidad",
        errors,
        min_value=Decimal("0.0001"),
    )
    if not data["rendimiento_unidad"]:
        errors["rendimiento_unidad"] = "La unidad de rendimiento es obligatoria."
    precio = _parse_decimal(
        data["precio_venta_sugerido"],
        "precio_venta_sugerido",
        errors,
        min_value=Decimal("0"),
    )
    return rendimiento, precio


def _validar_ingredientes(data, owner, errors):
    """Valida filas de ingredientes (incl. producto único por versión). Retorna filas listas para persistir."""
    filas = []
    productos_usados = set()

    for orden, (producto_id, cantidad_raw, unidad, notas) in enumerate(
        _zip_rows(
            data["ingredientes_producto"],
            data["ingredientes_cantidad"],
            data["ingredientes_unidad"],
            data["ingredientes_notas"],
        )
    ):
        if not producto_id and not cantidad_raw and not unidad:
            continue

        key = f"ingrediente_{orden}"
        errores_antes = len(errors)

        if not producto_id:
            errors[f"{key}_producto"] = "Selecciona un producto."
            continue

        producto = Producto.objects.filter(
            owner=owner,
            pk=producto_id,
            status=CatalogStatus.ACTIVO,
        ).first()
        if producto is None:
            errors[f"{key}_producto"] = "Producto no válido o inactivo."
            continue

        if producto.pk in productos_usados:
            errors[f"{key}_producto"] = (
                f"«{producto.nombre}» ya está en la formulación. "
                "Solo un registro por producto; suma las cantidades en una sola línea."
            )
            continue
        productos_usados.add(producto.pk)

        cantidad = _parse_decimal(
            cantidad_raw, f"{key}_cantidad", errors, min_value=Decimal("0.0001")
        )
        unidad = (unidad or "").strip()
        if not unidad:
            errors[f"{key}_unidad"] = "La unidad es obligatoria."
        elif not unidad_permitida_para_producto(owner, producto, unidad):
            errors[f"{key}_unidad"] = (
                f"Unidad no válida para {producto.nombre}. "
                "Selecciona una unidad configurada en Conversiones."
            )

        if len(errors) > errores_antes:
            continue

        filas.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "unidad": unidad[:20],
                "orden": orden,
                "notas": (notas or "").strip()[:100],
            }
        )

    return filas


def ingredientes_filas_from_post(data):
    filas = []
    for producto_id, cantidad, unidad, notas in _zip_rows(
        data["ingredientes_producto"],
        data["ingredientes_cantidad"],
        data["ingredientes_unidad"],
        data["ingredientes_notas"],
    ):
        if not producto_id and not cantidad and not unidad:
            continue
        filas.append(
            {
                "producto_id": str(producto_id or ""),
                "cantidad": cantidad or "",
                "unidad": unidad or "",
                "notas": notas or "",
            }
        )
    return filas


def ingredientes_filas_from_version(version):
    return [
        {
            "producto_id": str(linea.producto_id),
            "cantidad": str(linea.cantidad),
            "unidad": linea.unidad,
            "notas": linea.notas,
        }
        for linea in version.ingredientes.all()
    ]


def _fila_indirecto_vacia(gasto_id, cantidad_raw, notas):
    return (
        not gasto_id
        and cantidad_raw in (None, "")
        and not (notas or "").strip()
    )


def _validar_indirectos(data, owner, errors):
    filas = []
    gastos_usados = set()

    for orden, (gasto_id, cantidad_raw, notas) in enumerate(
        _zip_rows(
            data["indirectos_gasto"],
            data["indirectos_cantidad"],
            data["indirectos_notas"],
        )
    ):
        if _fila_indirecto_vacia(gasto_id, cantidad_raw, notas):
            continue

        key = f"indirecto_{orden}"
        errores_antes = len(errors)

        if not gasto_id:
            errors[f"{key}_gasto"] = "Selecciona un costo indirecto."
            continue

        gasto = CostoIndirecto.objects.filter(
            owner=owner,
            pk=gasto_id,
            status=CatalogStatus.ACTIVO,
        ).first()
        if gasto is None:
            errors[f"{key}_gasto"] = "Costo indirecto no válido o inactivo."
            continue

        if gasto.pk in gastos_usados:
            errors[f"{key}_gasto"] = (
                f"«{gasto.nombre}» ya está en la formulación. "
                "Solo un registro por gasto; suma las cantidades en una sola línea."
            )
            continue
        gastos_usados.add(gasto.pk)

        cantidad = _parse_decimal(
            cantidad_raw,
            f"{key}_cantidad",
            errors,
            min_value=Decimal("0"),
        )

        if len(errors) > errores_antes:
            continue

        filas.append(
            {
                "costo_indirecto": gasto,
                "cantidad": cantidad,
                "orden": orden,
                "notas": (notas or "").strip()[:100],
            }
        )

    return filas


def indirectos_filas_from_post(data):
    filas = []
    for gasto_id, cantidad, notas in _zip_rows(
        data["indirectos_gasto"],
        data["indirectos_cantidad"],
        data["indirectos_notas"],
    ):
        if _fila_indirecto_vacia(gasto_id, cantidad, notas):
            continue
        filas.append(
            {
                "gasto_id": str(gasto_id or ""),
                "cantidad": "" if cantidad in (None, "") else str(cantidad),
                "notas": notas or "",
            }
        )
    return filas


def indirectos_filas_from_version(version):
    return [
        {
            "gasto_id": str(linea.costo_indirecto_id),
            "cantidad": str(linea.cantidad),
            "notas": linea.notas,
        }
        for linea in version.costos_indirectos.all()
    ]


def _zip_rows(*lists):
    if not lists:
        return []
    length = max(len(lst) for lst in lists)
    rows = []
    for index in range(length):
        row = tuple(lst[index] if index < len(lst) else "" for lst in lists)
        rows.append(row)
    return rows


@transaction.atomic
def guardar_formulacion(version, owner, data, errors):
    rendimiento, precio = validate_formulacion_header(data, errors)
    if errors:
        return False

    ingredientes_validados = _validar_ingredientes(data, owner, errors)
    indirectos_validados = _validar_indirectos(data, owner, errors)

    if errors:
        return False

    version.rendimiento_cantidad = rendimiento
    version.rendimiento_unidad = data["rendimiento_unidad"].strip()[:30]
    version.save(update_fields=["rendimiento_cantidad", "rendimiento_unidad", "updated_at"])

    version.ingredientes.all().delete()
    version.costos_indirectos.all().delete()
    version.pasos.all().delete()

    for item in ingredientes_validados:
        RecetaIngrediente.objects.create(
            version=version,
            producto=item["producto"],
            cantidad=item["cantidad"],
            unidad=item["unidad"],
            orden=item["orden"],
            notas=item["notas"],
        )

    for item in indirectos_validados:
        RecetaCostoIndirecto.objects.create(
            version=version,
            costo_indirecto=item["costo_indirecto"],
            cantidad=item["cantidad"],
            orden=item["orden"],
            notas=item["notas"],
        )

    paso_orden = 0
    for instruccion, tiempo_raw in _zip_rows(data["pasos_instruccion"], data["pasos_tiempo"]):
        texto = (instruccion or "").strip()
        if not texto:
            continue
        paso_orden += 1
        errores_antes = len(errors)
        tiempo = None
        if tiempo_raw not in (None, ""):
            try:
                tiempo_val = int(str(tiempo_raw).strip())
                if tiempo_val <= 0:
                    errors[f"paso_{paso_orden}_tiempo"] = "El tiempo debe ser mayor que 0."
                else:
                    tiempo = tiempo_val
            except ValueError:
                errors[f"paso_{paso_orden}_tiempo"] = "Tiempo inválido."
        if len(errors) > errores_antes:
            continue
        RecetaPaso.objects.create(
            version=version,
            orden=paso_orden,
            instruccion=texto,
            tiempo_minutos=tiempo,
        )

    if errors:
        transaction.set_rollback(True)
        return False

    recalcular_totales_version(version, actualizar_precio=not data["precio_override_manual"])
    if data["precio_override_manual"] and precio is not None:
        version.precio_venta_sugerido = precio
        version.save(update_fields=["precio_venta_sugerido", "updated_at"])
    return True


@transaction.atomic
def crear_nueva_version(receta, notas_cambio=""):
    origen = receta.version_actual
    if origen is None:
        raise ValueError("La receta no tiene versión actual.")

    max_num = receta.versiones.aggregate(m=Max("numero_version"))["m"] or 0
    nueva = RecetaVersion.objects.create(
        receta=receta,
        numero_version=max_num + 1,
        notas_cambio=(notas_cambio or "").strip(),
        rendimiento_cantidad=origen.rendimiento_cantidad,
        rendimiento_unidad=origen.rendimiento_unidad,
        precio_venta_sugerido=origen.precio_venta_sugerido,
        margen_aplicado_pct=origen.margen_aplicado_pct,
    )

    for linea in origen.ingredientes.all():
        RecetaIngrediente.objects.create(
            version=nueva,
            producto=linea.producto,
            cantidad=linea.cantidad,
            unidad=linea.unidad,
            orden=linea.orden,
            notas=linea.notas,
            cantidad_normalizada=linea.cantidad_normalizada,
            costo_linea=linea.costo_linea,
        )
    for linea in origen.costos_indirectos.all():
        RecetaCostoIndirecto.objects.create(
            version=nueva,
            costo_indirecto=linea.costo_indirecto,
            cantidad=linea.cantidad,
            costo_linea=linea.costo_linea,
            orden=linea.orden,
            notas=linea.notas,
        )
    for paso in origen.pasos.all():
        RecetaPaso.objects.create(
            version=nueva,
            orden=paso.orden,
            instruccion=paso.instruccion,
            tiempo_minutos=paso.tiempo_minutos,
        )

    recalcular_totales_version(nueva)
    receta.version_actual = nueva
    receta.save(update_fields=["version_actual", "updated_at"])
    return nueva


def formulacion_context(version, owner):
    productos = Producto.objects.filter(owner=owner, status=CatalogStatus.ACTIVO).order_by(
        "nombre"
    )
    indirectos = CostoIndirecto.objects.filter(
        owner=owner,
        status=CatalogStatus.ACTIVO,
    ).order_by("nombre")
    unidades_conversion = list_unidades_desde_conversiones(owner)
    unidades_por_producto = {
        str(producto.pk): unidades_para_producto(owner, producto) for producto in productos
    }
    productos_nombres = {str(producto.pk): producto.nombre for producto in productos}
    indirectos_nombres = {str(gasto.pk): gasto.nombre for gasto in indirectos}
    return {
        "productos_activos": productos,
        "productos_nombres": productos_nombres,
        "indirectos_activos": indirectos,
        "indirectos_nombres": indirectos_nombres,
        "unidades_conversion": unidades_conversion,
        "unidades_por_producto": unidades_por_producto,
        "ingredientes": version.ingredientes.select_related("producto"),
        "ingredientes_filas": ingredientes_filas_from_version(version),
        "indirectos_filas": indirectos_filas_from_version(version),
        "indirectos": version.costos_indirectos.select_related("costo_indirecto"),
        "pasos": version.pasos.all(),
    }
