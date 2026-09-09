import { defineConfig, devices } from '@playwright/test';

const backendUrl = 'http://localhost:8010';
const frontendUrl = 'http://localhost:3010';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: frontendUrl,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: process.env.CI ? undefined : 'chrome',
      },
    },
  ],
  webServer: [
    {
      command: 'uv run python -m tests.e2e_seed && uv run uvicorn app.main:app --host 127.0.0.1 --port 8010',
      cwd: '../backend',
      env: {
        ...process.env,
        DATABASE_URL: 'sqlite:///./e2e_test.db',
        CORS_ALLOW_ORIGINS: frontendUrl,
      },
      url: `${backendUrl}/health`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: 'pnpm exec next build && pnpm exec next start -H 0.0.0.0 -p 3010',
      env: {
        ...process.env,
        NEXT_PUBLIC_API_URL: backendUrl,
      },
      url: frontendUrl,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
