"""Utilidades de presentación para noticias."""


def resumen_texto(noticia, *, max_len: int = 200) -> str:
    if noticia.resumen:
        return noticia.resumen.strip()
    detalle = (noticia.detalle or "").strip()
    if len(detalle) <= max_len:
        return detalle
    return detalle[: max_len - 1].rstrip() + "…"


def tipo_badge_class(tipo: str) -> str:
    value = (tipo or "").lower()
    if "manten" in value:
        return "badge-system"
    if "aviso" in value:
        return "badge-draft"
    if "mejora" in value:
        return "badge-active"
    if "nueva" in value:
        return "badge-type-user"
    return "badge-process"
