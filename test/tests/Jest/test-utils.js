/**
 * Utility functions for testing frontend JavaScript
 */
const fs = require('fs');
const path = require('path');

/**
 * Load HTML file and extract embedded JavaScript
 * @param {string} filename - Name of HTML file (e.g., 'login.html')
 * @returns {object} - { html, script }
 */
function loadHTMLFile(filename) {
  const frontendPath = path.join(__dirname, '../../../frontend', filename);
  const html = fs.readFileSync(frontendPath, 'utf-8');
  
  // Extract script content from HTML
  const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  const script = scriptMatch ? scriptMatch[1] : '';
  
  return { html, script };
}

/**
 * Setup DOM with HTML content
 * @param {string} html - HTML content
 */
function setupDOM(html) {
  document.body.innerHTML = html;
}

/**
 * Execute JavaScript code in the current context
 * @param {string} code - JavaScript code to execute
 * @returns {object} - Exposed functions from the script
 */
function executeScript(code) {
  // Create a new Function to execute the script in a controlled scope
  // Expose commonly used functions to window object
  const scriptWithExports = `
    ${code}
    // Expose functions to window if they exist
    if (typeof el !== 'undefined') window.el = el;
    if (typeof setMsg !== 'undefined') window.setMsg = setMsg;
    if (typeof login !== 'undefined') window.login = login;
    if (typeof logout !== 'undefined') window.logout = logout;
    if (typeof signup !== 'undefined') window.signup = signup;
    if (typeof validateForm !== 'undefined') window.validateForm = validateForm;
    if (typeof backToLogin !== 'undefined') window.backToLogin = backToLogin;
    if (typeof fetchDashboardData !== 'undefined') window.fetchDashboardData = fetchDashboardData;
    if (typeof updateDashboard !== 'undefined') window.updateDashboard = updateDashboard;
    if (typeof updateRecentActivity !== 'undefined') window.updateRecentActivity = updateRecentActivity;
    if (typeof updateTopAssets !== 'undefined') window.updateTopAssets = updateTopAssets;
    if (typeof refreshData !== 'undefined') window.refreshData = refreshData;
    if (typeof processPortfolioData !== 'undefined') window.processPortfolioData = processPortfolioData;
    if (typeof getAssetCategory !== 'undefined') window.getAssetCategory = getAssetCategory;
    if (typeof sortHoldings !== 'undefined') window.sortHoldings = sortHoldings;
    if (typeof filterHoldings !== 'undefined') window.filterHoldings = filterHoldings;
    if (typeof exportPortfolio !== 'undefined') window.exportPortfolio = exportPortfolio;
    if (typeof fetchPortfolioData !== 'undefined') window.fetchPortfolioData = fetchPortfolioData;
    if (typeof fetchAssets !== 'undefined') window.fetchAssets = fetchAssets;
    if (typeof clearFilters !== 'undefined') window.clearFilters = clearFilters;
    if (typeof toggleView !== 'undefined') window.toggleView = toggleView;
    if (typeof isGridView !== 'undefined') window.isGridView = isGridView;
    if (typeof switchTab !== 'undefined') window.switchTab = switchTab;
    if (typeof formatDate !== 'undefined') window.formatDate = formatDate;
    if (typeof showMessage !== 'undefined') window.showMessage = showMessage;
    if (typeof closeCreateOfferModal !== 'undefined') window.closeCreateOfferModal = closeCreateOfferModal;
    if (typeof openCreateOfferModal !== 'undefined') window.openCreateOfferModal = openCreateOfferModal;
    if (typeof toggleEditMode !== 'undefined') window.toggleEditMode = toggleEditMode;
    if (typeof cancelEdit !== 'undefined') window.cancelEdit = cancelEdit;
    if (typeof getCurrentUserId !== 'undefined') window.getCurrentUserId = getCurrentUserId;
    if (typeof updateDeleteButtonState !== 'undefined') window.updateDeleteButtonState = updateDeleteButtonState;
    // Expose portfolioData and make it writable
    if (typeof portfolioData !== 'undefined') {
      window.portfolioData = portfolioData;
      // Allow setting portfolioData from tests
      Object.defineProperty(window, 'setPortfolioData', {
        value: function(data) {
          portfolioData = data;
          window.portfolioData = portfolioData;
        },
        writable: true
      });
    }
    if (typeof allAssets !== 'undefined') window.allAssets = allAssets;
  `;
  
  try {
    eval(scriptWithExports);
  } catch (error) {
    console.error('Error executing script:', error);
  }
}

/**
 * Mock fetch response
 * @param {object} data - Response data
 * @param {number} status - HTTP status code
 * @param {boolean} ok - Response ok status
 */
function mockFetchResponse(data, status = 200, ok = true) {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data)
  });
}

/**
 * Mock fetch error
 * @param {string} message - Error message
 */
function mockFetchError(message = 'Network error') {
  return Promise.reject(new Error(message));
}

/**
 * Wait for async operations
 * @param {number} ms - Milliseconds to wait
 */
function wait(ms = 0) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Get element by ID (shorthand)
 * @param {string} id - Element ID
 */
function getById(id) {
  return document.getElementById(id);
}

/**
 * Set input value and trigger input event
 * @param {string} id - Element ID
 * @param {string} value - Input value
 */
function setInputValue(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

/**
 * Click element by ID
 * @param {string} id - Element ID
 */
function clickElement(id) {
  const element = document.getElementById(id);
  if (element) {
    element.click();
  }
}

module.exports = {
  loadHTMLFile,
  setupDOM,
  executeScript,
  mockFetchResponse,
  mockFetchError,
  wait,
  getById,
  setInputValue,
  clickElement
};

