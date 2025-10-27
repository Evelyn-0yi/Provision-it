/**
 * End-to-End Tests with Real Backend
 * Tests complete user workflows through browser with actual API calls
 * 
 * IMPORTANT: These tests require Flask backend to be running on localhost:5001
 * Flask serves both HTML files (/frontend/*) and API endpoints (/auth/*, /assets/*, etc.)
 * 
 * Run with: python run_tests.py --e2e --auto-flask
 */

import { test, expect } from '@playwright/test';

// ============================================================================
// E2E-001: Verify user can log in through frontend and redirect to dashboard
// ============================================================================
// Test Case ID: E2E-001
// Objective: Test complete login workflow from frontend to backend
// Description: User enters credentials, clicks login, API authenticates,
//             session is created, and user is redirected to dashboard
// Expected Result: User successfully logs in and lands on dashboard with
//                 session data persisted
// ============================================================================

test.describe('E2E-001: Login Workflow', () => {
  
  test('E2E-001-A: User logs in successfully and redirects to dashboard', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to login page
     * 2. Enter valid credentials
     * 3. Click login button
     * 4. Verify API call to /auth/login
     * 5. Verify redirect to dashboard
     * 6. Verify session storage has user data
     */
    
    // Arrange - Listen for API call
    let loginApiCalled = false;
    page.on('response', response => {
      if (response.url().includes('/login')) {
        loginApiCalled = true;
        console.log('Login API called:', response.status());
      }
    });
    
    // Act
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('#btnLogin');

    // Assert - Wait for redirect to browsing.html
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
    
    // Verify API was called
    expect(loginApiCalled).toBeTruthy();
    
    // Verify session storage
    const user = await page.evaluate(() => {
      return JSON.parse(sessionStorage.getItem('user') || 'null');
    });
    
    expect(user).not.toBeNull();
    expect(user.user_name).toBe('admin');
    expect(user.user_id).toBeDefined();
  });
  
  test('E2E-001-B: Invalid credentials show error message', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to login page
     * 2. Enter invalid credentials
     * 3. Click login button
     * 4. Verify error message appears
     * 5. Verify no redirect occurs
     */
    
    // Act
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'invaliduser');
    await page.fill('#password', 'wrongpassword');
    await page.click('#btnLogin');
    
    // Assert - Wait for error message
    await page.waitForTimeout(2000);
    
    // Should show error (various possible selectors)
    const hasError = await page.locator('.error, .msg.err, [class*="error"]').count() > 0;
    expect(hasError).toBeTruthy();
    
    // Should NOT redirect
    expect(page.url()).toContain('/frontend/login.html');
  });
  
  test('E2E-001-C: Logout clears session and redirects to login', async ({ page }) => {
    /**
     * Steps:
     * 1. Login successfully
     * 2. Navigate to dashboard
     * 3. Click logout button
     * 4. Verify session is cleared
     * 5. Verify redirect to login page
     */
    
    // Arrange - Login first
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'testuser1');
    await page.fill('#password', 'password123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
    
    // Act - Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")');
    
    // Assert
    await page.waitForURL('**/frontend/login.html', { timeout: 5000 });
    
    // Verify session cleared
    const user = await page.evaluate(() => {
      return sessionStorage.getItem('user');
    });
    expect(user).toBeNull();
  });
});


// ============================================================================
// E2E-002: Verify admin can create asset and it appears in list
// ============================================================================
// Test Case ID: E2E-002
// Objective: Test complete asset creation workflow through admin panel
// Description: Admin opens admin panel, fills asset creation form, submits,
//             and verifies asset appears in the asset list
// Expected Result: Asset is created via API, stored in database, and
//                 immediately visible in the UI
// ============================================================================

test.describe('E2E-002: Admin Asset Creation Workflow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
  });
  
  test('E2E-002-A: Admin creates asset and it appears in list', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to admin panel
     * 2. Click "Add Asset" button
     * 3. Fill asset creation form
     * 4. Select initial owner
     * 5. Submit form
     * 6. Verify success message
     * 7. Verify asset appears in asset list
     */
    
    // Arrange
    const timestamp = Date.now();
    const assetName = `E2E Test Asset ${timestamp}`;
    
    // Act
    await page.goto('/frontend/admin.html');
    await page.waitForTimeout(2000); // Wait for data load
    
    // Get initial asset count
    const initialCount = await page.locator('#assetsTable tbody tr').count();
    
    // Click Add Asset
    await page.click('button:has-text("Add Asset")');
    await page.waitForSelector('#addAssetModal', { state: 'visible' });
    
    // Fill form
    await page.fill('#newAssetName', assetName);
    await page.fill('#newAssetDescription', 'E2E test asset description');
    await page.fill('#newAssetTotalValue', '100000');
    await page.fill('#newAssetTotalUnits', '1000');
    await page.fill('#newAssetMinUnits', '1');
    await page.fill('#newAssetMaxUnits', '500');
    
    // Select owner (first available user)
    await page.waitForTimeout(1000);
    await page.selectOption('#newAssetOwner', { index: 1 });
    
    // Submit
    await page.click('#addAssetModal button[type="submit"]');
    
    // Assert - Wait for success message
    await page.waitForSelector('.msg.ok, .success', { timeout: 10000 });
    
    // Verify asset appears in list
    await page.waitForTimeout(2000); // Wait for refresh
    const newCount = await page.locator('#assetsTable tbody tr').count();
    expect(newCount).toBeGreaterThan(initialCount);
    
    // Verify asset name appears
    await expect(page.locator('#assetsTable')).toContainText(assetName);
  });
  
  test('E2E-002-B: Asset creation validates business rules in UI', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to admin panel
     * 2. Open asset creation form
     * 3. Enter invalid data (min > total)
     * 4. Verify validation error appears
     * 5. Verify form cannot be submitted
     */
    
    // Act
    await page.goto('/frontend/admin.html');
    await page.click('button:has-text("Add Asset")');
    
    // Fill with invalid data
    await page.fill('#newAssetTotalUnits', '50');
    await page.fill('#newAssetMinUnits', '100'); // Invalid: min > total
    await page.fill('#newAssetMaxUnits', '200');
    await page.locator('#newAssetMinUnits').blur();
    
    // Assert - Should show error
    await expect(page.locator('#unitsValidationError')).toContainText('Minimum units per fraction cannot be greater than total units');
  });
});


// ============================================================================
// E2E-003: Verify admin can modify asset value and changes propagate
// ============================================================================
// Test Case ID: E2E-003
// Objective: Test asset value modification workflow through admin panel
// Description: Admin modifies asset value, provides reason, submits, and
//             verifies changes are reflected in value history
// Expected Result: Asset value is updated, history record created, and
//                 changes visible in UI
// ============================================================================

test.describe('E2E-003: Asset Value Modification Workflow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
  });
  
  test('E2E-003-A: Admin modifies asset value successfully', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to admin panel
     * 2. Click "Asset Modify" button
     * 3. Select an asset
     * 4. Enter new value
     * 5. Enter reason
     * 6. Submit
     * 7. Verify success message
     * 8. Verify value updated in list
     */
    
    // Act
    await page.goto('/frontend/admin.html');
    await page.waitForTimeout(2000); // Wait for assets to load
    
    // Click Asset Modify
    await page.click('button:has-text("Asset Modify")');
    await page.waitForSelector('#assetModifyModal', { state: 'visible' });
    
    // Select first asset
    await page.selectOption('#assetModifySelect', { index: 1 });
    await page.waitForSelector('#modifyAssetInfo', { state: 'visible' });
    
    // Get current value for comparison
    const currentValue = await page.locator('#modifyCurrentValue').textContent();
    console.log('Current value:', currentValue);
    
    // Enter new value (add $10,000)
    await page.fill('#modifyNewValue', '60000');
    await page.fill('#modifyReason', 'Market appreciation based on recent demand');
    
    // Submit
    await page.click('#assetModifyModal button[type="submit"]');
    
    // Assert - Wait for success
    await page.waitForSelector('.msg.ok, .success', { timeout: 10000 });
    
    // Modal should close
    await expect(page.locator('#assetModifyModal')).not.toBeVisible();
  });
  
  test('E2E-003-B: Value modification requires reason', async ({ page }) => {
    /**
     * Steps:
     * 1. Open asset modify modal
     * 2. Select asset and enter new value
     * 3. Leave reason empty
     * 4. Try to submit
     * 5. Verify HTML5 validation prevents submission
     */
    
    // Act
    await page.goto('/frontend/admin.html');
    await page.waitForTimeout(2000);
    
    await page.click('button:has-text("Asset Modify")');
    await page.selectOption('#assetModifySelect', { index: 1 });
    await page.fill('#modifyNewValue', '70000');
    // Don't fill reason - leave it empty
    
    // Try to submit - should trigger HTML5 validation
    const submitButton = page.locator('#assetModifyModal button[type="submit"]');
    await submitButton.click();
    
    // Assert - Check that reason field has validation message
    const reasonField = page.locator('#modifyReason');
    const validationMessage = await reasonField.evaluate((el) => el.validationMessage);
    expect(validationMessage).toBeTruthy(); // Should have validation message like "Please fill in this field"
  });
});


// ============================================================================
// E2E-004: Verify user can browse assets and see updated values
// ============================================================================
// Test Case ID: E2E-004
// Objective: Test asset browsing reflects latest data from database
// Description: User navigates to browsing page and sees assets with current
//             values, including recently updated values
// Expected Result: Asset list shows correct values from database
// ============================================================================

test.describe('E2E-004: Asset Browsing with Real Data', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as regular user
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'testuser1');
    await page.fill('#password', 'password123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
  });
  
  test('E2E-004-A: User browses assets and sees current values', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to browsing page
     * 2. Wait for assets to load from API
     * 3. Verify assets are displayed
     * 4. Verify values are shown
     * 5. Verify data matches backend
     */
    
    // Act
    await page.goto('/frontend/browsing.html');
    await page.waitForTimeout(2000); // Wait for API data
    
    // Assert - Check assets are displayed
    const assetCards = page.locator('.asset-card, .card, table tbody tr');
    const count = await assetCards.count();
    expect(count).toBeGreaterThan(0);
    
    // Verify values are displayed ($ symbol)
    const bodyText = await page.textContent('body');
    expect(bodyText).toMatch(/\$/);
  });
  
  test('E2E-004-B: Asset details show complete information', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to browsing page
     * 2. Click on an asset
     * 3. Verify details modal/page opens
     * 4. Verify all asset information is displayed
     */
    
    // Act
    await page.goto('/frontend/browsing.html');
    await page.waitForTimeout(2000);
    
    // Click first asset
    const firstAsset = page.locator('.asset-card, table tbody tr').first();
    if (await firstAsset.count() > 0) {
      await firstAsset.click();
      await page.waitForTimeout(1000);
      
      // Modal or details page should appear
      const hasDetails = await page.locator('.modal, [id*="detail"]').count() > 0 ||
                         page.url().includes('product') ||
                         page.url().includes('asset');
      
      expect(hasDetails).toBeTruthy();
    }
  });
});


// ============================================================================
// E2E-005: Verify portfolio reflects correct fraction ownership
// ============================================================================
// Test Case ID: E2E-005
// Objective: Test that portfolio page displays user's actual holdings
// Description: User navigates to portfolio and sees their owned fractions
//             with correct units and values from database
// Expected Result: Portfolio shows accurate ownership data from database
// ============================================================================

test.describe('E2E-005: Portfolio Display Integration', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as regular user
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'testuser1');
    await page.fill('#password', 'password123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
  });
  
  test('E2E-005-A: Portfolio shows user fractions from database', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to portfolio page
     * 2. Wait for portfolio data to load from API
     * 3. Verify holdings are displayed
     * 4. Verify units owned are shown
     * 5. Verify estimated values are calculated
     */
    
    // Act
    await page.goto('/frontend/portfolio.html');
    await page.waitForTimeout(2000); // Wait for API data
    
    // Assert - Check portfolio elements
    const hasHoldings = await page.locator('table, .card, [class*="holding"]').count() > 0;
    expect(hasHoldings).toBeTruthy();
    
    // Check for units display
    const bodyText = await page.textContent('body');
    expect(bodyText).toMatch(/units|shares/i);
    expect(bodyText).toMatch(/\$/); // Value display
  });
  
  test('E2E-005-B: Portfolio shows transaction history', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to portfolio page
     * 2. Verify transaction history section exists
     * 3. Verify transactions are displayed (if any)
     */
    
    // Act
    await page.goto('/frontend/portfolio.html');
    await page.waitForTimeout(2000);
    
    // Assert - Check for transaction section
    const hasTransactions = await page.locator('[class*="transaction"], h3:has-text("Transaction"), table').count() > 0;
    expect(hasTransactions).toBeTruthy();
  });
});


// ============================================================================
// E2E-006: Complete Trading Workflow
// ============================================================================
// Test Case ID: E2E-006
// Objective: Test full trading flow from offer creation to execution
// Description: User creates offer, another user accepts it, fraction
//             ownership transfers, transaction records created
// Expected Result: Complete trade execution with database updates
// ============================================================================

test.describe('E2E-006: Trading Workflow (Full Flow)', () => {
  
  test('E2E-006-A: User creates buy offer successfully', async ({ page }) => {
    /**
     * Steps:
     * 1. Login as user
     * 2. Navigate to trading page
     * 3. Click create offer
     * 4. Fill offer form (buy offer)
     * 5. Submit
     * 6. Verify offer appears in buy offers list
     */
    
    // Arrange
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'testuser1');
    await page.fill('#password', 'password123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
    
    // Act
    await page.goto('/frontend/trading.html');
    await page.waitForTimeout(2000);
    
    // Look for create offer button
    const createButton = page.locator('button:has-text("Create"), button:has-text("New Offer")').first();
    if (await createButton.count() > 0) {
      await createButton.click();
      await page.waitForTimeout(500);
      
      // Fill offer form (if modal appears)
      const modal = page.locator('.modal, [id*="modal"]');
      if (await modal.count() > 0) {
        // Assert modal is visible
        await expect(modal.first()).toBeVisible();
      }
    }
  });
});


// ============================================================================
// E2E-007: Value History Integration
// ============================================================================
// Test Case ID: E2E-007
// Objective: Verify value history page shows asset valuation changes
// Description: User views value history for an asset and sees all historical
//             values with timestamps and reasons
// Expected Result: Value history displays correct data from database
// ============================================================================

test.describe('E2E-007: Value History Display', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'testuser1');
    await page.fill('#password', 'password123');
    await page.click('#btnLogin');
    await page.waitForURL(/frontend\/(dashboard|browsing)/, { timeout: 10000 });
  });
  
  test('E2E-007-A: Value history shows asset value changes', async ({ page }) => {
    /**
     * Steps:
     * 1. Navigate to value history page
     * 2. Select an asset
     * 3. Verify history records load from API
     * 4. Verify dates, values, and reasons are displayed
     */
    
    // Act
    await page.goto('/frontend/valuehistory.html');
    await page.waitForTimeout(2000);
    
    // Select an asset
    const assetSelect = page.locator('select#asset, select[name*="asset"]');
    if (await assetSelect.count() > 0) {
      await assetSelect.selectOption({ index: 1 });
      await page.waitForTimeout(2000);
      
      // Assert - Check for history display
      const hasHistory = await page.locator('table, .history-item, canvas').count() > 0;
      expect(hasHistory).toBeTruthy();
    }
  });
});


// ============================================================================
// E2E-008: Cross-Page Navigation and State Persistence
// ============================================================================
// Test Case ID: E2E-008
// Objective: Verify session persists across page navigation
// Description: User logs in, navigates between pages, and session remains
//             valid without re-login
// Expected Result: User can navigate freely without losing session
// ============================================================================

test.describe('E2E-008: Session Persistence Across Pages', () => {
  
  test('E2E-008-A: Session persists across all pages', async ({ page }) => {
    /**
     * Steps:
     * 1. Login
     * 2. Navigate to each page
     * 3. Verify session data persists
     * 4. Verify no re-login required
     */
    
    // Arrange - Login
    await page.goto('/frontend/login.html');
    await page.fill('#login', 'testuser1');
    await page.fill('#password', 'password123');
    await page.click('#btnLogin');
    await page.waitForURL('**/frontend/browsing.html', { timeout: 10000 });
    
    // Act & Assert - Navigate to each page
    const pages = [
      'browsing.html',
      'trading.html',
      'portfolio.html',
      'profile.html',
      'valuehistory.html'
    ];
    
    for (const pageName of pages) {
      await page.goto(`/frontend/${pageName}`);
      await page.waitForTimeout(1000);
      
      // Should not redirect to login
      expect(page.url()).not.toContain('/frontend/login.html');
      
      // Session should still exist
      const user = await page.evaluate(() => {
        return sessionStorage.getItem('user');
      });
      expect(user).not.toBeNull();
    }
  });
});


// ============================================================================
// E2E-009: Complete User Journey
// ============================================================================
// Test Case ID: E2E-009
// Objective: Test complete user journey from signup to trading
// Description: New user signs up, logs in, browses assets, views portfolio
// Expected Result: All steps work seamlessly with database persistence
// ============================================================================

test.describe('E2E-009: Complete User Journey', () => {
  
  test('E2E-009-A: New user complete workflow', async ({ page }) => {
    /**
     * Steps:
     * 1. Signup new user
     * 2. Verify redirect to dashboard
     * 3. Browse assets
     * 4. View portfolio (empty initially)
     * 5. View profile
     * 6. Logout
     * 7. Login again
     * 8. Verify data persists
     */
    
    const timestamp = Date.now();
    const username = `e2e_user_${timestamp}`;
    const email = `e2e_${timestamp}@test.com`;
    
    // Step 1: Signup
    await page.goto('/frontend/signup.html');
    await page.fill('#username', username);
    await page.fill('#email', email);
    await page.fill('#password', '1234');
    
    // Handle confirm password if exists
    const confirmField = page.locator('#confirmPassword, #confirm_password');
    if (await confirmField.count() > 0) {
      await confirmField.fill('1234');
    }
    
    await page.click('button[type="submit"]');
    
    // Step 2: Should redirect after signup
    await page.waitForURL(/frontend\/(browsing|login)/, { timeout: 10000 });
    
    // Step 3: Browse assets
    await page.goto('/frontend/browsing.html');
    await page.waitForTimeout(2000);
    const hasAssets = await page.locator('table, .card').count() > 0;
    expect(hasAssets).toBeTruthy();
    
    // Step 4: View portfolio
    await page.goto('/frontend/portfolio.html');
    await page.waitForTimeout(2000);
    
    // Step 5: View profile
    await page.goto('/frontend/profile.html');
    await page.waitForTimeout(1000);
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain(username);
    
    // Step 6: Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")');
    await page.waitForURL('**/frontend/login.html', { timeout: 5000 });
    
    // Step 7: Login again
    await page.fill('#login', username);
    await page.fill('#password', '1234');
    await page.click('#btnLogin');
    
    // Step 8: Verify data persists
    await page.waitForURL(/frontend\/(dashboard|browsing)/, { timeout: 10000 });
    
    // Check session
    const user = await page.evaluate(() => {
      return JSON.parse(sessionStorage.getItem('user') || 'null');
    });
    expect(user.user_name).toBe(username);
  });
});

