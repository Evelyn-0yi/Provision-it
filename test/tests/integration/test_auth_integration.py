"""
Integration Tests for Authentication Module
Tests API ↔ Database interactions for auth endpoints
"""

import pytest
import json
from datetime import datetime
from app import create_app, db
from app.models import User


# ============================================================================
# IT-001: Verify /auth/login integrates correctly with the User DB table
# ============================================================================
# Test Case ID: IT-001
# Objective: Verify that the login endpoint correctly queries the User table
#            and returns appropriate responses
# Description: Test the full flow from API endpoint through service layer to
#             database, ensuring authentication logic works end-to-end
# Expected Result: Valid credentials return 200 with user data and session,
#                 invalid credentials return 401, soft-deleted users denied
# ============================================================================

class TestAuthLoginIntegration:
    """Integration tests for /auth/login endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app):
        """Setup test data for auth tests"""
        with app.app_context():
            # Create test user in database
            test_user = User(
                user_name='testuser_auth',
                email='test_auth@example.com',
                password='password123',  # Plain text for testing
                is_manager=False,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            db.session.add(test_user)
            db.session.commit()
            self.test_user_id = test_user.user_id
            
        yield
        
        # Cleanup
        with app.app_context():
            User.query.filter_by(user_id=self.test_user_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it001_login_with_valid_credentials(self, client, app):
        """
        IT-001-A: Login with valid username and password
        
        Steps:
        1. POST to /auth/login with valid credentials
        2. Verify response status is 200
        3. Verify user data is returned
        4. Verify session data is created
        5. Verify user is fetched from database
        """
        # Arrange
        login_data = {
            'username': 'testuser_auth',
            'password': 'password123'
        }
        
        # Act
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 200, "Login should succeed with valid credentials"
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['user_name'] == 'testuser_auth'
        assert data['user']['email'] == 'test_auth@example.com'
        assert 'session' in data
        assert 'user_id' in data['session']
        assert 'session_token' in data['session']
        
        # Verify database interaction
        with app.app_context():
            user = User.query.filter_by(user_name='testuser_auth').first()
            assert user is not None, "User should exist in database"
            assert not user.is_deleted, "User should not be soft-deleted"
    
    def test_it001_login_with_invalid_credentials(self, client):
        """
        IT-001-B: Login with invalid credentials should be rejected
        
        Steps:
        1. POST to /auth/login with wrong password
        2. Verify response status is 401
        3. Verify error message is returned
        """
        # Arrange
        login_data = {
            'username': 'testuser_auth',
            'password': 'wrongpassword'
        }
        
        # Act
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401, "Login should fail with invalid password"
        data = json.loads(response.data)
        assert 'error' in data or data.get('status') == 'error'
    
    def test_it001_login_with_nonexistent_user(self, client):
        """
        IT-001-C: Login with non-existent username should be rejected
        
        Steps:
        1. POST to /auth/login with non-existent username
        2. Verify response status is 401
        3. Verify appropriate error message
        """
        # Arrange
        login_data = {
            'username': 'nonexistent_user_xyz',
            'password': 'anypassword'
        }
        
        # Act
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data.get('message', '')
    
    def test_it001_login_soft_deleted_user_denied(self, client, app):
        """
        IT-001-D: Soft-deleted users cannot login
        
        Steps:
        1. Soft-delete a user in database
        2. Attempt to login
        3. Verify login is denied
        4. Verify proper error message
        """
        # Arrange - Soft delete the user
        with app.app_context():
            user = User.query.filter_by(user_name='testuser_auth').first()
            user.is_deleted = True
            db.session.commit()
        
        login_data = {
            'username': 'testuser_auth',
            'password': 'password123'
        }
        
        # Act
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401, "Soft-deleted users should not be able to login"
        
        # Cleanup - restore user
        with app.app_context():
            user = User.query.filter_by(user_name='testuser_auth').first()
            user.is_deleted = False
            db.session.commit()
    
    def test_it001_login_creates_session(self, client):
        """
        IT-001-E: Login creates session in Flask session
        
        Steps:
        1. Login with valid credentials
        2. Verify session is created
        3. Verify session contains user_id
        """
        # Arrange
        login_data = {
            'username': 'testuser_auth',
            'password': 'password123'
        }
        
        # Act
        with client:
            response = client.post('/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 200
            
            # Check Flask session (using client context)
            from flask import session
            assert 'user_id' in session, "Session should contain user_id"
            assert session['user_id'] == self.test_user_id


# ============================================================================
# IT-001-EXTRA: Signup integration tests
# ============================================================================

class TestAuthSignupIntegration:
    """Integration tests for /auth/signup endpoint"""
    
    def test_it001_signup_creates_user_in_database(self, client, app):
        """
        IT-001-F: Signup creates new user in database
        
        Steps:
        1. POST to /auth/signup with new user data
        2. Verify response is 201
        3. Verify user exists in database
        4. Verify user data is correct
        """
        # Arrange
        import time
        timestamp = int(time.time() * 1000)
        signup_data = {
            'username': f'newuser_{timestamp}',
            'email': f'newuser_{timestamp}@example.com',
            'password': 'password123',
            'is_manager': False
        }
        
        # Act
        response = client.post('/auth/signup',
                             data=json.dumps(signup_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Verify database
        with app.app_context():
            user = User.query.filter_by(user_name=signup_data['username']).first()
            assert user is not None, "User should be created in database"
            assert user.email == signup_data['email']
            assert not user.is_deleted
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    def test_it001_signup_duplicate_username_rejected(self, client, app):
        """
        IT-001-G: Signup with duplicate username is rejected
        
        Steps:
        1. Create a user
        2. Try to signup with same username
        3. Verify rejection with 400 status
        4. Verify database doesn't have duplicate
        """
        # Arrange - Create first user
        import time
        timestamp = int(time.time() * 1000)
        signup_data = {
            'username': f'duplicate_{timestamp}',
            'email': f'first_{timestamp}@example.com',
            'password': 'password123'
        }
        
        response1 = client.post('/auth/signup',
                              data=json.dumps(signup_data),
                              content_type='application/json')
        assert response1.status_code == 201
        
        # Act - Try duplicate username
        duplicate_data = {
            'username': f'duplicate_{timestamp}',
            'email': f'second_{timestamp}@example.com',
            'password': 'password123'
        }
        
        response2 = client.post('/auth/signup',
                              data=json.dumps(duplicate_data),
                              content_type='application/json')
        
        # Assert
        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert 'already exists' in data['message'].lower()
        
        # Verify only one user in database
        with app.app_context():
            users = User.query.filter_by(user_name=signup_data['username']).all()
            assert len(users) == 1, "Should only have one user with this username"
            
            # Cleanup
            db.session.delete(users[0])
            db.session.commit()

