import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();

test.describe("Administration — acceso", () => {
  test("usuarios redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/administracion/usuarios/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Administration — Master", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("sidebar: grupo Administración y enlaces", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("button", { name: "Administración" }).click();
    const sub = page.locator("#nav-administracion");
    await expect(sub.getByRole("link", { name: "Monedas" })).toBeVisible();
    await expect(sub.getByRole("link", { name: "Usuarios" })).toBeVisible();
    await expect(sub.getByRole("link", { name: "Facturación" })).toBeVisible();
    await expect(sub.getByRole("link", { name: "Gestión noticias" })).toBeVisible();
    await expect(sub.getByRole("link", { name: "Mensajes contacto" })).toBeVisible();
  });

  test.describe("Monedas", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/administracion/monedas/");
    });

    test("listado: cabecera, filtros y tabla", async ({ page }) => {
      await expect(page).toHaveTitle(/Monedas/i);
      await expect(page.getByRole("heading", { level: 1, name: "Monedas" })).toBeVisible();
      await expect(page.getByText("Catálogo global de monedas")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nueva moneda" })).toHaveAttribute(
        "href",
        /\/app\/administracion\/monedas\/nuevo\/?$/
      );

      const filters = page.getByRole("search", { name: "Filtrar monedas" });
      await expect(filters.getByLabel("Nombre")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const table = page.locator("#tabla-monedas");
      await expect(table).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Código" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });

    test("alta: formulario nueva moneda", async ({ page }) => {
      await page.getByRole("link", { name: "+ Nueva moneda" }).click();
      await expect(page).toHaveURL(/\/app\/administracion\/monedas\/nuevo\/?$/);
      await expect(page.getByRole("heading", { level: 1, name: "Nueva moneda" })).toBeVisible();

      const form = page.locator("form[data-bb-validate-form]");
      await expect(form.getByLabel("Código ISO *")).toBeVisible();
      await expect(form.getByLabel("Nombre *")).toBeVisible();
      await expect(form.getByLabel("Símbolo *")).toBeVisible();
      await expect(form.getByLabel("Decimales *")).toBeVisible();
      await expect(page.getByRole("link", { name: "Volver al listado" })).toBeVisible();
    });
  });

  test.describe("Usuarios", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/administracion/usuarios/");
    });

    test("listado: cabecera, filtros y tabla", async ({ page }) => {
      await expect(page).toHaveTitle(/Usuarios/i);
      await expect(page.getByRole("heading", { level: 1, name: "Usuarios" })).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nuevo usuario" })).toHaveAttribute(
        "href",
        /\/app\/administracion\/usuarios\/nuevo\/?$/
      );

      const filters = page.getByRole("search", { name: "Filtrar usuarios" });
      await expect(filters.getByLabel("Usuario")).toBeVisible();
      await expect(filters.getByLabel("Tipo")).toBeVisible();
      await expect(filters.getByLabel("Estado cuenta")).toBeVisible();

      const table = page.locator("#tabla-usuarios");
      await expect(table.getByRole("columnheader", { name: "Negocio" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });

    test("alta: formulario y ayuda en la misma pestaña", async ({ page }) => {
      await page.getByRole("link", { name: "+ Nuevo usuario" }).click();
      await expect(page.getByRole("heading", { level: 1, name: "Nuevo usuario" })).toBeVisible();

      const form = page.locator("form.usuarios-form");
      await expect(form.getByLabel("Usuario *")).toBeVisible();
      await expect(form.getByLabel("Correo *")).toBeVisible();
      await expect(form.getByLabel("Contraseña *")).toBeVisible();
      await expect(form.getByLabel("Confirmar contraseña *")).toBeVisible();
      await expect(form.getByLabel("Tipo de usuario *")).toBeVisible();
      await expect(form.getByLabel("Moneda *")).toBeVisible();
      await expect(form.getByRole("heading", { name: "Perfil (UserProfile)" })).toBeVisible();

      await page.getByRole("link", { name: "Ayuda" }).click();
      await expect(page).toHaveURL(/\/app\/administracion\/usuarios\/nuevo\/ayuda\/?$/);
      await expect(page.getByRole("heading", { name: "Ayuda: crear usuario" })).toBeVisible();
      await expect(page.getByRole("link", { name: /Volver al formulario/i }).first()).toBeVisible();
    });

    test("alta User: redirige a facturación con owner preseleccionado", async ({ page }) => {
      const suffix = Date.now();
      const username = `e2e.user.${suffix}`;

      await page.getByRole("link", { name: "+ Nuevo usuario" }).click();
      await page.getByLabel("Usuario *").fill(username);
      await page.getByLabel("Correo *").fill(`${username}@example.com`);
      await page.getByLabel("Contraseña *").fill("E2eTestPass123!");
      await page.getByLabel("Confirmar contraseña *").fill("E2eTestPass123!");
      await page.getByLabel("Nombre del negocio").fill("E2E Repostería");
      await page.getByLabel("Tipo de usuario *").selectOption("U");

      await page.getByRole("button", { name: "Guardar usuario" }).click();

      await expect(page).toHaveURL(/\/app\/administracion\/facturacion\/nuevo\/\?owner=\d+$/);
      await expect(page.getByRole("heading", { level: 1, name: "Nuevo período de pago" })).toBeVisible();
      await expect(page.getByText(/recién creado/i)).toBeVisible();
      await expect(page.locator("#owner_display")).toHaveValue(new RegExp(`${username} — E2E Repostería`));
    });
  });

  test.describe("Facturación", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/administracion/facturacion/");
    });

    test("listado: cabecera, filtros y tabla", async ({ page }) => {
      await expect(page).toHaveTitle(/Facturación/i);
      await expect(page.getByRole("heading", { level: 1, name: "Facturación" })).toBeVisible();
      await expect(page.getByText("billing_paymentcontrol")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nuevo período" })).toBeVisible();

      const filters = page.getByRole("search", { name: "Filtrar períodos de pago" });
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByLabel("Modalidad")).toBeVisible();

      const table = page.locator("#tabla-facturacion");
      await expect(table.getByRole("columnheader", { name: "Usuario" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Monto" })).toBeVisible();
    });

    test("alta: formulario nuevo período", async ({ page }) => {
      await page.getByRole("link", { name: "+ Nuevo período" }).click();
      await expect(page.getByRole("heading", { level: 1, name: "Nuevo período de pago" })).toBeVisible();

      const form = page.locator("form.facturacion-form");
      await expect(form.getByLabel("Usuario (owner) *")).toBeVisible();
      await expect(form.getByLabel("Modalidad *")).toBeVisible();
      await expect(form.getByLabel("Estado *")).toBeVisible();
      await expect(form.getByRole("heading", { name: "Período" })).toBeVisible();
      await expect(form.getByLabel("Fecha inicio")).toBeVisible();
      await expect(form.getByRole("heading", { name: "Pago" })).toBeVisible();
      await expect(page.getByRole("link", { name: "Ayuda" })).toBeVisible();
    });
  });

  test.describe("Gestión noticias", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/administracion/noticias/");
    });

    test("listado: cabecera, filtros y tabla", async ({ page }) => {
      await expect(page).toHaveTitle(/Gestión noticias/i);
      await expect(page.getByRole("heading", { level: 1, name: "Gestión noticias" })).toBeVisible();
      await expect(page.getByRole("link", { name: "Noticias" })).toHaveAttribute(
        "href",
        /\/app\/noticias\/?$/
      );
      await expect(page.getByRole("link", { name: "+ Nueva noticia" })).toBeVisible();

      const filters = page.getByRole("search", { name: "Filtrar noticias" });
      await expect(filters.getByLabel("Título")).toBeVisible();
      await expect(filters.getByLabel("Alcance")).toBeVisible();

      const table = page.locator("#tabla-noticias");
      await expect(table.getByRole("columnheader", { name: "Título" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });

    test("alta: formulario nueva noticia", async ({ page }) => {
      await page.getByRole("link", { name: "+ Nueva noticia" }).click();
      await expect(page.getByRole("heading", { level: 1, name: "Nueva noticia" })).toBeVisible();

      const form = page.locator("form.noticias-form");
      await expect(form.getByRole("heading", { name: "Alcance y tipo" })).toBeVisible();
      await expect(form.getByLabel("Tipo *")).toBeVisible();
      await expect(form.getByLabel("Estado *")).toBeVisible();
      await expect(form.getByLabel("Título *")).toBeVisible();
      await expect(form.getByRole("radio", { name: /Global \(todos\)/ })).toBeVisible();
      await expect(page.getByRole("link", { name: /Volver al listado/i })).toBeVisible();
    });
  });

  test.describe("Mensajes contacto", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/app/administracion/mensajes-contacto/");
    });

    test("listado: cabecera, filtros y tabla", async ({ page }) => {
      await expect(page).toHaveTitle(/Mensajes contacto/i);
      await expect(page.getByRole("heading", { level: 1, name: "Mensajes contacto" })).toBeVisible();
      await expect(page.getByRole("link", { name: "/contacto/" })).toHaveAttribute(
        "href",
        /\/contacto\/?$/
      );

      const filters = page.getByRole("search", { name: "Filtrar mensajes de contacto" });
      await expect(filters.getByLabel("Nombre")).toBeVisible();
      await expect(filters.getByLabel("Correo")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();

      const table = page.locator("#tabla-mensajecontacto");
      await expect(table.getByRole("columnheader", { name: "Fecha" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
    });
  });
});
