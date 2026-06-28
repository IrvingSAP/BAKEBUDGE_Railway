# Reglas del módulo Perfil — `UserProfile` (`apps.accounts`)



**Estado:** **Conforme v1** (2026-06-20) — perfil de negocio Django + enlace a **Seguridad de la cuenta** (**Conforme v1**, validación manual OK).



Configuración de negocio y preferencias del usuario conectado (`UserProfile`).



**Template Django:** `apps/accounts/templates/accounts/perfil.html` · **URL:** `/app/perfil/`  

**Checklist prototipo:** [`perfil-checklist-conforme.md`](perfil-checklist-conforme.md)  

**Seguridad cuenta:** [`cuenta-seguridad-reglas.md`](cuenta-seguridad-reglas.md) · **Checklist:** [`cuenta-seguridad-checklist-conforme.md`](cuenta-seguridad-checklist-conforme.md)  

**Modelo:** [`BAKEBUDGE_MODELS.md#userprofile`](BAKEBUDGE_MODELS.md#userprofile)  

**Relacionado:** [`dashboard-reglas.md`](dashboard-reglas.md), [`BAKEBUDGE_ANALYTICS.md`](BAKEBUDGE_ANALYTICS.md), [`acceso-reglas.md`](acceso-reglas.md)



```bash

# Django

# Perfil:    http://127.0.0.1:8000/app/perfil/

# Seguridad: http://127.0.0.1:8000/app/seguridad/cuenta/

```



---



## Alcance



| Incluye | No incluye |

|---------|------------|

| Datos del negocio (`nombre_negocio`, `moneda`, `margen_objetivo_pct`) | Avatar / logo (`ImageField`) |

| Unidades por defecto (peso, volumen, conteo) | Django `UserProfile` CRUD Master |

| Resumen cuenta (readonly) + enlace seguridad | Billing / suscripción |

| Enlace **Seguridad de la cuenta** → cambio contraseña + reset 2FA | Edición de email/username en Perfil |



Acceso menú: **Perfil** → `/app/perfil/`.



---



## Regla fundamental



- Solo el perfil de `request.user` (`UserProfile.user`).

- Sidebar y topbar: `app_profile.nombre_negocio` (topbar en chip; pie sidebar con email y username de referencia).



---



## Pantalla Perfil (`/app/perfil/`)



### Sección — Datos del negocio



| Campo | Modelo | Regla |

|-------|--------|-------|

| `nombre_negocio` | `UserProfile.nombre_negocio` | Obligatorio, máx. 150 |

| `moneda` | `UserProfile.moneda` → `Moneda` | Solo `activa=True` (+ moneda actual si quedó inactiva) |

| `margen_objetivo_pct` | `UserProfile.margen_objetivo_pct` | Numérico ≥ 0; default 40 |



Botón **Guardar cambios** → modal OK + redirect PRG.



### Sección — Unidades por defecto



| Campo | Opciones |

|-------|----------|

| `unidad_peso_default` | g, kg |

| `unidad_volumen_default` | ml, L |

| `unidad_conteo_default` | unidad |



Mismo formulario POST que datos del negocio.



### Sección — Cuenta y seguridad (readonly)



Usuario, correo, estado 2FA. Enlace a [`/app/seguridad/cuenta/`](cuenta-seguridad-reglas.md).



---



## Impacto en otros módulos



| Campo perfil | Usado en |

|--------------|----------|

| `margen_objetivo_pct` | `RecetaVersion.precio_venta_sugerido`, analytics |

| `moneda` | Formato costos en productos, recetas, producción |

| `unidad_*_default` | Alta productos / conversiones (futuro) |



---



## Archivos Django



| Archivo | Rol |

|---------|-----|

| `apps/accounts/views.py` | `perfil`, `cuenta_seguridad` |

| `apps/accounts/services/perfil_helpers.py` | Validación perfil negocio |

| `apps/accounts/templates/accounts/perfil.html` | Template perfil |

| `apps/accounts/tests.py` | Tests |



---



## Registro



| Fecha | Evento |

|-------|--------|

| 2026-06-16 | Prototipo + reglas — checklist **Conforme** |

| 2026-06-20 | Implementación Django `/app/perfil/` |
| 2026-06-20 | Seguridad de la cuenta — **Conforme v1** (validación manual usuario nuevo) |

