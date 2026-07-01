import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();
const RECETAS_LIST = "/app/recetas/";

test.describe("Recipes — acceso", () => {
  test("listado redirige a login sin sesión", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });

  test("nueva receta redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/recetas/nuevo/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Recipes — listado (/app/recetas/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto(RECETAS_LIST);
  });

  test("cabecera y enlace alta", async ({ page }) => {
    await expect(page).toHaveTitle(/Recetas/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "recetas");
    await expect(page.getByRole("heading", { level: 1, name: "Recetas" })).toBeVisible();
    await expect(page.getByText("Cabecera de receta")).toBeVisible();
    await expect(page.getByRole("link", { name: "+ Nueva receta" })).toHaveAttribute(
      "href",
      /\/app\/recetas\/nuevo\/?$/
    );
  });

  test("filtros y tabla", async ({ page }) => {
    const filters = page.getByRole("search", { name: "Filtrar recetas" });
    await expect(filters.getByLabel("Nombre")).toBeVisible();
    await expect(filters.getByLabel("Estado")).toBeVisible();
    await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

    const table = page.locator("#tabla-recetas");
    await expect(table.getByRole("columnheader", { name: "Receta" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Versión" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Rendimiento" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Costo total" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Costo / porción" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Precio sugerido" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
  });

  test("limpiar filtros vacía los campos", async ({ page }) => {
    const filters = page.getByRole("search", { name: "Filtrar recetas" });
    await filters.getByLabel("Nombre").fill("brownie");
    await filters.locator("#filter-estado").selectOption("Activo");
    await filters.getByRole("button", { name: "Limpiar filtros" }).click();
    await expect(filters.getByLabel("Nombre")).toHaveValue("");
    await expect(filters.locator("#filter-estado")).toHaveValue("");
  });

  test("sidebar: enlace Recetas", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("link", { name: "Recetas", exact: true }).click();
    await expect(page).toHaveURL(/\/app\/recetas\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Recetas" })).toBeVisible();
  });
});

test.describe("Recipes — alta y cabecera", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("nueva receta: formulario v1 y ayuda", async ({ page }) => {
    await page.goto("/app/recetas/nuevo/");
    await expect(page.getByRole("heading", { level: 1, name: "Nueva receta" })).toBeVisible();
    await expect(page.getByText("versión inicial")).toBeVisible();

    const form = page.locator("form.recetas-form");
    await expect(form.getByRole("heading", { name: "Identificación" })).toBeVisible();
    await expect(form.getByLabel("Nombre")).toBeVisible();
    await expect(form.getByLabel("Descripción corta")).toBeVisible();
    await expect(form.getByLabel("Notas")).toBeVisible();
    await expect(form.getByLabel("Imagen")).toBeVisible();
    await expect(form.getByRole("heading", { name: "Versión inicial v1" })).toBeVisible();
    await expect(form.getByLabel("Cantidad")).toBeVisible();
    await expect(form.getByLabel("Unidad")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar y marcar activo" })).toBeVisible();

    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/recetas\/nuevo\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: crear receta" })).toBeVisible();
  });

  test("edición desde fila del listado", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const editLink = page.locator("#tabla-recetas").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay recetas para editar");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Editar receta" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Estado y versión vigente" })).toBeVisible();
  });

  test("eliminar: pantalla de confirmación", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const deleteLink = page.locator("#tabla-recetas").getByRole("link", { name: "Eliminar" }).first();
    test.skip((await deleteLink.count()) === 0, "No hay recetas para eliminar");

    await deleteLink.click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/eliminar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Eliminar receta" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Inactivar" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Eliminar permanentemente" })).toBeVisible();
  });
});

test.describe("Recipes — formulación y costos", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("formulación vigente: secciones y ayuda", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const formLink = page.locator("#tabla-recetas").getByRole("link", { name: "Formulación" }).first();
    test.skip((await formLink.count()) === 0, "No hay recetas con versión vigente");

    await formLink.click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/version\/?$/);
    await expect(page.locator(".badge-vigente")).toContainText("vigente");
    await expect(page.getByRole("heading", { name: "Resumen de costos" })).toBeVisible();
    await expect(page.getByLabel("Precio sugerido")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Rendimiento" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Ingredientes" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Costos indirectos" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Pasos de elaboración" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar formulación" })).toBeVisible();

    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/version\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: formulación" })).toBeVisible();
  });

  test("costos: desglose de versión vigente", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const costosLink = page.locator("#tabla-recetas").getByRole("link", { name: "Costos" }).first();
    test.skip((await costosLink.count()) === 0, "No hay recetas con costos");

    await costosLink.click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/costos\/?$/);
    await expect(page.getByText("Desglose de costos de la versión vigente")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Resumen de costos" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Detalle de costos — ingredientes" })).toBeVisible();
    await expect(page.locator(".recetaversion-cost-panel")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Navegación receta" })).toBeVisible();
  });

  test("historial de versiones", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const formLink = page.locator("#tabla-recetas").getByRole("link", { name: "Formulación" }).first();
    test.skip((await formLink.count()) === 0, "No hay recetas con versión");

    await formLink.click();
    await page.getByRole("navigation", { name: "Navegación versión" }).getByRole("link", { name: "Historial" }).click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/versiones\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Historial de versiones" })).toBeVisible();
    await expect(page.getByRole("columnheader", { name: "Versión" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Formulación vigente" })).toBeVisible();
  });

  test("detalle de versión histórica", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const formLink = page.locator("#tabla-recetas").getByRole("link", { name: "Formulación" }).first();
    test.skip((await formLink.count()) === 0, "No hay recetas con versión");

    await formLink.click();
    await page.getByRole("navigation", { name: "Navegación versión" }).getByRole("link", { name: "Historial" }).click();

    const verDetalle = page.getByRole("link", { name: "Ver detalle" }).first();
    test.skip((await verDetalle.count()) === 0, "No hay versiones en el historial");

    await verDetalle.click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/versiones\/\d+\/?$/);
    await expect(page.getByText("Versión histórica — solo lectura")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Resumen" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Ingredientes" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Pasos" })).toBeVisible();
  });

  test("nueva versión: formulario motivo", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const formLink = page.locator("#tabla-recetas").getByRole("link", { name: "Formulación" }).first();
    test.skip((await formLink.count()) === 0, "No hay recetas con versión");

    await formLink.click();
    await page.getByRole("navigation", { name: "Navegación versión" }).getByRole("link", { name: "Nueva versión" }).click();
    await expect(page).toHaveURL(/\/app\/recetas\/\d+\/version\/nueva\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Nueva versión" })).toBeVisible();
    await expect(page.getByLabel("Motivo del cambio")).toBeVisible();
    await expect(page.getByRole("button", { name: "Crear nueva versión" })).toBeVisible();
  });

  test("enlace Producir desde listado", async ({ page }) => {
    await page.goto(RECETAS_LIST);
    const producirLink = page.locator("#tabla-recetas").getByRole("link", { name: "Producir" }).first();
    test.skip((await producirLink.count()) === 0, "No hay recetas con versión para producir");

    await expect(producirLink).toHaveAttribute("href", /\/app\/produccion\/nueva\/\?receta_id=\d+/);
  });
});
