/**
 * Unit tests for login.html embedded JavaScript
 */

const { loadHTMLFile, setupDOM, executeScript, mockFetchResponse, mockFetchError, wait } = require('./test-utils');

describe('login.html JavaScript', () => {
  let html, script;

  beforeAll(() => {
    const loaded = loadHTMLFile('login.html');
    html = loaded.html;
    script = loaded.script;
  });

  beforeEach(() => {
    // Setup DOM with login.html content
    setupDOM(html);
    
    // Execute the embedded script to define functions
    executeScript(script);
    
    // Make window functions available globally for tests
    global.el = window.el;
    global.setMsg = window.setMsg;
    global.login = window.login;
  });

  describe('DOM Elements', () => {
    test('should have all required input elements', () => {
      expect(document.getElementById('login')).toBeTruthy();
      expect(document.getElementById('password')).toBeTruthy();
      expect(document.getElementById('btnLogin')).toBeTruthy();
      expect(document.getElementById('msg')).toBeTruthy();
    });
  });

  describe('Helper Functions', () => {
    test('el() should get element by id', () => {
      const loginInput = el('login');
      expect(loginInput).toBeTruthy();
      expect(loginInput.id).toBe('login');
    });

    test('setMsg() should update message element with text and style', () => {
      setMsg('Test message', null);
      const msg = document.getElementById('msg');
      expect(msg.textContent).toBe('Test message');
      expect(msg.className).toContain('muted');

      setMsg('Success message', true);
      expect(msg.textContent).toBe('Success message');
      expect(msg.className).toContain('ok');

      setMsg('Error message', false);
      expect(msg.textContent).toBe('Error message');
      expect(msg.className).toContain('err');
    });
  });

  describe('login() function', () => {
    test('should show error when login field is empty', async () => {
      document.getElementById('login').value = '';
      document.getElementById('password').value = 'password123';

      await login();

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('complete login information');
      expect(msg.className).toContain('err');
    });

    test('should show error when password field is empty', async () => {
      document.getElementById('login').value = 'testuser';
      document.getElementById('password').value = '';

      await login();

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('complete login information');
      expect(msg.className).toContain('err');
    });

    test('should call API with correct credentials on success', async () => {
      document.getElementById('login').value = 'testuser';
      document.getElementById('password').value = 'password123';

      const mockResponse = {
        status: 'success',
        user: { user_id: 1, user_name: 'testuser' },
        session: { session_token: 'test-token' }
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse));

      await login();
      await wait(10);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5001/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ login: 'testuser', password: 'password123' })
        })
      );

      // Check sessionStorage
      expect(sessionStorage.getItem('user')).toBeTruthy();
      expect(sessionStorage.getItem('sessionToken')).toBe('test-token');

      // Check redirect
      expect(window.location.href).toBe('browsing.html');
    });

    test('should show error message on failed login', async () => {
      document.getElementById('login').value = 'testuser';
      document.getElementById('password').value = 'wrongpassword';

      const mockResponse = {
        status: 'error',
        message: 'Invalid credentials'
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse, 401, false));

      await login();
      await wait(10);

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('Invalid credentials');
      expect(msg.className).toContain('err');
    });

    test('should handle network errors gracefully', async () => {
      document.getElementById('login').value = 'testuser';
      document.getElementById('password').value = 'password123';

      global.fetch = jest.fn(() => mockFetchError('Network error'));

      await login();
      await wait(10);

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('Network error');
      expect(msg.className).toContain('err');
    });

    test('should trim whitespace from login input', async () => {
      document.getElementById('login').value = '  testuser  ';
      document.getElementById('password').value = 'password123';

      const mockResponse = {
        status: 'success',
        user: { user_id: 1, user_name: 'testuser' },
        session: { session_token: 'test-token' }
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse));

      await login();
      await wait(10);

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ login: 'testuser', password: 'password123' })
        })
      );
    });

    test('should handle response without session data', async () => {
      document.getElementById('login').value = 'testuser';
      document.getElementById('password').value = 'password123';

      const mockResponse = {
        status: 'success',
        user: { user_id: 1, user_name: 'testuser' }
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse));

      await login();
      await wait(10);

      expect(sessionStorage.getItem('sessionToken')).toBe('');
      expect(window.location.href).toBe('browsing.html');
    });
  });
});

