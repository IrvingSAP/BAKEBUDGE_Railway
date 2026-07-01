import { test, expect } from "@playwright/test";

test.describe("Public site — layout compartido", () => {
  test("footer: navegación y copyright", async ({ page }) => {
    await page.goto("/servicios/");
    const footer = page.locator("footer.site-footer");
    await expect(footer).toBeVisible();
    await expect(footer.getByRole("link", { name: "Inicio" })).toHaveAttribute("href", /\/$/);
    await expect(footer.getByRole("link", { name: "Servicios" })).toHaveAttribute(
      "href",
      /\/servicios\/?$/
    );
    await expect(footer.getByRole("link", { name: "Contacto" })).toHaveAttribute(
      "href",
      /\/contacto\/?$/
    );
    await expect(footer.getByText("© 2026 BAKEBUDGE")).toBeVisible();
  });

  test("modal global presente en zona pública", async ({ page }) => {
    await page.goto("/contacto/");
    const modal = page.locator("#bbModal");
    await expect(modal).toBeAttached();
    await expect(modal).toHaveAttribute("aria-hidden", "true");
  });

  test("menú móvil: toggle abre navegación", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    await page.getByRole("button", { name: "Menú" }).click();
    await expect(page.locator("[data-site-nav]")).toHaveClass(/is-open/);
  });
});

test.describe("Public site — home (/)", () => {
  test("data-page inicio", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("body")).toHaveAttribute("data-page", "inicio");
  });
});

test.describe("Public site — servicios (/servicios/)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/servicios/");
  });

  test("cabecera y descripción", async ({ page }) => {
    await expect(page).toHaveTitle(/Servicios/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "servicios");
    await expect(page.getByRole("heading", { level: 1, name: "Gestión integral para tu repostería" })).toBeVisible();
    await expect(page.getByText("BAKEBUDGE está diseñada")).toBeVisible();
    await expect(page.locator('[data-nav="servicios"]')).toHaveClass(/active/);
  });

  test("tarjetas de capacidades", async ({ page }) => {
    const grid = page.locator(".features-grid");
    await expect(grid.locator("article.feature-card")).toHaveCount(6);
    await expect(page.getByRole("heading", { name: "Recetas personalizadas" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Cálculo automático de costos" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Catálogo de insumos" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Análisis de rentabilidad" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Planificación de producción" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Dashboard analítico" })).toBeVisible();
  });

  test("CTA inferior: solicitar acceso y contactar", async ({ page }) => {
    const cta = page.locator(".cta-box").last();
    await expect(cta.getByRole("heading", { name: "¿Listo para transformar tu cocina?" })).toBeVisible();
    await expect(cta.getByRole("link", { name: "Solicitar acceso" })).toHaveAttribute(
      "href",
      /\/contacto\/?$/
    );
    await expect(cta.getByRole("link", { name: "Contactar" })).toHaveAttribute(
      "href",
      /\/contacto\/?$/
    );
  });
});

test.describe("Public site — contacto (/contacto/)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/contacto/");
  });

  test("cabecera e información de contacto", async ({ page }) => {
    await expect(page).toHaveTitle(/Contacto/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "contacto");
    await expect(page.getByRole("heading", { level: 1, name: "Estamos aquí para ayudarte" })).toBeVisible();
    await expect(page.locator('[data-nav="contacto"]')).toHaveClass(/active/);

    const info = page.locator(".contact-card").first();
    await expect(info.getByRole("heading", { name: "Hablemos" })).toBeVisible();
    await expect(info.getByRole("link", { name: "bakebudg@gmail.com" })).toHaveAttribute(
      "href",
      "mailto:bakebudg@gmail.com"
    );
    await expect(info.getByText("Respuesta en 24–48 h hábiles")).toBeVisible();
  });

  test("formulario: campos y envío", async ({ page }) => {
    const card = page.locator(".contact-form");
    await expect(card.getByRole("heading", { name: "Envíanos un mensaje" })).toBeVisible();

    const form = card.locator("form");
    await expect(form.getByLabel("Nombre")).toBeVisible();
    await expect(form.getByLabel("Correo")).toBeVisible();
    await expect(form.getByRole("textbox", { name: "Mensaje" })).toBeVisible();
    await expect(form.getByRole("button", { name: "Enviar mensaje" })).toBeVisible();
  });

  test("validación: mensaje corto muestra modal de error", async ({ page }) => {
    const form = page.locator(".contact-form form");
    await form.getByLabel("Nombre").fill("Prueba E2E");
    await form.getByLabel("Correo").fill("e2e-public@example.com");
    await form.getByRole("textbox", { name: "Mensaje" }).fill("corto");
    await form.getByRole("button", { name: "Enviar mensaje" }).click();

    await expect(page.locator("#bbModal")).toHaveClass(/is-open/);
    await expect(page.locator("#bbModalBody")).toContainText("10 caracteres");
  });

  test("envío válido muestra modal de éxito", async ({ page }) => {
    const form = page.locator(".contact-form form");
    await form.getByLabel("Nombre").fill("Prueba E2E Public Site");
    await form.getByLabel("Correo").fill(`e2e+${Date.now()}@example.com`);
    await form.getByRole("textbox", { name: "Mensaje" }).fill(
      "Mensaje de prueba E2E desde Playwright para validar el formulario público."
    );
    await form.getByRole("button", { name: "Enviar mensaje" }).click();

    await expect(page).toHaveURL(/\/contacto\/?$/);
    await expect(page.locator("#bbModal")).toHaveClass(/is-open/);
    await expect(page.locator("#bbModalBody")).toContainText("Recibimos tu mensaje");
  });
});

test.describe("Public site — navegación entre páginas", () => {
  test("cabecera: Servicios e Inicio", async ({ page }) => {
    await page.goto("/contacto/");
    await page.locator("header.site-header").getByRole("link", { name: "Servicios" }).click();
    await expect(page).toHaveURL(/\/servicios\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Gestión integral para tu repostería" })).toBeVisible();

    await page.locator("header.site-header").getByRole("link", { name: "Inicio" }).click();
    await expect(page).toHaveURL(/\/$/);
    await expect(page.locator("#inicio.hero")).toBeVisible();
  });

  test("cabecera: Entrar lleva a ingreso", async ({ page }) => {
    await page.goto("/");
    await page.locator("header.site-header").getByRole("link", { name: "Entrar" }).click();
    await expect(page).toHaveURL(/\/ingresar\/?$/);
  });
});
