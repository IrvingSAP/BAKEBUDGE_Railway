import { test, expect } from "@playwright/test";

test.describe("Smoke — zona pública", () => {
  test("la landing carga", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/BAKEBUDGE/i);
  });

  test("página de ingreso accesible", async ({ page }) => {
    await page.goto("/ingresar/");
    await expect(page.getByRole("heading", { name: /ingresar/i })).toBeVisible();
  });
});
