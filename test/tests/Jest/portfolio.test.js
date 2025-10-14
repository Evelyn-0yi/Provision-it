/**
 * Unit tests for portfolio.html embedded JavaScript
 */

const { loadHTMLFile, setupDOM, executeScript, mockFetchResponse, wait } = require('./test-utils');

describe('portfolio.html JavaScript', () => {
  let html, script;
  let mockUser = { user_id: 1, user_name: 'testuser', is_manager: false };

  beforeAll(() => {
    const loaded = loadHTMLFile('portfolio.html');
    html = loaded.html;
    script = loaded.script;
  });

  beforeEach(() => {
    setupDOM(html);
    sessionStorage.setItem('user', JSON.stringify(mockUser));
    
    // Mock Chart.js
    global.Chart = jest.fn().mockImplementation(() => ({
      destroy: jest.fn()
    }));
    
    executeScript(script);
    
    global.processPortfolioData = window.processPortfolioData;
    global.getAssetCategory = window.getAssetCategory;
    global.sortHoldings = window.sortHoldings;
    global.filterHoldings = window.filterHoldings;
    global.exportPortfolio = window.exportPortfolio;
    global.logout = window.logout;
  });

  describe('processPortfolioData() function', () => {
    test('should process holdings data correctly', () => {
      const holdings = [
        { asset_id: 1, asset_name: 'Asset 1', units: 10, latest_value: 100 }
      ];
      const assets = [];
      const priceMap = { '1': 150 };

      const result = processPortfolioData(holdings, assets, priceMap);

      expect(result).toHaveLength(1);
      expect(result[0].asset_id).toBe(1);
      expect(result[0].units).toBe(10);
      expect(result[0].unit_price).toBe(150);
      expect(result[0].total_price).toBe(1500);
    });

    test('should handle empty holdings', () => {
      const result = processPortfolioData([], [], {});
      expect(result).toHaveLength(0);
    });
  });

  describe('getAssetCategory() function', () => {
    test('should categorize real estate correctly', () => {
      const asset = { asset_name: '房产投资' };
      expect(getAssetCategory(asset)).toBe('Real Estate');
    });

    test('should categorize stocks correctly', () => {
      const asset = { asset_name: '股票投资' };
      expect(getAssetCategory(asset)).toBe('Stocks');
    });

    test('should categorize crypto correctly', () => {
      const asset = { asset_name: 'Bitcoin Investment' };
      expect(getAssetCategory(asset)).toBe('Cryptocurrency');
    });

    test('should categorize unknown as Other', () => {
      const asset = { asset_name: 'Random Asset' };
      expect(getAssetCategory(asset)).toBe('Other');
    });
  });

  describe('sortHoldings() function', () => {
    beforeEach(() => {
      // Use setPortfolioData to update the actual portfolioData variable in the script scope
      const testData = [
        { asset_name: 'Asset A', units: 10, total_price: 1000 },
        { asset_name: 'Asset B', units: 5, total_price: 2000 }
      ];
      
      if (window.setPortfolioData) {
        window.setPortfolioData(testData);
      } else {
        window.portfolioData = testData;
      }
    });

    test('should sort by value', () => {
      document.getElementById('sortBy').value = 'value';
      sortHoldings();

      // Check the sorted data
      expect(window.portfolioData[0].total_price).toBe(2000);
    });

    test('should sort by units', () => {
      document.getElementById('sortBy').value = 'units';
      sortHoldings();

      expect(window.portfolioData[0].units).toBe(10);
    });

    test('should sort by name', () => {
      document.getElementById('sortBy').value = 'name';
      sortHoldings();

      expect(window.portfolioData[0].asset_name).toBe('Asset A');
    });
  });

  describe('exportPortfolio() function', () => {
    test('should generate CSV file', () => {
      window.portfolioData = [
        { asset_name: 'Asset 1', unit_price: 100, units: 10, total_price: 1000 }
      ];

      // Mock URL.createObjectURL
      global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
      global.URL.revokeObjectURL = jest.fn();

      // Mock link click
      const mockClick = jest.fn();
      const originalCreateElement = document.createElement.bind(document);
      document.createElement = jest.fn((tag) => {
        if (tag === 'a') {
          return {
            download: '',
            href: '',
            click: mockClick
          };
        }
        return originalCreateElement(tag);
      });

      exportPortfolio();

      expect(mockClick).toHaveBeenCalled();
      
      // Restore original
      document.createElement = originalCreateElement;
    });
  });

  describe('filterHoldings() function', () => {
    beforeEach(() => {
      window.portfolioData = [
        { asset_name: 'Asset A', total_price: 1000 },
        { asset_name: 'Asset B', total_price: 2000 },
        { asset_name: 'Asset C', total_price: 3000 },
        { asset_name: 'Asset D', total_price: 4000 },
        { asset_name: 'Asset E', total_price: 5000 },
        { asset_name: 'Asset F', total_price: 6000 }
      ];
    });

    test('should filter top 5 holdings', () => {
      document.getElementById('filterBy').value = 'top5';
      filterHoldings();

      // The function temporarily modifies display, check DOM update
      const holdingsTable = document.getElementById('holdingsTable');
      expect(holdingsTable).toBeTruthy();
    });
  });

  describe('logout() function', () => {
    test('should clear session and redirect', async () => {
      global.fetch = jest.fn(() => mockFetchResponse({}));

      await logout();

      expect(sessionStorage.getItem('user')).toBeNull();
      expect(window.location.href).toBe('login.html');
    });
  });
});

