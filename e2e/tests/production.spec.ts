import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();
const PRODUCCION_LIST = "/app/produccion/";

test.describe("Production — acceso", () => {
  test("listado redirige a login sin sesión", async ({ page }) => {
    await page.goto(PRODUCCION_LIST);
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });

  test("nueva orden redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/produccion/nueva/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });

  test("detalle redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/produccion/1/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Production — listado (/app/produccion/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto(PRODUCCION_LIST);
  });

  test("cabecera y enlace alta", async ({ page }) => {
    await expect(page).toHaveTitle(/Producción/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "produccion");
    await expect(page.getByRole("heading", { level: 1, name: "Órdenes de producción" })).toBeVisible();
    await expect(page.getByText("Planifica lotes")).toBeVisible();
    await expect(page.getByRole("link", { name: "+ Nueva orden" })).toHaveAttribute(
      "href",
      /\/app\/produccion\/nueva\/?$/
    );
  });

  test("filtros y tabla", async ({ page }) => {
    const filters = page.getByRole("search", { name: "Filtrar órdenes" });
    await expect(filters.getByLabel("Código o receta")).toBeVisible();
    await expect(filters.getByLabel("Estado")).toBeVisible();
    await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

    const estado = filters.locator("#filter-estado");
    await expect(estado.locator('option[value="Borrador"]')).toHaveText("Borrador");
    await expect(estado.locator('option[value="Completada"]')).toHaveText("Completada");

    const table = page.locator("#tabla-ordenes");
    await expect(table.getByRole("columnheader", { name: "Código" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Receta" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Lotes" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Costo estimado" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Fecha" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
  });

  test("limpiar filtros vacía los campos", async ({ page }) => {
    const filters = page.getByRole("search", { name: "Filtrar órdenes" });
    await filters.getByLabel("Código o receta").fill("ORD");
    await filters.locator("#filter-estado").selectOption("Borrador");
    await filters.getByRole("button", { name: "Limpiar filtros" }).click();
    await expect(filters.getByLabel("Código o receta")).toHaveValue("");
    await expect(filters.locator("#filter-estado")).toHaveValue("");
  });

  test("sidebar: enlace Producción", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("link", { name: "Producción", exact: true }).click();
    await expect(page).toHaveURL(/\/app\/produccion\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Órdenes de producción" })).toBeVisible();
  });
});

test.describe("Production — nueva orden", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/produccion/nueva/");
  });

  test("formulario: receta, planificación y vista previa", async ({ page }) => {
    await expect(page.getByRole("heading", { level: 1, name: "Nueva orden de producción" })).toBeVisible();
    await expect(page.getByText("Planificación en estado")).toBeVisible();

    const form = page.locator("#form-orden-create");
    await expect(form.getByRole("heading", { name: "Receta y versión" })).toBeVisible();
    await expect(form.getByLabel("Receta")).toBeVisible();
    await expect(form.getByRole("heading", { name: "Planificación" })).toBeVisible();
    await expect(form.getByLabel("Cantidad de lotes")).toBeVisible();
    await expect(form.getByLabel("Fecha programada")).toBeVisible();
    await expect(form.getByLabel("Notas")).toBeVisible();
    await expect(page.getByRole("button", { name: "Crear orden" })).toBeVisible();

    const preview = page.locator(".produccion-preview");
    await expect(preview.getByText("Costo estimado")).toBeVisible();
    await expect(preview.getByText("Rendimiento esperado")).toBeVisible();
    await expect(preview.getByText("Costo / porción")).toBeVisible();
  });

  test("ayuda en la misma pestaña", async ({ page }) => {
    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/produccion\/nueva\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: nueva orden de producción" })).toBeVisible();
    await expect(page.getByRole("link", { name: "← Volver al formulario" })).toHaveAttribute(
      "href",
      /\/app\/produccion\/nueva\/?$/
    );
  });
});

test.describe("Production — detalle y edición", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("detalle desde fila Ver", async ({ page }) => {
    await page.goto(PRODUCCION_LIST);
    const verLink = page.locator("#tabla-ordenes").getByRole("link", { name: "Ver" }).first();
    test.skip((await verLink.count()) === 0, "No hay órdenes en el listado");

    await verLink.click();
    await expect(page).toHaveURL(/\/app\/produccion\/\d+\/?$/);

    await expect(page.locator("h1.orden-codigo")).toBeVisible();
    await expect(page.locator(".produccion-detail-header .badge")).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Planificación" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Costos" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Formulación escalada" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 3, name: "Ingredientes" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 3, name: "Costos indirectos" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 3, name: "Pasos" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Listado" })).toHaveAttribute(
      "href",
      /\/app\/produccion\/?$/
    );
  });

  test("detalle: acciones según estado", async ({ page }) => {
    await page.goto(PRODUCCION_LIST);
    const verLink = page.locator("#tabla-ordenes").getByRole("link", { name: "Ver" }).first();
    test.skip((await verLink.count()) === 0, "No hay órdenes en el listado");

    await verLink.click();
    const acciones = page.locator("section.card", {
      has: page.getByRole("heading", { level: 2, name: "Acciones" }),
    });
    const completar = page.locator("#panel-completar");
    const completada = page.getByText("Orden completada");
    const cancelada = page.getByText("Orden cancelada");

    if (await acciones.isVisible()) {
      await expect(acciones.getByRole("button", { name: "Cancelar orden" })).toBeVisible();
      const iniciar = acciones.getByRole("button", { name: "Iniciar producción" });
      const editar = acciones.getByRole("link", { name: "Editar planificación" });
      if (await iniciar.isVisible()) {
        await expect(editar).toBeVisible();
      }
    } else if (await completar.isVisible()) {
      await expect(page.getByRole("heading", { level: 2, name: "Completar producción" })).toBeVisible();
      await expect(page.getByLabel("Precio venta / unidad")).toBeVisible();
      await expect(page.getByRole("button", { name: "Confirmar completada" })).toBeVisible();
    } else if (await completada.isVisible()) {
      await expect(completada).toBeVisible();
    } else if (await cancelada.isVisible()) {
      await expect(cancelada).toBeVisible();
    }
  });

  test("edición: formulario borrador", async ({ page }) => {
    await page.goto(PRODUCCION_LIST);
    const editLink = page.locator("#tabla-ordenes").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay órdenes en borrador editables");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/produccion\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Editar");
    await expect(page.getByRole("heading", { name: "Planificación" })).toBeVisible();
    await expect(page.getByLabel("Cantidad de lotes")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar cambios" })).toBeVisible();
  });

  test("edición: ayuda contextual", async ({ page }) => {
    await page.goto(PRODUCCION_LIST);
    const editLink = page.locator("#tabla-ordenes").getByRole("link", { name: "Editar" }).first();
    test.skip((await editLink.count()) === 0, "No hay órdenes en borrador para ayuda");

    await editLink.click();
    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/produccion\/\d+\/editar\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: /Ayuda: editar orden/i })).toBeVisible();
    await expect(page.getByRole("link", { name: "← Volver al formulario" })).toBeVisible();
  });
});
