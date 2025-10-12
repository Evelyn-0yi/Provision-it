/**
 * Test helper utilities for Playwright E2E tests
 */

/**
 * Login as a user
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} username - Username
 * @param {string} password - Password
 */
export async function login(page, username = 'admin', password = 'admin123') {
  await page.goto('/frontend/login.html');
  await page.fill('#login', username);
  await page.fill('#password', password);
  await page.click('#btnLogin');
  await page.waitForLoadState('networkidle');
}

/**
 * Setup mock session storage for admin user
 * @param {import('@playwright/test').Page} page - Playwright page object
 */
export async function setupAdminSession(page) {
  await page.addInitScript(() => {
    sessionStorage.setItem('user', JSON.stringify({
      user_id: 1,
      user_name: 'admin',
      email: 'admin@test.com',
      is_manager: true
    }));
  });
}

/**
 * Setup mock session storage for regular user
 * @param {import('@playwright/test').Page} page - Playwright page object
 */
export async function setupUserSession(page) {
  await page.addInitScript(() => {
    sessionStorage.setItem('user', JSON.stringify({
      user_id: 2,
      user_name: 'testuser',
      email: 'user@test.com',
      is_manager: false
    }));
  });
}

/**
 * Mock API responses
 * @param {import('@playwright/test').Page} page - Playwright page object
 */
export async function mockApiResponses(page) {
  // Mock users endpoint
  await page.route('**/users', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        users: [
          { user_id: 1, user_name: 'admin', email: 'admin@test.com', is_manager: true },
          { user_id: 2, user_name: 'testuser', email: 'user@test.com', is_manager: false }
        ]
      })
    });
  });

  // Mock assets endpoint
  await page.route('**/assets', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        assets: [
          {
            asset_id: 1,
            asset_name: 'Test Asset 1',
            total_unit: 100,
            total_value: '10000.00',
            unit_min: 1,
            unit_max: 50,
            created_at: '2023-01-01T00:00:00Z'
          }
        ]
      })
    });
  });
}

/**
 * Wait for element to be visible with timeout
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} selector - CSS selector
 * @param {number} timeout - Timeout in ms
 */
export async function waitForElement(page, selector, timeout = 5000) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

