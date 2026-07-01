import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();

const CATALOG_ROUTES = [
  { path: "/app/productos/", name: "productos" },
  { path: "/app/categorias/", name: "categorías" },
  { path: "/app/conversiones/", name: "conversiones" },
  { path: "/app/costos-indirectos/", name: "costos indirectos" },
] as const;

test.describe("Catalog — acceso", () => {
  for (const route of CATALOG_ROUTES) {
    test(`${route.name} redirige a login sin sesión`, async ({ page }) => {
      await page.goto(route.path);
      await expect(page).toHaveURL(/\/ingresar\/?/);
    });
  }
});

test.describe("Catalog — navegación sidebar", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/");
  });

  test("enlace Productos", async ({ page }) => {
    await page.getByRole("link", { name: "Productos", exact: true }).click();
    await expect(page).toHaveURL(/\/app\/productos\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Productos" })).toBeVisible();
  });

  test("submenú Catálogo base: categorías, conversiones y costos indirectos", async ({ page }) => {
    await page.getByRole("button", { name: "Catálogo base" }).click();
    const sub = page.locator("#nav-catalogo-base");
    await expect(sub.getByRole("link", { name: "Categorías" })).toBeVisible();
    await expect(sub.getByRole("link", { name: "Conversiones de unidad" })).toBeVisible();
    await expect(sub.getByRole("link", { name: "Costos indirectos" })).toBeVisible();

    await sub.getByRole("link", { name: "Categorías" }).click();
    await expect(page).toHaveURL(/\/app\/categorias\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Categorias" })).toBeVisible();
  });
});

test.describe("Catalog — Productos", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test.describe("Listado", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/productos/");
    });

    test("cabecera y enlace alta", async ({ page }) => {
      await expect(page).toHaveTitle(/Productos/i);
      await expect(page.getByRole("heading", { level: 1, name: "Productos" })).toBeVisible();
      await expect(page.getByText("Catalogo de insumos")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nuevo producto" })).toHaveAttribute(
        "href",
        /\/app\/productos\/nuevo\/?$/
      );
    });

    test("filtros y tabla", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar productos" });
      await expect(filters.getByLabel("Nombre")).toBeVisible();
      await expect(filters.getByLabel("Categoria")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const table = page.locator("#tabla-productos");
      await expect(table.getByRole("columnheader", { name: "Nombre" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Categoria" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Unidad base" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Costo / unidad" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });

    test("limpiar filtros vacía los campos", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar productos" });
      await filters.getByLabel("Nombre").fill("harina");
      await filters.locator("#filter-estado").selectOption("Activo");
      await filters.getByRole("button", { name: "Limpiar filtros" }).click();
      await expect(filters.getByLabel("Nombre")).toHaveValue("");
      await expect(filters.locator("#filter-estado")).toHaveValue("");
    });
  });

  test("alta: formulario y ayuda", async ({ page }) => {
    await page.goto("/app/productos/nuevo/");
    await expect(page.getByRole("heading", { level: 1, name: "Nuevo producto" })).toBeVisible();

    const form = page.locator("form.productos-form");
    await expect(form.getByRole("heading", { name: "Datos basicos" })).toBeVisible();
    await expect(form.getByLabel("Nombre *")).toBeVisible();
    await expect(form.getByLabel("Categoria *")).toBeVisible();
    await expect(form.getByLabel("Estado *")).toBeVisible();
    await expect(form.getByRole("heading", { name: "Costo y unidad base" })).toBeVisible();
    await expect(form.getByLabel("Unidad base *")).toBeVisible();
    await expect(form.getByLabel("Costo por unidad base *")).toBeVisible();
    await expect(form.getByLabel("Proveedor")).toBeVisible();
    await expect(form.getByLabel("Notas")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar producto" })).toBeVisible();

    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/productos\/nuevo\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: crear producto" })).toBeVisible();
    await expect(page.getByRole("link", { name: "← Volver al formulario" })).toBeVisible();
  });

  test("edición desde fila del listado", async ({ page }) => {
    await page.goto("/app/productos/");
    const editLink = page.locator("#tabla-productos").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay productos para editar");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/productos\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Editar producto" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar cambios" })).toBeVisible();
  });

  test("eliminar: pantalla de confirmación", async ({ page }) => {
    await page.goto("/app/productos/");
    const deleteLink = page.locator("#tabla-productos").getByRole("link", { name: "Eliminar" }).first();
    test.skip((await deleteLink.count()) === 0, "No hay productos para eliminar");

    await deleteLink.click();
    await expect(page).toHaveURL(/\/app\/productos\/\d+\/eliminar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Eliminar producto" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Si, eliminar" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Cancelar" })).toHaveAttribute(
      "href",
      /\/app\/productos\/?$/
    );
  });
});

test.describe("Catalog — Categorías", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test.describe("Listado", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/categorias/");
    });

    test("cabecera y enlace alta", async ({ page }) => {
      await expect(page).toHaveTitle(/Categorias/i);
      await expect(page.getByRole("heading", { level: 1, name: "Categorias" })).toBeVisible();
      await expect(page.getByText("Clasificacion de productos")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nueva categoria" })).toHaveAttribute(
        "href",
        /\/app\/categorias\/nuevo\/?$/
      );
    });

    test("filtros y tabla", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar categorias" });
      await expect(filters.getByLabel("Nombre")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByLabel("Predeterminada")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const table = page.locator("#tabla-categorias");
      await expect(table.getByRole("columnheader", { name: "Orden" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Nombre" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Codigo" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Color" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Predeterminada" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });
  });

  test("alta: formulario y ayuda", async ({ page }) => {
    await page.goto("/app/categorias/nuevo/");
    await expect(page.getByRole("heading", { level: 1, name: "Nueva categoria" })).toBeVisible();

    const form = page.locator("form");
    await expect(form.getByRole("heading", { name: "Datos de categoria" })).toBeVisible();
    await expect(form.getByLabel("Nombre *")).toBeVisible();
    await expect(form.getByLabel("Codigo")).toBeVisible();
    await expect(form.getByLabel("Orden")).toBeVisible();
    await expect(form.getByLabel("Color")).toBeVisible();
    await expect(form.getByLabel("Estado *")).toBeVisible();
    await expect(form.getByLabel("Descripcion")).toBeVisible();
    await expect(form.getByLabel("Marcar como predeterminada")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar categoria" })).toBeVisible();

    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/categorias\/nuevo\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: crear categoría" })).toBeVisible();
  });

  test("edición desde fila del listado", async ({ page }) => {
    await page.goto("/app/categorias/");
    const editLink = page.locator("#tabla-categorias").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay categorías para editar");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/categorias\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Editar categoria" })).toBeVisible();
  });
});

test.describe("Catalog — Conversiones", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test.describe("Listado", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/conversiones/");
    });

    test("cabecera y enlace alta", async ({ page }) => {
      await expect(page).toHaveTitle(/Conversiones/i);
      await expect(page.getByRole("heading", { level: 1, name: "Conversiones de unidad" })).toBeVisible();
      await expect(page.getByText("Reglas de equivalencia")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nueva conversion" })).toHaveAttribute(
        "href",
        /\/app\/conversiones\/nuevo\/?$/
      );
    });

    test("filtros y tabla", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar conversiones" });
      await expect(filters.getByLabel("Etiqueta / unidad")).toBeVisible();
      await expect(filters.getByLabel("Alcance")).toBeVisible();
      await expect(filters.getByLabel("Hacia unidad")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const table = page.locator("#tabla-conversiones");
      await expect(table.getByRole("columnheader", { name: "Etiqueta" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Alcance" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Desde" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Hacia" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Factor" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Equivalencia" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });
  });

  test("alta: formulario y ayuda", async ({ page }) => {
    await page.goto("/app/conversiones/nuevo/");
    await expect(page.getByRole("heading", { level: 1, name: "Nueva conversion" })).toBeVisible();

    const form = page.locator("form");
    await expect(form.getByRole("heading", { name: "Datos de conversion" })).toBeVisible();
    await expect(form.getByLabel("Producto (opcional)")).toBeVisible();
    await expect(form.getByLabel("Etiqueta")).toBeVisible();
    await expect(form.getByLabel("Desde unidad *")).toBeVisible();
    await expect(form.getByLabel("Hacia unidad *")).toBeVisible();
    await expect(form.getByLabel("Factor *")).toBeVisible();
    await expect(form.getByLabel("Notas")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar conversion" })).toBeVisible();

    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/conversiones\/nuevo\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: crear conversión" })).toBeVisible();
  });

  test("edición desde fila del listado", async ({ page }) => {
    await page.goto("/app/conversiones/");
    const editLink = page.locator("#tabla-conversiones").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay conversiones para editar");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/conversiones\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Editar conversion" })).toBeVisible();
  });
});

test.describe("Catalog — Costos indirectos", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test.describe("Listado", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/costos-indirectos/");
    });

    test("cabecera y enlace alta", async ({ page }) => {
      await expect(page).toHaveTitle(/Costos indirectos/i);
      await expect(page.getByRole("heading", { level: 1, name: "Costos indirectos" })).toBeVisible();
      await expect(page.getByText("Catalogo de costos de operacion")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nuevo costo indirecto" })).toHaveAttribute(
        "href",
        /\/app\/costos-indirectos\/nuevo\/?$/
      );
    });

    test("filtros y tabla", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar costos indirectos" });
      await expect(filters.getByLabel("Nombre")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByLabel("Unidad cobro")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const table = page.locator("#tabla-costos-indirectos");
      await expect(table.getByRole("columnheader", { name: "Nombre" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Costo/unidad" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Unidad cobro" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Tarifa ref." })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });
  });

  test("alta: formulario y ayuda", async ({ page }) => {
    await page.goto("/app/costos-indirectos/nuevo/");
    await expect(page.getByRole("heading", { level: 1, name: "Nuevo costo indirecto" })).toBeVisible();

    const form = page.locator("form");
    await expect(form.getByRole("heading", { name: "Datos de costo" })).toBeVisible();
    await expect(form.getByLabel("Nombre *")).toBeVisible();
    await expect(form.getByLabel("Unidad cobro *")).toBeVisible();
    await expect(form.getByLabel("Costo por unidad *")).toBeVisible();
    await expect(form.getByLabel("Estado *")).toBeVisible();
    await expect(form.getByLabel("Notas")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar costo indirecto" })).toBeVisible();

    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/costos-indirectos\/nuevo\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: crear costo indirecto" })).toBeVisible();
  });

  test("edición desde fila del listado", async ({ page }) => {
    await page.goto("/app/costos-indirectos/");
    const editLink = page.locator("#tabla-costos-indirectos").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay costos indirectos para editar");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/costos-indirectos\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Editar costo indirecto" })).toBeVisible();
  });
});
