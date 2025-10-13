/**
 * Unit tests for signup.html embedded JavaScript
 */

const { loadHTMLFile, setupDOM, executeScript, mockFetchResponse, mockFetchError, wait } = require('./test-utils');

describe('signup.html JavaScript', () => {
  let html, script;

  beforeAll(() => {
    const loaded = loadHTMLFile('signup.html');
    html = loaded.html;
    script = loaded.script;
  });

  beforeEach(() => {
    // Setup DOM with signup.html content
    setupDOM(html);
    
    // Mock setTimeout for redirect
    jest.useFakeTimers();
    
    // Execute the embedded script to define functions
    executeScript(script);
    
    // Make window functions available globally for tests
    global.el = window.el;
    global.setMsg = window.setMsg;
    global.validateForm = window.validateForm;
    global.signup = window.signup;
    global.backToLogin = window.backToLogin;
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('DOM Elements', () => {
    test('should have all required input elements', () => {
      expect(document.getElementById('username')).toBeTruthy();
      expect(document.getElementById('email')).toBeTruthy();
      expect(document.getElementById('password')).toBeTruthy();
      expect(document.getElementById('confirmPassword')).toBeTruthy();
      expect(document.getElementById('btnSignup')).toBeTruthy();
      expect(document.getElementById('btnBackToLogin')).toBeTruthy();
      expect(document.getElementById('msg')).toBeTruthy();
    });
  });

  describe('validateForm() function', () => {
    test('should return false when username is empty', () => {
      document.getElementById('username').value = '';
      document.getElementById('email').value = 'test@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const result = validateForm();
      expect(result).toBe(false);
      
      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('fill in all fields');
    });

    test('should return false when username is too short', () => {
      document.getElementById('username').value = 'ab';
      document.getElementById('email').value = 'test@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const result = validateForm();
      expect(result).toBe(false);
      
      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('at least 3 characters');
    });

    test('should return false when email is invalid', () => {
      document.getElementById('username').value = 'testuser';
      document.getElementById('email').value = 'invalid-email';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const result = validateForm();
      expect(result).toBe(false);
      
      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('valid email address');
    });

    test('should return false when passwords do not match', () => {
      document.getElementById('username').value = 'testuser';
      document.getElementById('email').value = 'test@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password456';

      const result = validateForm();
      expect(result).toBe(false);
      
      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('do not match');
    });

    test('should return false when password is too short', () => {
      document.getElementById('username').value = 'testuser';
      document.getElementById('email').value = 'test@example.com';
      document.getElementById('password').value = 'pas';
      document.getElementById('confirmPassword').value = 'pas';

      const result = validateForm();
      expect(result).toBe(false);
      
      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('at least 4 characters');
    });

    test('should return true when all fields are valid', () => {
      document.getElementById('username').value = 'testuser';
      document.getElementById('email').value = 'test@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const result = validateForm();
      expect(result).toBe(true);
    });

    test('should validate different email formats', () => {
      const validEmails = [
        'test@example.com',
        'user.name@example.co.uk',
        'test+tag@example.com',
        'user123@test-domain.com'
      ];

      validEmails.forEach(email => {
        document.getElementById('username').value = 'testuser';
        document.getElementById('email').value = email;
        document.getElementById('password').value = 'password123';
        document.getElementById('confirmPassword').value = 'password123';

        const result = validateForm();
        expect(result).toBe(true);
      });
    });
  });

  describe('signup() function', () => {
    test('should not proceed if validation fails', async () => {
      document.getElementById('username').value = '';
      document.getElementById('email').value = 'test@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      global.fetch = jest.fn();

      await signup();

      expect(fetch).not.toHaveBeenCalled();
    });

    test('should call API with correct data on successful signup', async () => {
      // Use real timers for this test to avoid timeout issues
      jest.useRealTimers();
      
      document.getElementById('username').value = 'newuser';
      document.getElementById('email').value = 'newuser@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const mockResponse = {
        status: 'success',
        user: { user_id: 1, user_name: 'newuser' }
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse));

      await signup();
      await wait(10);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5001/auth/signup',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            username: 'newuser',
            email: 'newuser@example.com',
            password: 'password123',
            confirm_password: 'password123'
          })
        })
      );

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('successfully');
      expect(msg.className).toContain('ok');
      
      // Restore fake timers for other tests
      jest.useFakeTimers();
    });

    test('should redirect to login page after successful signup', async () => {
      document.getElementById('username').value = 'newuser';
      document.getElementById('email').value = 'newuser@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const mockResponse = {
        status: 'success',
        user: { user_id: 1, user_name: 'newuser' }
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse));

      // Start signup
      const signupPromise = signup();
      
      // Wait for signup to complete
      await signupPromise;
      
      // Now fast-forward timers to trigger the redirect setTimeout
      jest.advanceTimersByTime(2000);

      expect(window.location.href).toBe('login.html');
    });

    test('should show error message on failed signup', async () => {
      document.getElementById('username').value = 'existinguser';
      document.getElementById('email').value = 'existing@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      const mockResponse = {
        status: 'error',
        message: 'Username already exists'
      };

      global.fetch = jest.fn(() => mockFetchResponse(mockResponse, 400, false));

      await signup();
      
      // Run pending promises
      await Promise.resolve();

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('Username already exists');
      expect(msg.className).toContain('err');
    }, 10000);

    test('should handle network errors gracefully', async () => {
      document.getElementById('username').value = 'newuser';
      document.getElementById('email').value = 'newuser@example.com';
      document.getElementById('password').value = 'password123';
      document.getElementById('confirmPassword').value = 'password123';

      global.fetch = jest.fn(() => mockFetchError('Network error'));

      await signup();
      
      // Run pending promises
      await Promise.resolve();

      const msg = document.getElementById('msg');
      expect(msg.textContent).toContain('Network error');
      expect(msg.className).toContain('err');
    }, 10000);
  });

  describe('backToLogin() function', () => {
    test('should redirect to login page', () => {
      backToLogin();
      expect(window.location.href).toBe('login.html');
    });
  });
});

