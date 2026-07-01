import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();
const NOTICIAS_FEED = "/app/noticias/";

test.describe("Noticias — acceso", () => {
  test("feed redirige a login sin sesión", async ({ page }) => {
    await page.goto(NOTICIAS_FEED);
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });

  test("detalle redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/noticias/1/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Noticias — feed (/app/noticias/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto(NOTICIAS_FEED);
  });

  test("cabecera y lista de noticias", async ({ page }) => {
    await expect(page).toHaveTitle(/Noticias/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "noticias");
    await expect(page.getByRole("heading", { level: 1, name: "Noticias" })).toBeVisible();
    await expect(page.getByText("Novedades del sistema")).toBeVisible();
    await expect(page.locator(".news-list")).toBeVisible();
  });

  test("estado vacío o tarjetas de noticia", async ({ page }) => {
    const list = page.locator(".news-list");
    const empty = list.locator(".news-empty");
    const cards = list.locator("article.news-card");

    if (await empty.isVisible()) {
      await expect(empty).toHaveText("No hay noticias visibles para tu cuenta en este momento.");
    } else {
      await expect(cards.first()).toBeVisible();
      await expect(cards.first().locator("h2")).toBeVisible();
      await expect(cards.first().locator(".news-meta time")).toBeVisible();
      await expect(cards.first().locator(".badge").first()).toBeVisible();
    }
  });

  test("tarjeta con detalle: enlace Leer más", async ({ page }) => {
    const leerMas = page.getByRole("link", { name: "Leer más →" }).first();
    test.skip((await leerMas.count()) === 0, "No hay noticias con detalle en el feed");

    const href = await leerMas.getAttribute("href");
    expect(href).toMatch(/\/app\/noticias\/\d+\/?$/);

    await leerMas.click();
    await expect(page).toHaveURL(/\/app\/noticias\/\d+\/?$/);
    await expect(page.locator(".news-detail-body")).toBeVisible();
  });

  test("sidebar: enlace Noticias", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("link", { name: "Noticias", exact: true }).click();
    await expect(page).toHaveURL(/\/app\/noticias\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Noticias" })).toBeVisible();
  });
});

test.describe("Noticias — detalle (/app/noticias/<id>/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("404 si la noticia no existe o no es visible", async ({ page }) => {
    const response = await page.goto("/app/noticias/999999999/");
    expect(response?.status()).toBe(404);
  });

  test("detalle: cabecera, cuerpo y volver al feed", async ({ page }) => {
    await page.goto(NOTICIAS_FEED);
    const leerMas = page.getByRole("link", { name: "Leer más →" }).first();
    test.skip((await leerMas.count()) === 0, "No hay noticias con detalle para abrir");

    const card = page.locator("article.news-card").filter({
      has: page.getByRole("link", { name: "Leer más →" }),
    }).first();
    const titulo = (await card.locator("h2").innerText()).trim();

    await card.getByRole("link", { name: "Leer más →" }).click();
    await expect(page.getByRole("heading", { level: 1, name: titulo })).toBeVisible();
    await expect(page.getByText("Detalle de la noticia del sistema")).toBeVisible();
    await expect(page.locator("article.news-detail")).toBeVisible();
    await expect(page.locator(".news-detail-body")).not.toBeEmpty();
    await expect(page.locator(".news-meta time")).toBeVisible();

    await page.getByRole("link", { name: "← Volver a noticias" }).click();
    await expect(page).toHaveURL(/\/app\/noticias\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Noticias" })).toBeVisible();
  });

  test("detalle: enlaces interno o externo si existen", async ({ page }) => {
    await page.goto(NOTICIAS_FEED);
    const leerMas = page.getByRole("link", { name: "Leer más →" }).first();
    test.skip((await leerMas.count()) === 0, "No hay noticias con detalle");

    await leerMas.click();
    const links = page.locator(".news-detail-links");
    if (await links.isVisible()) {
      const interno = links.getByRole("link", { name: "Ir al módulo →" });
      const externo = links.getByRole("link", { name: "Abrir enlace externo →" });
      if (await interno.isVisible()) {
        await expect(interno).toHaveAttribute("href", /.+/);
      }
      if (await externo.isVisible()) {
        await expect(externo).toHaveAttribute("href", /^https?:\/\//);
        await expect(externo).toHaveAttribute("target", "_blank");
        await expect(externo).toHaveAttribute("rel", /noopener/);
      }
    }
  });
});

test.describe("Noticias — feed sin detalle", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto(NOTICIAS_FEED);
  });

  test("enlace externo en tarjeta sin detalle", async ({ page }) => {
    const externo = page.locator(".news-list").getByRole("link", { name: "Abrir enlace →" }).first();
    test.skip((await externo.count()) === 0, "No hay noticias con enlace externo sin detalle");

    await expect(externo).toHaveAttribute("href", /^https?:\/\//);
    await expect(externo).toHaveAttribute("target", "_blank");
  });

  test("enlace interno en tarjeta sin detalle", async ({ page }) => {
    const verMas = page.locator(".news-list").getByRole("link", { name: "Ver más →" }).first();
    test.skip((await verMas.count()) === 0, "No hay noticias con enlace interno sin detalle");

    await expect(verMas).toHaveAttribute("href", /.+/);
    await expect(verMas).not.toHaveAttribute("href", /\/app\/noticias\/\d+/);
  });
});
