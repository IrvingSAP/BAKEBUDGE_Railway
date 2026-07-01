import { expect, type Page } from "@playwright/test";
import { authenticator } from "otplib";

export type E2eCredentials = {
  username: string;
  password: string;
  totpSecret: string;
};

export const E2E_SKIP_MESSAGE =
  "Define PLAYWRIGHT_E2E_USER, PLAYWRIGHT_E2E_PASSWORD y PLAYWRIGHT_E2E_TOTP_SECRET (usuario Master con 2FA)";

export function getE2eCredentials(): E2eCredentials | null {
  const username = process.env.PLAYWRIGHT_E2E_USER;
  const password = process.env.PLAYWRIGHT_E2E_PASSWORD;
  const totpSecret = process.env.PLAYWRIGHT_E2E_TOTP_SECRET;
  if (!username || !password || !totpSecret) {
    return null;
  }
  return { username, password, totpSecret };
}

/** Login completo: credenciales + TOTP (usuario con seguridad ya configurada). */
export async function loginAsE2eUser(page: Page, creds: E2eCredentials): Promise<void> {
  await page.goto("/ingresar/");
  await page.getByLabel("Usuario").fill(creds.username);
  await page.locator(".acceso-form").getByLabel("Contraseña").fill(creds.password);
  await page.getByRole("button", { name: "Ingresar" }).click();

  await expect(page).toHaveURL(/\/seguridad\/totp\/?$/);
  const code = authenticator.generate(creds.totpSecret);
  await page.getByLabel("Código 2FA").fill(code);
  await page.getByRole("button", { name: "Verificar" }).click();

  await expect(page).toHaveURL(/\/app\//);
}
