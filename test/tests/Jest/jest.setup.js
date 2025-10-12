// Jest setup file for frontend unit tests
// This file runs before each test file

// Mock fetch globally with a default response
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({})
  })
);

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

global.sessionStorage = sessionStorageMock;

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

global.localStorage = localStorageMock;

// Mock location
delete window.location;
window.location = { 
  href: '',
  assign: jest.fn(),
  replace: jest.fn()
};

// Suppress console errors during tests (they're expected during script initialization)
const originalConsoleError = console.error;
global.consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation((...args) => {
  // Only suppress errors that are expected during script initialization
  const message = args[0]?.toString() || '';
  const errorObj = args[0];
  
  // Suppress expected initialization errors
  if (
    message.includes('Error fetching') ||
    message.includes('ReferenceError: portfolio is not defined') ||
    message.includes('Error loading') ||
    message.includes('HTMLCanvasElement.prototype.getContext') ||
    message.includes('Not implemented') ||
    message.includes('Failed to load assets') ||
    (errorObj && errorObj.type === 'not implemented')
  ) {
    // Suppress these expected errors
    return;
  }
  // Log other errors normally
  originalConsoleError.apply(console, args);
});

// Reset mocks before each test
beforeEach(() => {
  fetch.mockClear();
  fetch.mockImplementation(() => 
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({})
    })
  );
  sessionStorage.clear();
  localStorage.clear();
  window.location.href = '';
});

