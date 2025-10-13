/**
 * Unit tests for common JavaScript functions across multiple HTML files
 */

const { loadHTMLFile, setupDOM, executeScript, mockFetchResponse, wait } = require('./test-utils');

describe('browsing.html JavaScript', () => {
  let html, script;

  beforeAll(() => {
    const loaded = loadHTMLFile('browsing.html');
    html = loaded.html;
    script = loaded.script;
  });

  beforeEach(() => {
    setupDOM(html);
    sessionStorage.setItem('user', JSON.stringify({ user_id: 1, user_name: 'testuser' }));
    executeScript(script);
    
    global.getAssetCategory = window.getAssetCategory;
    global.clearFilters = window.clearFilters;
    global.toggleView = window.toggleView;
    global.isGridView = window.isGridView;
  });

  test('should have search and filter elements', () => {
    expect(document.getElementById('searchInput')).toBeTruthy();
    expect(document.getElementById('categoryFilter')).toBeTruthy();
    expect(document.getElementById('sortBy')).toBeTruthy();
  });

  test('getAssetCategory should categorize assets', () => {
    expect(getAssetCategory({ asset_name: 'Real Estate Property' })).toBe('Real Estate');
    expect(getAssetCategory({ asset_name: 'Stock Portfolio' })).toBe('Stocks');
    expect(getAssetCategory({ asset_name: 'Bitcoin Fund' })).toBe('Cryptocurrency');
  });

  test('clearFilters should reset all filter inputs', () => {
    document.getElementById('searchInput').value = 'test';
    document.getElementById('minPrice').value = '100';
    
    clearFilters();
    
    expect(document.getElementById('searchInput').value).toBe('');
    expect(document.getElementById('minPrice').value).toBe('');
  });

  test('toggleView should switch between grid and list view', () => {
    // Check observable behavior - the button text changes
    const button = document.getElementById('viewToggle');
    const initialText = button.textContent;
    
    toggleView();
    
    const newText = button.textContent;
    expect(newText).not.toBe(initialText);
    // Button should toggle between "List View" and "Grid View"
    expect(newText === 'List View' || newText === 'Grid View').toBe(true);
  });
});

describe('trading.html JavaScript', () => {
  let html, script;

  beforeAll(() => {
    const loaded = loadHTMLFile('trading.html');
    html = loaded.html;
    script = loaded.script;
  });

  beforeEach(() => {
    setupDOM(html);
    sessionStorage.setItem('user', JSON.stringify({ user_id: 1, user_name: 'testuser' }));
    executeScript(script);
    
    global.switchTab = window.switchTab;
    global.formatDate = window.formatDate;
    global.showMessage = window.showMessage;
    global.closeCreateOfferModal = window.closeCreateOfferModal;
    global.openCreateOfferModal = window.openCreateOfferModal;
  });

  test('should have required trading elements', () => {
    expect(document.getElementById('createOfferModal')).toBeTruthy();
    expect(document.getElementById('tradeConfirmModal')).toBeTruthy();
  });

  test('switchTab should change active tab', () => {
    const mockEvent = { target: document.querySelector('.tab') };
    global.event = mockEvent;
    
    switchTab('buy');
    
    expect(document.getElementById('buyTab').classList.contains('active')).toBe(true);
  });

  test('formatDate should format date strings', () => {
    const dateStr = '2024-01-15T10:30:00Z';
    const formatted = formatDate(dateStr);
    expect(formatted).toContain('/');
  });

  test('showMessage should display message with correct class', () => {
    showMessage('Test message', true);
    const container = document.getElementById('messageContainer');
    expect(container.innerHTML).toContain('Test message');
    expect(container.innerHTML).toContain('ok');

    showMessage('Error message', false);
    expect(container.innerHTML).toContain('Error message');
    expect(container.innerHTML).toContain('err');
  });

  test('closeCreateOfferModal should hide modal', () => {
    openCreateOfferModal();
    closeCreateOfferModal();
    
    const modal = document.getElementById('createOfferModal');
    expect(modal.style.display).toBe('none');
  });
});

describe('profile.html JavaScript', () => {
  let html, script;

  beforeAll(() => {
    const loaded = loadHTMLFile('profile.html');
    html = loaded.html;
    script = loaded.script;
  });

  beforeEach(() => {
    setupDOM(html);
    sessionStorage.setItem('user', JSON.stringify({ 
      user_id: 1, 
      user_name: 'testuser',
      email: 'test@example.com'
    }));
    executeScript(script);
    
    global.el = window.el;
    global.setMsg = window.setMsg;
    global.toggleEditMode = window.toggleEditMode;
    global.cancelEdit = window.cancelEdit;
    global.getCurrentUserId = window.getCurrentUserId;
    global.updateDeleteButtonState = window.updateDeleteButtonState;
  });

  test('el should get element by id', () => {
    const element = el('username');
    expect(element).toBeTruthy();
  });

  test('setMsg should update message element', () => {
    setMsg('Test message', true);
    const msg = el('msg');
    expect(msg.textContent).toBe('Test message');
    expect(msg.className).toContain('ok');
  });

  test('toggleEditMode should show/hide form', () => {
    toggleEditMode();
    expect(el('profileForm').style.display).toBe('block');
    expect(el('profileDisplay').style.display).toBe('none');
    
    toggleEditMode();
    expect(el('profileForm').style.display).toBe('none');
    expect(el('profileDisplay').style.display).toBe('block');
  });

  test('getCurrentUserId should return user id from session', () => {
    const userId = getCurrentUserId();
    expect(userId).toBe(1);
  });

  test('updateDeleteButtonState should enable/disable button based on inputs', () => {
    el('deleteConfirmation').value = 'DELETE';
    el('deletePassword').value = 'password123';
    
    updateDeleteButtonState();
    
    expect(el('confirmDeleteBtn').disabled).toBe(false);
  });

  test('updateDeleteButtonState should keep button disabled when confirmation is wrong', () => {
    el('deleteConfirmation').value = 'WRONG';
    el('deletePassword').value = 'password123';
    
    updateDeleteButtonState();
    
    expect(el('confirmDeleteBtn').disabled).toBe(true);
  });

  test('cancelEdit should reset form', () => {
    el('username').setAttribute('data-original', 'originaluser');
    el('username').value = 'newuser';
    
    cancelEdit();
    
    expect(el('username').value).toBe('originaluser');
  });
});

