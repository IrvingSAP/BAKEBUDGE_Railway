import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();
const MONEDAS_LIST = "/app/administracion/monedas/";

test.describe("Core — acceso layout /app/", () => {
  test("dashboard redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Core — layout app_base", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/");
  });

  test("shell: sidebar, topbar y modal global en DOM", async ({ page }) => {
    await expect(page.locator(".app-sidebar")).toBeVisible();
    await expect(page.locator(".app-topbar")).toBeVisible();
    await expect(page.locator(".sidebar-toggle")).toBeVisible();
    await expect(page.locator(".app-topbar-brand")).toContainText("BAKE");
    await expect(page.locator(".app-user-name")).toBeVisible();

    const modal = page.locator("#bbModal");
    await expect(modal).toBeAttached();
    await expect(modal).toHaveAttribute("aria-hidden", "true");
    await expect(modal).toHaveAttribute("role", "dialog");
  });

  test("data-page en body según pantalla", async ({ page }) => {
    await expect(page.locator("body")).toHaveAttribute("data-page", "dashboard");

    await page.goto("/app/perfil/");
    await expect(page.locator("body")).toHaveAttribute("data-page", "perfil");
  });

  test("sidebar: marca y cierre de sesión", async ({ page }) => {
    await expect(page.locator(".app-sidebar .app-brand")).toContainText("BAKEBUDGE");
    await expect(page.getByRole("button", { name: "Cerrar sesión" })).toBeVisible();
  });

  test("sidebar toggle abre menú en viewport móvil", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator(".sidebar-toggle").click();
    await expect(page.locator(".app-sidebar")).toHaveClass(/is-open/);
  });
});

test.describe("Core — modal global (BakeBudgeModal)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/");
    await page.waitForFunction(() => typeof window.BakeBudgeModal !== "undefined");
  });

  test("showError abre modal de validación", async ({ page }) => {
    await page.evaluate(() => {
      window.BakeBudgeModal.showError("E2E — error de prueba");
    });

    const modal = page.locator("#bbModal");
    await expect(modal).toHaveClass(/is-open/);
    await expect(modal).toHaveAttribute("aria-hidden", "false");
    await expect(page.locator("#bbModalTitle")).toHaveText("Error de validación");
    await expect(page.locator("#bbModalBody")).toContainText("E2E — error de prueba");
    await expect(page.locator("#bbModalBtn")).toHaveText("Cerrar");
  });

  test("showSuccess usa título y botón de éxito", async ({ page }) => {
    await page.evaluate(() => {
      window.BakeBudgeModal.showSuccess("E2E — operación OK");
    });

    await expect(page.locator("#bbModalTitle")).toHaveText("Operación exitosa");
    await expect(page.locator("#bbModalBody")).toContainText("E2E — operación OK");
    await expect(page.locator("#bbModalBtn")).toHaveText("Aceptar");
  });

  test("cerrar con botón y con Escape", async ({ page }) => {
    await page.evaluate(() => {
      window.BakeBudgeModal.showInfo("E2E — info");
    });
    await expect(page.locator("#bbModal")).toHaveClass(/is-open/);

    await page.locator("#bbModalBtn").click();
    await expect(page.locator("#bbModal")).not.toHaveClass(/is-open/);

    await page.evaluate(() => {
      window.BakeBudgeModal.showWarning("E2E — aviso");
    });
    await expect(page.locator("#bbModal")).toHaveClass(/is-open/);
    await page.keyboard.press("Escape");
    await expect(page.locator("#bbModal")).not.toHaveClass(/is-open/);
  });
});

test.describe("Core — validación cliente (BakeBudgeFormErrors)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto(`${MONEDAS_LIST}nuevo/`);
    await page.waitForFunction(() => typeof window.BakeBudgeFormErrors !== "undefined");
  });

  test("apply marca campos inválidos y mensaje de error", async ({ page }) => {
    await page.evaluate(() => {
      const form = document.querySelector("[data-bb-validate-form]");
      window.BakeBudgeFormErrors.apply(form, { codigo: "El código es obligatorio." });
    });

    const field = page.locator(".form-field", { has: page.locator("#codigo") });
    await expect(field).toHaveClass(/form-field--invalid/);
    await expect(page.locator("#codigo")).toHaveAttribute("aria-invalid", "true");
    await expect(page.locator("#codigo-error")).toContainText("El código es obligatorio.");
  });
});

test.describe("Core — password toggle", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/seguridad/cuenta/");
  });

  test("mostrar y ocultar contraseña", async ({ page }) => {
    const field = page.locator(".password-field").first();
    const input = field.locator(".password-field__input");
    const toggle = field.getByRole("button", { name: "Mostrar contraseña" });

    await input.fill("clave-secreta-e2e");
    await expect(input).toHaveAttribute("type", "password");

    await toggle.click();
    await expect(input).toHaveAttribute("type", "text");
    await expect(field.getByRole("button", { name: "Ocultar contraseña" })).toBeVisible();

    await field.getByRole("button", { name: "Ocultar contraseña" }).click();
    await expect(input).toHaveAttribute("type", "password");
  });
});

test.describe("Core — Moneda (core_moneda)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("perfil: selector Moneda con monedas seed", async ({ page }) => {
    await page.goto("/app/perfil/");
    const moneda = page.locator("form.form-perfil").getByLabel("Moneda");
    await expect(moneda).toBeVisible();
    await expect(moneda.locator("option")).toContainText("COP");
    await expect(moneda.locator("option")).toContainText("USD");
  });

  test.describe("Administración — listado", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(MONEDAS_LIST);
    });

    test("cabecera, core_moneda y enlace alta", async ({ page }) => {
      await expect(page).toHaveTitle(/Monedas/i);
      await expect(page.getByRole("heading", { level: 1, name: "Monedas" })).toBeVisible();
      await expect(page.getByText("Catálogo global de monedas")).toBeVisible();
      await expect(page.getByRole("link", { name: "+ Nueva moneda" })).toHaveAttribute(
        "href",
        /\/app\/administracion\/monedas\/nuevo\/?$/
      );
    });

    test("filtros y tabla", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar monedas" });
      await expect(filters.getByLabel("Nombre")).toBeVisible();
      await expect(filters.getByLabel("Estado")).toBeVisible();
      await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

      const table = page.locator("#tabla-monedas");
      await expect(table.getByRole("columnheader", { name: "Código" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Nombre" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Símbolo" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Decimales" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Orden" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Perfiles" })).toBeVisible();
      await expect(table.getByRole("columnheader", { name: "Acciones" })).toBeVisible();
      await expect(table.locator("tbody")).toContainText("COP");
    });

    test("limpiar filtros vacía los campos", async ({ page }) => {
      const filters = page.getByRole("search", { name: "Filtrar monedas" });
      await filters.getByLabel("Nombre").fill("colombiano");
      await filters.locator("#filter-activa").selectOption("Activa");
      await filters.getByRole("button", { name: "Limpiar filtros" }).click();
      await expect(filters.getByLabel("Nombre")).toHaveValue("");
      await expect(filters.locator("#filter-activa")).toHaveValue("");
    });
  });

  test("alta: formulario referencia core_moneda", async ({ page }) => {
    await page.goto(`${MONEDAS_LIST}nuevo/`);
    await expect(page.getByRole("heading", { level: 1, name: "Nueva moneda" })).toBeVisible();
    await expect(page.getByText("core_moneda")).toBeVisible();

    const form = page.locator("form[data-bb-validate-form]");
    await expect(form.getByRole("heading", { name: "Datos de moneda" })).toBeVisible();
    await expect(form.getByLabel("Código ISO *")).toBeVisible();
    await expect(form.getByLabel("Nombre *")).toBeVisible();
    await expect(form.getByLabel("Símbolo *")).toBeVisible();
    await expect(form.getByLabel("Decimales *")).toBeVisible();
    await expect(form.getByLabel("Orden *")).toBeVisible();
    await expect(form.getByLabel("Moneda activa (visible en selectores de perfil)")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar moneda" })).toBeVisible();
  });

  test("edición: moneda seed COP", async ({ page }) => {
    await page.goto(`${MONEDAS_LIST}COP/editar/`);
    await expect(page).toHaveURL(/\/app\/administracion\/monedas\/COP\/editar\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Editar moneda" })).toBeVisible();
    await expect(page.locator("#codigo")).toHaveValue("COP");
    await expect(page.getByRole("button", { name: "Guardar cambios" })).toBeVisible();
  });

  test("eliminar: pantalla de confirmación COP", async ({ page }) => {
    await page.goto(`${MONEDAS_LIST}COP/eliminar/`);
    await expect(page.getByRole("heading", { level: 1, name: "Eliminar moneda" })).toBeVisible();
    await expect(page.getByText("COP")).toBeVisible();
    await expect(page.getByText("Perfiles que usan esta moneda")).toBeVisible();
    await expect(page.getByRole("link", { name: "Cancelar" })).toHaveAttribute(
      "href",
      /\/app\/administracion\/monedas\/?$/
    );
  });
});
