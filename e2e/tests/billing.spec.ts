import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();
const FACTURACION_LIST = "/app/administracion/facturacion/";

test.describe("Billing — acceso", () => {
  test("facturación redirige a login sin sesión", async ({ page }) => {
    await page.goto(FACTURACION_LIST);
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Billing — Facturación (PaymentControl)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("sidebar: enlace Facturación bajo Administración", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("button", { name: "Administración" }).click();
    await page.locator("#nav-administracion").getByRole("link", { name: "Facturación" }).click();
    await expect(page).toHaveURL(new RegExp(`${FACTURACION_LIST.replace(/\//g, "\\/")}?$`));
    await expect(page.getByRole("heading", { level: 1, name: "Facturación" })).toBeVisible();
  });

  test.describe("Listado", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(FACTURACION_LIST);
    });

    test("cabecera, modelo y enlace alta", async ({ page }) => {
      await expect(page).toHaveTitle(/Facturación/i);
      await expect(page.getByRole("heading", { level: 1, name: "Facturación" })).toBeVisible();
      await expect(page.getByText("Suscripciones y pagos")).toBeVisible();
      await expect(page.getByText("billing_paymentcontrol")).toBeVisible();
      await expect(page.getByText("Solo usuarios")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nuevo período" })).toHaveAttribute(
        "href",
        /\/app\/administracion\/facturacion\/nuevo\/?$/
      );
    });

    test("filtros: usuario, estado y modalidad", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar períodos de pago" });
      await expect(filters.getByLabel("Usuario")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByLabel("Modalidad")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const estado = filters.locator("#filter-estado");
      await expect(estado.locator("option").first()).toHaveText("Todos");
      await expect(estado.locator('option[value="Activo"]')).toHaveText("Activo");
      await expect(estado.locator('option[value="Consumido"]')).toHaveText("Consumido");

      const modalidad = filters.locator("#filter-modalidad");
      await expect(modalidad.locator("option").first()).toHaveText("Todas");
      await expect(modalidad.locator('option[value="Mensual"]')).toHaveText("Mensual");
      await expect(modalidad.locator('option[value="Anual"]')).toHaveText("Anual");
    });

    test("tabla: columnas de PaymentControl", async ({ page }) => {
      const table = page.locator("#tabla-facturacion");
      await expect(table).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Usuario" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Modalidad" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Inicio" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Fin" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Monto" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Método" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Fecha pago" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });

    test("limpiar filtros vacía los campos", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar períodos de pago" });
      await filters.getByLabel("Usuario").fill("demo");
      await filters.locator("#filter-estado").selectOption("Activo");
      await filters.locator("#filter-modalidad").selectOption("Mensual");
      await filters.getByRole("button", { name: "Limpiar filtros" }).click();

      await expect(filters.getByLabel("Usuario")).toHaveValue("");
      await expect(filters.locator("#filter-estado")).toHaveValue("");
      await expect(filters.locator("#filter-modalidad")).toHaveValue("");
    });

    test("query ?owner= prellena filtro usuario", async ({ page }) => {
      const table = page.locator("#tabla-facturacion tbody tr");
      const rowCount = await table.count();
      test.skip(rowCount === 0, "No hay períodos en la tabla para probar ?owner=");

      const username = (await table.first().locator("td").first().innerText()).trim();
      await page.goto(`${FACTURACION_LIST}?owner=${encodeURIComponent(username)}`);

      const filters = page.getByRole("search", { name: "Filtrar períodos de pago" });
      await expect(filters.getByLabel("Usuario")).toHaveValue(username);
    });
  });

  test.describe("Alta", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${FACTURACION_LIST}nuevo/`);
    });

    test("formulario nuevo período: secciones y campos", async ({ page }) => {
      await expect(page).toHaveTitle(/Nuevo período/i);
      await expect(page.getByRole("heading", { level: 1, name: "Nuevo período de pago" })).toBeVisible();
      await expect(page.getByText("billing_paymentcontrol")).toBeVisible();

      const form = page.locator("form.facturacion-form");
      await expect(form.getByRole("heading", { name: "Usuario y modalidad" })).toBeVisible();
      await expect(form.getByLabel("Usuario (owner) *")).toBeVisible();
      await expect(form.getByLabel("Modalidad *")).toBeVisible();
      await expect(form.getByLabel("Estado *")).toBeVisible();

      await expect(form.getByRole("heading", { name: "Período" })).toBeVisible();
      await expect(form.getByLabel("Fecha inicio")).toBeVisible();
      await expect(form.getByLabel("Fecha fin")).toBeVisible();
      await expect(form.getByLabel("Plazo de gracia (días)")).toBeVisible();

      await expect(form.getByRole("heading", { name: "Pago" })).toBeVisible();
      await expect(form.getByLabel("Fecha de pago")).toBeVisible();
      await expect(form.getByLabel("Método de pago")).toBeVisible();
      await expect(form.getByLabel("Monto")).toBeVisible();
      await expect(form.getByLabel("Moneda")).toBeVisible();
      await expect(form.getByLabel("Comprobante / referencia")).toBeVisible();
      await expect(form.getByLabel("Otros datos")).toBeVisible();

      await expect(page.getByRole("button", { name: "Guardar período" })).toBeVisible();
      await expect(page.getByRole("button", { name: "Guardar y activar" })).toBeVisible();
      await expect(page.getByRole("link", { name: "Cancelar" })).toBeVisible();
      await expect(page.getByRole("link", { name: "← Volver al listado" })).toHaveAttribute(
        "href",
        /\/app\/administracion\/facturacion\/?$/
      );
    });

    test("ayuda en la misma pestaña", async ({ page }) => {
      await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
      await expect(page).toHaveURL(/\/app\/administracion\/facturacion\/nuevo\/ayuda\/?$/);
      await expect(page.getByRole("heading", { level: 1, name: "Ayuda: crear período de pago" })).toBeVisible();
      await expect(page.getByText("PaymentControl")).toBeVisible();
      await expect(page.getByRole("link", { name: "← Volver al formulario" })).toHaveAttribute(
        "href",
        /\/app\/administracion\/facturacion\/nuevo\/?$/
      );
    });
  });

  test("edición: formulario desde fila del listado", async ({ page }) => {
    await page.goto(FACTURACION_LIST);
    const table = page.locator("#tabla-facturacion");
    const editLink = table.getByRole("link", { name: /^(Editar|Ver)$/ }).first();
    test.skip((await editLink.count()) === 0, "No hay períodos para editar");

    await editLink.click();
    await expect(page).toHaveURL(/\/app\/administracion\/facturacion\/\d+\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: /período de pago/i })).toBeVisible();

    const form = page.locator("form.facturacion-form");
    await expect(form.getByRole("heading", { name: "Identificación" })).toBeVisible();
    await expect(form.getByLabel("ID")).toBeVisible();
    await expect(form.getByLabel("Usuario (owner)")).toBeVisible();
    await expect(form.getByLabel("Creado")).toBeVisible();
    await expect(form.getByLabel("Actualizado")).toBeVisible();
    await expect(form.getByRole("heading", { name: "Período y estado" })).toBeVisible();
    await expect(form.getByLabel("Modalidad *")).toBeVisible();
    await expect(form.getByLabel("Estado *")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar cambios" })).toBeVisible();
  });

  test("edición: ayuda contextual", async ({ page }) => {
    await page.goto(FACTURACION_LIST);
    const editLink = page
      .locator("#tabla-facturacion")
      .getByRole("link", { name: /^(Editar|Ver)$/ })
      .first();
    test.skip((await editLink.count()) === 0, "No hay períodos para ayuda de edición");

    await editLink.click();
    await page.locator(".page-header-actions").getByRole("link", { name: "Ayuda" }).click();
    await expect(page).toHaveURL(/\/app\/administracion\/facturacion\/\d+\/editar\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda: editar período de pago" })).toBeVisible();
    await expect(page.getByRole("link", { name: "← Volver al formulario" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Ir al listado" })).toHaveAttribute(
      "href",
      /\/app\/administracion\/facturacion\/?$/
    );
  });

  test("acción: suspender o cancelar período", async ({ page }) => {
    await page.goto(FACTURACION_LIST);
    const table = page.locator("#tabla-facturacion");
    const accionLink = table.getByRole("link", { name: /^(Suspender|Cancelar)$/ }).first();
    test.skip((await accionLink.count()) === 0, "No hay períodos activos o pendientes con acción");

    const accion = (await accionLink.innerText()).trim();
    await accionLink.click();
    await expect(page).toHaveURL(/\/app\/administracion\/facturacion\/\d+\/accion\/?$/);

    if (accion === "Suspender") {
      await expect(page.getByRole("heading", { level: 1, name: "Suspender período activo" })).toBeVisible();
      await expect(page.getByRole("button", { name: "Confirmar suspensión" })).toBeVisible();
    } else {
      await expect(page.getByRole("heading", { level: 1, name: "Cancelar período pendiente" })).toBeVisible();
      await expect(page.getByRole("button", { name: "Confirmar cancelación" })).toBeVisible();
    }

    await expect(page.getByText("estado → suspendido")).toBeVisible();
    await expect(page.getByRole("link", { name: "← Cancelar" })).toHaveAttribute(
      "href",
      /\/app\/administracion\/facturacion\/?$/
    );
  });
});
