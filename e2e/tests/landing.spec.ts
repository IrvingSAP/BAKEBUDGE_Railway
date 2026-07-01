import { test, expect } from "@playwright/test";

test.describe("Landing principal — secciones y CTA", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("hero: mensaje principal y CTA solicitar acceso", async ({ page }) => {
    const hero = page.locator("#inicio.hero");
    await expect(hero).toBeVisible();
    await expect(hero.getByText("Repostería con números claros")).toBeVisible();
    await expect(
      hero.getByRole("heading", {
        level: 1,
        name: "Conoce el costo real de cada postre",
      })
    ).toBeVisible();

    const heroCta = hero.getByRole("link", { name: "Solicitar acceso" });
    await expect(heroCta).toBeVisible();
    await expect(heroCta).toHaveAttribute("href", /\/contacto\/?$/);

    await expect(hero.locator(".hero-stat strong", { hasText: "Recetas" })).toBeVisible();
    await expect(hero.locator(".hero-stat strong", { hasText: "Producción" })).toBeVisible();
    await expect(hero.locator(".hero-stat strong", { hasText: "Analytics" })).toBeVisible();
  });

  test("sección servicios: título y tarjetas de capacidades", async ({ page }) => {
    const servicios = page.locator("#servicios");
    await expect(servicios).toBeVisible();
    await expect(
      servicios.getByRole("heading", {
        level: 2,
        name: "Todo lo que necesitas para tu repostería",
      })
    ).toBeVisible();

    const cards = servicios.locator("article.feature-card");
    await expect(cards).toHaveCount(6);
    await expect(servicios.getByRole("heading", { name: "Recetas versionadas" })).toBeVisible();
    await expect(servicios.getByRole("heading", { name: "Acceso seguro" })).toBeVisible();
  });

  test("sección cómo funciona: cuatro pasos", async ({ page }) => {
    await expect(
      page.getByRole("heading", {
        level: 2,
        name: "De la idea al margen en cuatro pasos",
      })
    ).toBeVisible();

    const steps = page.locator(".steps .step");
    await expect(steps).toHaveCount(4);
    await expect(page.getByRole("heading", { name: "Carga tus insumos" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Analiza resultados" })).toBeVisible();
  });

  test("galería inspiración (#recetas)", async ({ page }) => {
    const galeria = page.locator("#recetas");
    await expect(galeria).toBeVisible();
    await expect(
      galeria.getByRole("heading", {
        level: 2,
        name: "Descubre el arte de la repostería",
      })
    ).toBeVisible();
    await expect(galeria.locator(".gallery-grid img")).toHaveCount(3);
  });

  test("CTA final (#contacto): mensaje y acciones", async ({ page }) => {
    const cta = page.locator("#contacto .cta-box");
    await expect(cta).toBeVisible();
    await expect(
      cta.getByRole("heading", {
        level: 2,
        name: "Empieza a costear con claridad hoy",
      })
    ).toBeVisible();

    const solicitar = cta.getByRole("link", { name: "Solicitar acceso" });
    const servicios = cta.getByRole("link", { name: "Conocer servicios" });
    await expect(solicitar).toHaveAttribute("href", /\/contacto\/?$/);
    await expect(servicios).toHaveAttribute("href", /\/servicios\/?$/);
  });

  test("cabecera: navegación y CTA global", async ({ page }) => {
    const header = page.locator("header.site-header");
    await expect(header).toBeVisible();
    await expect(header.getByRole("link", { name: /BAKE.*BUDGE/i })).toBeVisible();
    await expect(header.getByRole("link", { name: "Inicio" })).toBeVisible();
    await expect(header.getByRole("link", { name: "Servicios" })).toBeVisible();
    await expect(header.getByRole("link", { name: "Contacto" })).toBeVisible();
    await expect(header.getByRole("link", { name: "Entrar" })).toHaveAttribute(
      "href",
      /\/ingresar\/?$/
    );
  });

  test("CTA hero navega a página de contacto", async ({ page }) => {
    await page.locator("#inicio").getByRole("link", { name: "Solicitar acceso" }).click();
    await expect(page).toHaveURL(/\/contacto\/?$/);
    await expect(
      page.getByRole("heading", { level: 1, name: "Estamos aquí para ayudarte" })
    ).toBeVisible();
    const form = page.locator(".contact-form");
    await expect(form.getByLabel("Nombre")).toBeVisible();
    await expect(form.getByLabel("Correo")).toBeVisible();
    await expect(form.getByRole("textbox", { name: "Mensaje" })).toBeVisible();
  });
});
