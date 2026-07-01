from django.db import models


class Status(models.TextChoices):
    EN_PROCESO = "P", "En proceso"
    ACTIVO = "A", "Activo"
    INACTIVO = "I", "Inactivo"


STATUS_CHOICES = Status.choices


class UnidadCobro(models.TextChoices):
    HORA = "hora", "Hora"
    MINUTO = "minuto", "Minuto"
    LOTE = "lote", "Lote"
    PORCION = "porcion", "Porcion"
    MES = "mes", "Mes"
    FIJO = "fijo", "Fijo"


UNIDAD_COBRO_CHOICES = UnidadCobro.choices


CATEGORIA_COLOR_CHOICES = (
    ("#FFFFFF", "Blanco"),
    ("#FAFAFA", "Gris muy claro"),
    ("#F5F5F5", "Gris claro"),
    ("#EEEEEE", "Gris perla"),
    ("#E0E0E0", "Gris plateado"),
    ("#BDBDBD", "Gris medio"),
    ("#9E9E9E", "Gris"),
    ("#757575", "Gris oscuro"),
    ("#424242", "Grafito"),
    ("#212121", "Negro suave"),
    ("#FFF8E1", "Crema"),
    ("#FFFDE7", "Vainilla"),
    ("#FFF3E0", "Durazno claro"),
    ("#FFE0B2", "Melocotón"),
    ("#FFCCBC", "Salmón claro"),
    ("#FFECB3", "Mantequilla"),
    ("#FFE082", "Miel clara"),
    ("#FFD54F", "Amarillo pastel"),
    ("#FFF176", "Limón suave"),
    ("#F0F4C3", "Verde lima claro"),
    ("#DCEDC8", "Menta clara"),
    ("#C8E6C9", "Verde menta"),
    ("#A5D6A7", "Verde pastel"),
    ("#81C784", "Verde fresco"),
    ("#AED581", "Verde manzana"),
    ("#B2DFDB", "Aqua claro"),
    ("#80DEEA", "Cian suave"),
    ("#81D4FA", "Azul cielo"),
    ("#90CAF9", "Azul pastel"),
    ("#BBDEFB", "Azul claro"),
    ("#C5CAE9", "Lavanda claro"),
    ("#D1C4E9", "Lila suave"),
    ("#E1BEE7", "Rosa lila"),
    ("#F8BBD0", "Rosa pastel"),
    ("#F48FB1", "Rosa"),
    ("#FFCDD2", "Rosa claro"),
    ("#EF9A9A", "Coral claro"),
    ("#FFAB91", "Naranja suave"),
    ("#FF8A65", "Naranja"),
    ("#FFCC80", "Albaricoque"),
    ("#D7CCC8", "Beige"),
    ("#BCAAA4", "Taupe"),
    ("#A1887F", "Marrón claro"),
    ("#8D6E63", "Cacao"),
    ("#795548", "Chocolate"),
    ("#6D4C41", "Café"),
    ("#E8D5C4", "Arena"),
    ("#D4A574", "Caramelo"),
    ("#C9956C", "Toffee"),
    ("#B87333", "Cobre"),
)

CATEGORIA_COLOR_VALUES = {hex_code for hex_code, _ in CATEGORIA_COLOR_CHOICES}
