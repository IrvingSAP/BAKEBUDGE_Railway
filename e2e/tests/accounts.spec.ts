import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();

test.describe("Accounts — acceso", () => {
  test("perfil redirige a login si no hay sesión", async ({ page }) => {
    await page.goto("/app/perfil/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
    await expect(page.getByRole("heading", { name: "Ingresar" })).toBeVisible();
  });

  test("seguridad de cuenta redirige a login si no hay sesión", async ({ page }) => {
    await page.goto("/app/seguridad/cuenta/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Accounts — perfil (/app/perfil/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/perfil/");
  });

  test("cabecera y secciones principales", async ({ page }) => {
    await expect(page).toHaveTitle(/Perfil/i);
    await expect(page.getByRole("heading", { level: 1, name: "Perfil" })).toBeVisible();
    await expect(
      page.getByText("Configura tu repostería, moneda, margen objetivo")
    ).toBeVisible();
  });

  test("formulario perfil: datos del negocio", async ({ page }) => {
    const form = page.locator("form.form-perfil");
    await expect(form).toBeVisible();

    const negocio = form.getByRole("heading", { name: "Datos del negocio" });
    await expect(negocio).toBeVisible();
    await expect(form.getByLabel("Nombre de la repostería")).toBeVisible();
    await expect(form.getByLabel("Moneda")).toBeVisible();
    await expect(form.getByLabel("Margen objetivo (%)")).toBeVisible();
    await expect(form.getByText("Usado para precio de venta sugerido en recetas")).toBeVisible();
  });

  test("formulario perfil: unidades por defecto", async ({ page }) => {
    const form = page.locator("form.form-perfil");
    await expect(form.getByRole("heading", { name: "Unidades por defecto" })).toBeVisible();
    await expect(form.getByLabel("Peso")).toBeVisible();
    await expect(form.getByLabel("Volumen")).toBeVisible();
    await expect(form.getByLabel("Conteo")).toBeVisible();
  });

  test("formulario perfil: acción guardar", async ({ page }) => {
    const form = page.locator("form.form-perfil");
    await expect(form.getByRole("button", { name: "Guardar cambios" })).toBeVisible();
  });

  test("bloque cuenta y seguridad enlaza a seguridad de la cuenta", async ({ page }) => {
    const bloque = page.locator("section.card", {
      has: page.getByRole("heading", { name: "Cuenta y seguridad" }),
    });
    await expect(bloque).toBeVisible();
    await expect(bloque.getByText(/Usuario:/)).toBeVisible();
    await expect(bloque.getByText(/Correo:/)).toBeVisible();

    const link = bloque.getByRole("link", { name: "Seguridad de la cuenta" });
    await expect(link).toHaveAttribute("href", /\/app\/seguridad\/cuenta\/?$/);
  });

  test("navegación perfil → seguridad de la cuenta", async ({ page }) => {
    await page.getByRole("link", { name: "Seguridad de la cuenta" }).click();
    await expect(page).toHaveURL(/\/app\/seguridad\/cuenta\/?$/);
    await expect(
      page.getByRole("heading", { level: 1, name: "Seguridad de la cuenta" })
    ).toBeVisible();
  });
});

test.describe("Accounts — seguridad de la cuenta (/app/seguridad/cuenta/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/seguridad/cuenta/");
  });

  test("cabecera y aviso de reinicio 2FA", async ({ page }) => {
    await expect(page).toHaveTitle(/Seguridad de la cuenta/i);
    await expect(
      page.getByRole("heading", { level: 1, name: "Seguridad de la cuenta" })
    ).toBeVisible();
    await expect(
      page.getByText("Cambia tu contraseña y reinicia la verificación de correo y autenticador 2FA.")
    ).toBeVisible();

    const aviso = page.getByRole("note");
    await expect(aviso).toContainText("Perderás el factor TOTP actual");
    await expect(aviso).toContainText("Se cerrará tu sesión actual");
  });

  test("datos de solo lectura del usuario", async ({ page }) => {
    const readonly = page.locator(".cuenta-seguridad-readonly");
    await expect(readonly).toBeVisible();
    await expect(readonly.getByText(/Usuario:/)).toBeVisible();
    await expect(readonly.getByText(/Correo:/)).toBeVisible();
    await expect(readonly.getByText(/Repostería:/)).toBeVisible();
  });

  test("formulario: campos de contraseña y confirmación", async ({ page }) => {
    const form = page.locator(".cuenta-seguridad-form form");
    await expect(form).toBeVisible();
    await expect(form.getByLabel("Contraseña actual")).toBeVisible();
    await expect(form.getByLabel("Nueva contraseña")).toBeVisible();
    await expect(form.getByLabel("Confirmar nueva contraseña")).toBeVisible();
    await expect(form.getByText("Mínimo 8 caracteres")).toBeVisible();

    await expect(
      form.getByRole("checkbox", {
        name: /Entiendo que debo reconfigurar correo y 2FA/,
      })
    ).toBeVisible();
  });

  test("formulario: toggles mostrar contraseña", async ({ page }) => {
    const form = page.locator(".cuenta-seguridad-form form");
    await expect(form.getByRole("button", { name: "Mostrar contraseña" })).toHaveCount(3);
  });

  test("acciones del formulario", async ({ page }) => {
    const form = page.locator(".cuenta-seguridad-form form");
    await expect(
      form.getByRole("button", { name: "Confirmar cambio de seguridad" })
    ).toBeVisible();
    await expect(form.getByRole("link", { name: "Volver al perfil" })).toHaveAttribute(
      "href",
      /\/app\/perfil\/?$/
    );
  });

  test("navegación seguridad → volver al perfil", async ({ page }) => {
    await page.getByRole("link", { name: "Volver al perfil" }).click();
    await expect(page).toHaveURL(/\/app\/perfil\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Perfil" })).toBeVisible();
  });
});
