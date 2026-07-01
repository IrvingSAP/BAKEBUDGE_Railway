import { test, expect } from "@playwright/test";
import { E2E_SKIP_MESSAGE, getE2eCredentials, loginAsE2eUser } from "../helpers/auth";

const creds = getE2eCredentials();

test.describe("Analytics — acceso", () => {
  test("estadísticas redirige a login sin sesión", async ({ page }) => {
    await page.goto("/app/estadisticas/");
    await expect(page).toHaveURL(/\/ingresar\/?/);
  });
});

test.describe("Analytics — estadísticas (/app/estadisticas/)", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!creds, E2E_SKIP_MESSAGE);
    await loginAsE2eUser(page, creds!);
    await page.goto("/app/estadisticas/");
  });

  test("cabecera y descripción", async ({ page }) => {
    await expect(page).toHaveTitle(/Estadísticas/i);
    await expect(page.getByRole("heading", { level: 1, name: "Estadísticas" })).toBeVisible();
    await expect(
      page.getByText("Snapshots de producción completada — solo órdenes finalizadas")
    ).toBeVisible();
  });

  test("filtros GET: periodo, receta y categoría", async ({ page }) => {
    const filters = page.getByRole("search", { name: "Filtrar estadísticas" });
    await expect(filters).toBeVisible();
    await expect(filters.getByLabel("Periodo")).toBeVisible();
    await expect(filters.getByLabel("Receta")).toBeVisible();
    await expect(filters.getByLabel("Categoría insumo")).toBeVisible();
    await expect(filters.getByRole("button", { name: "Limpiar filtros" })).toBeVisible();

    await expect(filters.locator("#filter-periodo option").first()).toHaveText("Todos");
    await expect(filters.locator("#filter-receta option").first()).toHaveText("Todas");
    await expect(filters.locator("#filter-categoria option").first()).toHaveText("Todas");
  });

  test("KPIs del periodo", async ({ page }) => {
    const grid = page.locator(".stats-grid");
    await expect(grid).toBeVisible();

    const cards = grid.locator(".stat-card");
    await expect(cards).toHaveCount(4);
    await expect(cards.nth(0)).toContainText("Margen real (periodo)");
    await expect(cards.nth(0)).toContainText("Objetivo");
    await expect(cards.nth(1)).toContainText("Ganancia total");
    await expect(cards.nth(2)).toContainText("Órdenes completadas");
    await expect(cards.nth(2)).toContainText("Con snapshot analytics");
    await expect(cards.nth(3)).toContainText("Órdenes con pérdida");
    await expect(cards.nth(3)).toContainText("Margen");
  });

  test("widgets de ranking y evolución", async ({ page }) => {
    await expect(page.getByRole("heading", { level: 2, name: "Recetas más producidas" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Insumos más usados" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Versiones más productivas" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Evolución costo / porción" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 2, name: "Ratio indirectos / ingredientes" })).toBeVisible();

    await expect(page.locator(".bar-list").first()).toBeVisible();
    await expect(page.locator(".estadisticas-ratio")).toBeVisible();
  });

  test("tabla detalle por producción completada", async ({ page }) => {
    await expect(
      page.getByRole("heading", { level: 2, name: "Detalle por producción completada" })
    ).toBeVisible();

    const table = page.locator("#tabla-analytics");
    await expect(table).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Código" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Receta" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Unidades" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Costo prod." })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Precio venta" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Margen real" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Ganancia" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Período" })).toBeVisible();
  });

  test("estado vacío o filas de detalle", async ({ page }) => {
    const table = page.locator("#tabla-analytics tbody");
    const emptyRow = table.getByText("Aún no hay producciones completadas");
    const dataRows = table.locator("tr");

    if (await emptyRow.isVisible()) {
      await expect(emptyRow).toBeVisible();
    } else {
      await expect(dataRows.first()).toBeVisible();
    }
  });

  test("limpiar filtros vuelve a URL base", async ({ page }) => {
    await page.goto("/app/estadisticas/?periodo=2026-01");
    await page.getByRole("button", { name: "Limpiar filtros" }).click();
    await expect(page).toHaveURL(/\/app\/estadisticas\/?$/);
  });

  test("sidebar: enlace Estadísticas", async ({ page }) => {
    await page.goto("/app/");
    await page.getByRole("link", { name: "Estadísticas", exact: true }).click();
    await expect(page).toHaveURL(/\/app\/estadisticas\/?$/);
    await expect(page.getByRole("heading", { level: 1, name: "Estadísticas" })).toBeVisible();
  });
});
