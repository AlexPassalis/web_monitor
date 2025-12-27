import { defineConfig, devices } from "@playwright/test";

const base_url = "http://localhost:3000";

export default defineConfig({
  testDir: "./tests",
  outputDir: "./tests/results",
  fullyParallel: true,
  use: {
    baseURL: base_url,
    ignoreHTTPSErrors: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "bun run dev",
    url: base_url,
    reuseExistingServer: true,
  },
});
