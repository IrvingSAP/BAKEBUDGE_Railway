import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();

test.describe("Ayuda — acceso", () => {
  test("ayuda general redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/ayuda/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Ayuda — Ayuda General (/app/ayuda/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/ayuda/");
  });

  test("cabecera y modo solo lectura", async ({ page }) => {
    await expect(page).toHaveTitle(/Ayuda General/i);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda General" })).toBeVisible();
    await expect(page.getByText("Guía del ciclo completo")).toBeVisible();
    await expect(page.getByText("Solo lectura — sin formularios")).toBeVisible();
  });

  test("panorama: tres fases del ciclo", async ({ page }) => {
    await expect(page.getByRole("heading", { level: 2, name: "Panorama del ciclo" })).toBeVisible();

    const flow = page.getByRole("list", { name: "Fases del ciclo" });
    await expect(flow).toBeVisible();
    await expect(flow.getByRole("listitem")).toHaveCount(3);
    await expect(flow.getByText("Fase 1")).toBeVisible();
    await expect(flow.getByText("Catálogo base")).toBeVisible();
    await expect(flow.getByText("Fase 2")).toBeVisible();
    await expect(flow.getByText("Recetas y producción")).toBeVisible();
    await expect(flow.getByText("Fase 3")).toBeVisible();
    await expect(flow.getByText("Análisis y estadísticas")).toBeVisible();
  });

  test("enlaces saltar a sección y dashboard", async ({ page }) => {
    const intro = page.locator(".ayuda-intro");
    await expect(intro.getByRole("link", { name: "Catálogo base" })).toHaveAttribute(
      "href",
      "#seccion-catalogo"
    );
    await expect(intro.getByRole("link", { name: "Recetas y producción" })).toHaveAttribute(
      "href",
      "#seccion-recetas"
    );
    await expect(intro.getByRole("link", { name: "Análisis" })).toHaveAttribute(
      "href",
      "#seccion-analisis"
    );
    await expect(intro.getByRole("link", { name: "Noticias" })).toHaveAttribute(
      "href",
      "#seccion-noticias"
    );
    await expect(intro.getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      /\/app\/?$/
    );
  });

  test("salto interno: enlace Catálogo base muestra sección 1", async ({ page }) => {
    await page.locator(".ayuda-intro").getByRole("link", { name: "Catálogo base" }).click();
    const section = page.locator("#seccion-catalogo");
    await expect(section).toBeInViewport();
    await expect(section.getByRole("heading", { level: 2, name: "1. Catálogo base" })).toBeVisible();
  });

  test("sección 1 — catálogo base y pasos", async ({ page }) => {
    const section = page.locator("#seccion-catalogo");
    await expect(section.getByText("apps.accounts")).toBeVisible();
    await expect(section.getByText("apps.catalog")).toBeVisible();

    await expect(section.getByRole("heading", { level: 3, name: "Perfil" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Perfil" })).toHaveAttribute(
      "href",
      /\/app\/perfil\/?$/
    );
    await expect(section.getByRole("heading", { level: 3, name: "Categorías de producto" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Categorías" })).toHaveAttribute(
      "href",
      /\/app\/categorias\/?$/
    );
    await expect(section.getByRole("heading", { level: 3, name: "Conversiones de unidad" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Conversiones" })).toHaveAttribute(
      "href",
      /\/app\/conversiones\/?$/
    );
    await expect(section.getByRole("heading", { level: 3, name: "Costos indirectos" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Costos indirectos" })).toHaveAttribute(
      "href",
      /\/app\/costos-indirectos\/?$/
    );
  });

  test("sección 2 — recetas y producción", async ({ page }) => {
    const section = page.locator("#seccion-recetas");
    await expect(section.getByRole("heading", { level: 2, name: "2. Recetas y producción" })).toBeVisible();
    await expect(section.getByRole("heading", { level: 3, name: "Productos (insumos)" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Productos" })).toHaveAttribute(
      "href",
      /\/app\/productos\/?$/
    );
    await expect(section.getByRole("heading", { level: 3, name: "Recetas y versiones" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Recetas" })).toHaveAttribute(
      "href",
      /\/app\/recetas\/?$/
    );
    await expect(section.getByRole("heading", { level: 3, name: "Producción (órdenes)" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Producción" })).toHaveAttribute(
      "href",
      /\/app\/produccion\/?$/
    );
    await expect(section.getByText("Borrador")).toBeVisible();
    await expect(section.getByText("Completada")).toBeVisible();
  });

  test("sección 3 — análisis y estadísticas", async ({ page }) => {
    const section = page.locator("#seccion-analisis");
    await expect(section.getByRole("heading", { level: 2, name: "3. Análisis y estadísticas" })).toBeVisible();
    await expect(section.getByRole("heading", { level: 3, name: "Snapshots al completar" })).toBeVisible();
    await expect(section.getByRole("heading", { level: 3, name: "Pantalla Estadísticas" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Estadísticas" })).toHaveAttribute(
      "href",
      /\/app\/estadisticas\/?$/
    );
    await expect(section.getByRole("heading", { level: 3, name: "Dashboard como resumen" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Dashboard" })).toHaveAttribute(
      "href",
      /\/app\/?$/
    );
  });

  test("sección 4 — noticias", async ({ page }) => {
    const section = page.locator("#seccion-noticias");
    await expect(section.getByRole("heading", { level: 2, name: "4. Noticias" })).toBeVisible();
    await expect(section.getByText("apps.noticias")).toBeVisible();
    await expect(section.getByRole("heading", { level: 3, name: "Feed de noticias" })).toBeVisible();
    await expect(section.getByRole("link", { name: "Ir a Noticias" })).toHaveAttribute(
      "href",
      /\/app\/noticias\/?$/
    );
    await expect(section.getByText("Alcance global")).toBeVisible();
    await expect(section.getByText("Alcance personal")).toBeVisible();
  });

  test("sidebar: enlace Ayuda General", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("link", { name: "Ayuda General" }).click();
    await expect(page).toHaveURL(/\/app\/ayuda\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Ayuda General" })).toBeVisible();
  });
});
