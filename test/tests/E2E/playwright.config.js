import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './',
  fullyParallel: false,  // Run tests sequentially
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,  // Single worker only
  reporter: 'html',
  maxFailures: 1,  // Stop after first failure
  
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5001',
    trace: 'retain-on-failure',  // Save trace on failure
    screenshot: 'only-on-failure',  // Save screenshots on failure
    video: 'off',  // Disable video
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Disabled to reduce test noise - enable for cross-browser testing
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // No webServer needed - Flask serves HTML files on port 5001
  // HTML files are available at /frontend/login.html, /frontend/browsing.html, etc.
});
