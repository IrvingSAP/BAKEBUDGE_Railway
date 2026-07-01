import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

const djangoRoot = path.resolve(__dirname, "..");
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:8000";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : {
        command: "python manage.py runserver 127.0.0.1:8000 --noreload",
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
        cwd: djangoRoot,
      },
});
