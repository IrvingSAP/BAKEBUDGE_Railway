import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();
const DASHBOARD_HOME = "/app/";

test.describe("Dashboard — acceso", () => {
  test("home redirige a login sin sesión", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Dashboard — home (/app/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
  });

  test("login lleva al dashboard", async ({ page }) => {
    await expect(page).toHaveURL(/\/app\/?$/);
    await expect(page.locator("body")).toHaveAttribute("data-page", "dashboard");
  });

  test("cabecera y descripción", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    await expect(page).toHaveTitle(/Dashboard/i);
    await expect(page.getByRole("heading", { level: 1, name: "Dashboard" })).toBeVisible();
    await expect(page.getByText("Resumen de tu repostería")).toBeVisible();
  });

  test("KPIs: cuatro tarjetas con enlaces a módulos", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    const grid = page.locator(".stats-grid");
    await expect(grid).toBeVisible();

    const cards = grid.locator("a.stat-card-link");
    await expect(cards).toHaveCount(4);

    await expect(cards.nth(0)).toContainText("Productos activos");
    await expect(cards.nth(0)).toContainText("Insumos en catálogo");
    await expect(cards.nth(0)).toHaveAttribute("href", /\/app\/productos\/?$/);

    await expect(cards.nth(1)).toContainText("Recetas");
    await expect(cards.nth(1)).toContainText("con versión vigente");
    await expect(cards.nth(1)).toHaveAttribute("href", /\/app\/recetas\/?$/);

    await expect(cards.nth(2)).toContainText("Órdenes del mes");
    await expect(cards.nth(2)).toContainText("completadas");
    await expect(cards.nth(2)).toHaveAttribute("href", /\/app\/produccion\/?$/);

    await expect(cards.nth(3)).toContainText("Margen promedio");
    await expect(cards.nth(3)).toContainText("Objetivo:");
    await expect(cards.nth(3)).toContainText("Ver estadísticas");
    await expect(cards.nth(3)).toHaveAttribute("href", /\/app\/estadisticas\/?$/);

    await expect(cards.nth(0).locator(".value")).toHaveText(/^\d+$/);
    await expect(cards.nth(3).locator(".value")).toHaveText(/%$/);
  });

  test("tarjeta Productos activos navega al listado", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    await page.locator(".stats-grid a.stat-card-link").first().click();
    await expect(page).toHaveURL(/\/app\/productos\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Productos" })).toBeVisible();
  });

  test("tarjeta Margen promedio navega a estadísticas", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    await page.locator(".stats-grid a.stat-card-link").nth(3).click();
    await expect(page).toHaveURL(/\/app\/estadisticas\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Estadísticas" })).toBeVisible();
  });

  test("primeros pasos: checklist y enlaces", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    const section = page.locator(".content-grid section.card", {
      has: page.getByRole("heading", { level: 2, name: "Primeros pasos" }),
    });
    await expect(section).toBeVisible();
    await expect(section.getByText("Crear primer producto")).toBeVisible();
    await expect(section.getByText("Crear primera receta")).toBeVisible();
    await expect(section.getByRole("link", { name: "Ver productos" })).toHaveAttribute(
      "href",
      /\/app\/productos\/?$/
    );
    await expect(section.getByRole("link", { name: "Ver recetas" })).toHaveAttribute(
      "href",
      /\/app\/recetas\/?$/
    );
  });

  test("producción reciente: tabla y enlace ver todas", async ({ page }) => {
    await page.goto(DASHBOARD_HOME);
    const section = page.locator(".content-grid section.card", {
      has: page.getByRole("heading", { level: 2, name: "Producción reciente" }),
    });
    await expect(section).toBeVisible();

    const table = section.locator("table.table-bakebudge");
    await expect(table.getByRole("columnheader", { name: "Orden" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Receta" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Estado" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Costo" })).toBeVisible();

    const tbody = table.locator("tbody");
    const emptyRow = tbody.getByText("Aún no hay órdenes de producción registradas");
    const dataRows = tbody.locator("tr").filter({ hasNot: emptyRow });

    if (await emptyRow.isVisible()) {
      await expect(emptyRow).toBeVisible();
    } else {
      await expect(dataRows.first()).toBeVisible();
      await expect(dataRows.first().getByRole("link").first()).toHaveAttribute(
        "href",
        /\/app\/produccion\/\d+\/?$/
      );
    }

    await expect(section.getByRole("link", { name: /Ver todas las órdenes/i })).toHaveAttribute(
      "href",
      /\/app\/produccion\/?$/
    );
  });

  test("sidebar: enlace Dashboard", async ({ page }) => {
    await page.goto("/app/perfil/");
    await page.getByRole("link", { name: "Dashboard", exact: true }).click();
    await expect(page).toHaveURL(/\/app\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Dashboard" })).toBeVisible();
  });
});

test.describe("Dashboard — acceso denegado (/app/acceso-denegado/)", () => {
  test("redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/acceso-denegado/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });

  test("pantalla informativa con sesión", async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/acceso-denegado/");

    await expect(page).toHaveTitle(/Acceso denegado/i);
    await expect(page.locator("body")).toHaveAttribute("data-page", "acceso-denegado");
    await expect(page.getByRole("heading", { level: 1, name: "Acceso no disponible" })).toBeVisible();
    await expect(page.getByText("requieren una suscripción activa")).toBeVisible();
    await expect(page.getByRole("link", { name: "Contactar soporte" })).toHaveAttribute(
      "href",
      /\/contacto\/?$/
    );
    await expect(page.getByRole("link", { name: "Volver al inicio" })).toHaveAttribute("href", /\/$/);
  });
});
