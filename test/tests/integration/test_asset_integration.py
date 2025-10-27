"""
Integration Tests for Asset Module
Tests API ↔ Database ↔ Service interactions for asset management
"""

import pytest
import json
from app import create_app, db
from app.models import User, Asset, Fraction, AssetValueHistory
from datetime import datetime


# ============================================================================
# IT-002: Verify POST /assets creates asset and persists in DB
# ============================================================================
# Test Case ID: IT-002
# Objective: Verify that creating an asset through API correctly persists
#            all data in the database
# Description: Test the full flow from API endpoint through service layer to
#             database, ensuring asset creation logic works end-to-end
# Expected Result: Asset is created, persisted, and can be retrieved with
#                 correct data
# ============================================================================

class TestAssetCreationIntegration:
    """Integration tests for asset creation"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app):
        """Setup test data"""
        with app.app_context():
            # Create admin user for creating assets
            self.admin_user = User(
                user_name='admin_asset_test',
                email='admin_asset@test.com',
                password='admin123',
                is_manager=True,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            db.session.add(self.admin_user)
            db.session.commit()
            self.admin_user_id = self.admin_user.user_id
            
        yield
        
        # Cleanup
        with app.app_context():
            # Delete in correct order (children before parents)
            test_assets = Asset.query.filter(Asset.asset_name.like('test_asset_%')).all()
            for asset in test_assets:
                AssetValueHistory.query.filter_by(asset_id=asset.asset_id).delete(synchronize_session=False)
                Fraction.query.filter_by(asset_id=asset.asset_id).delete(synchronize_session=False)
            Asset.query.filter(Asset.asset_name.like('test_asset_%')).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.admin_user_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it002_create_asset_persists_in_database(self, client, app):
        """
        IT-002-A: Creating asset via API persists in database
        
        Steps:
        1. POST to /assets with valid asset data
        2. Verify response is 201
        3. Query database to verify asset exists
        4. Verify all fields are correct
        """
        # Arrange
        asset_data = {
            'asset_name': 'test_asset_integration_001',
            'asset_description': 'Test asset for integration testing',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '50000.00'
        }
        
        # Act
        response = client.post('/assets',
                             data=json.dumps(asset_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201, "Asset creation should succeed"
        data = json.loads(response.data)
        assert 'asset' in data
        asset_id = data['asset']['asset_id']
        
        # Verify in database
        with app.app_context():
            asset = db.session.get(Asset, asset_id)
            assert asset is not None, "Asset should exist in database"
            assert asset.asset_name == asset_data['asset_name']
            assert asset.asset_description == asset_data['asset_description']
            assert asset.total_unit == asset_data['total_unit']
            assert asset.unit_min == asset_data['unit_min']
            assert asset.unit_max == asset_data['unit_max']
            assert float(asset.total_value) == float(asset_data['total_value'])
            assert asset.created_at is not None
    
    def test_it002_create_asset_validates_constraints(self, client, app):
        """
        IT-002-B: Asset creation validates business rules
        
        Steps:
        1. Try to create asset with invalid constraints
        2. Verify rejection
        3. Verify no asset created in database
        """
        # Arrange - invalid: unit_min > total_unit
        invalid_asset = {
            'asset_name': 'test_asset_invalid',
            'total_unit': 50,
            'unit_min': 100,  # Invalid: greater than total
            'unit_max': 200,
            'total_value': '10000.00'
        }
        
        # Act
        response = client.post('/assets',
                             data=json.dumps(invalid_asset),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400, "Invalid asset should be rejected"
        
        # Verify not in database
        with app.app_context():
            asset = Asset.query.filter_by(asset_name='test_asset_invalid').first()
            assert asset is None, "Invalid asset should not be in database"


# ============================================================================
# IT-003: Verify creating asset with initial fraction and value history
# ============================================================================
# Test Case ID: IT-003
# Objective: Verify that creating an asset automatically creates related
#            fraction and value history records
# Description: Test the service layer integration where AssetService calls
#             FractionService and ValueHistoryService
# Expected Result: One API call creates asset, fraction, and value history
#                 atomically
# ============================================================================

class TestAssetWithFractionIntegration:
    """Integration tests for asset creation with initial fraction"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app):
        """Setup test data"""
        with app.app_context():
            # Create admin and owner users
            self.admin_user = User(
                user_name='admin_frac_test',
                email='admin_frac@test.com',
                password='admin123',
                is_manager=True,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            self.owner_user = User(
                user_name='owner_frac_test',
                email='owner_frac@test.com',
                password='owner123',
                is_manager=False,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            db.session.add_all([self.admin_user, self.owner_user])
            db.session.commit()
            self.admin_user_id = self.admin_user.user_id
            self.owner_user_id = self.owner_user.user_id
            
        yield
        
        # Cleanup
        with app.app_context():
            # Delete in correct order (children before parents)
            test_assets = Asset.query.filter(Asset.asset_name.like('test_asset_frac_%')).all()
            for asset in test_assets:
                AssetValueHistory.query.filter_by(asset_id=asset.asset_id).delete(synchronize_session=False)
                Fraction.query.filter_by(asset_id=asset.asset_id).delete(synchronize_session=False)
            Asset.query.filter(Asset.asset_name.like('test_asset_frac_%')).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.admin_user_id).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.owner_user_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it003_create_asset_with_fraction_and_history(self, client, app):
        """
        IT-003-A: Creating asset creates fraction and value history atomically
        
        Steps:
        1. POST to /assets/with-initial-fraction
        2. Verify asset is created
        3. Verify initial fraction is created
        4. Verify value history record is created
        5. Verify all relationships are correct
        """
        # Arrange
        asset_data = {
            'asset_name': 'test_asset_frac_001',
            'asset_description': 'Asset with fraction',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 500,
            'total_value': '100000.00',
            'owner_id': self.owner_user_id,
            'adjusted_by': self.admin_user_id
        }
        
        # Act
        response = client.post('/assets/with-initial-fraction',
                             data=json.dumps(asset_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 201, "Asset with fraction should be created"
        data = json.loads(response.data)
        assert 'asset' in data
        assert 'fraction' in data
        assert 'value_history' in data
        
        asset_id = data['asset']['asset_id']
        fraction_id = data['fraction']['fraction_id']
        
        # Verify in database
        with app.app_context():
            # Check asset
            asset = db.session.get(Asset, asset_id)
            assert asset is not None
            assert asset.asset_name == asset_data['asset_name']
            
            # Check fraction
            fraction = db.session.get(Fraction, fraction_id)
            assert fraction is not None
            assert fraction.asset_id == asset_id
            assert fraction.owner_id == self.owner_user_id
            assert fraction.units == asset_data['total_unit'], "Initial fraction should have all units"
            assert fraction.is_active is True
            assert fraction.parent_fraction_id is None, "Initial fraction has no parent"
            
            # Check value history
            history = AssetValueHistory.query.filter_by(asset_id=asset_id).first()
            assert history is not None
            assert float(history.value) == float(asset_data['total_value'])
            assert history.source == 'initial_creation'
            assert history.adjusted_by == self.admin_user_id
            assert history.adjustment_reason == 'Initial value'
    
    def test_it003_create_asset_rollback_on_error(self, client, app):
        """
        IT-003-B: If fraction creation fails, asset creation is rolled back
        
        Steps:
        1. Try to create asset with invalid owner_id
        2. Verify error response
        3. Verify no asset in database
        4. Verify no fraction in database
        5. Verify transaction rollback worked
        """
        # Arrange
        asset_data = {
            'asset_name': 'test_asset_frac_rollback',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 500,
            'total_value': '100000.00',
            'owner_id': 99999,  # Non-existent user
            'adjusted_by': self.admin_user_id
        }
        
        # Act
        response = client.post('/assets/with-initial-fraction',
                             data=json.dumps(asset_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code in [400, 404], "Should fail with invalid owner"
        
        # Verify rollback - nothing in database
        with app.app_context():
            asset = Asset.query.filter_by(asset_name='test_asset_frac_rollback').first()
            assert asset is None, "Asset should not exist after rollback"
            
            fractions = Fraction.query.filter_by(owner_id=99999).all()
            assert len(fractions) == 0, "No fractions should exist after rollback"


# ============================================================================
# IT-004: Verify PATCH /assets/:id updates DB and cascades to value history
# ============================================================================
# Test Case ID: IT-004
# Objective: Verify that updating an asset's value creates a new value
#            history entry
# Description: Test the cascade effect where asset updates trigger related
#             table updates
# Expected Result: Asset value is updated and a new history record is created
# ============================================================================

class TestAssetUpdateIntegration:
    """Integration tests for asset updates"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app):
        """Setup test data"""
        with app.app_context():
            # Create admin user
            self.admin_user = User(
                user_name='admin_update_test',
                email='admin_update@test.com',
                password='admin123',
                is_manager=True,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            db.session.add(self.admin_user)
            db.session.commit()
            self.admin_user_id = self.admin_user.user_id
            
            # Create test asset
            self.test_asset = Asset(
                asset_name='test_asset_update_001',
                asset_description='Asset for update testing',
                total_unit=1000,
                unit_min=1,
                unit_max=500,
                total_value='50000.00',
                created_at=datetime.utcnow()
            )
            db.session.add(self.test_asset)
            db.session.commit()
            self.asset_id = self.test_asset.asset_id
            
            # Create initial value history
            initial_history = AssetValueHistory(
                asset_id=self.asset_id,
                value=50000.00,
                recorded_at=datetime.utcnow(),
                source='initial_creation',
                adjusted_by=self.admin_user_id,
                adjustment_reason='Initial value'
            )
            db.session.add(initial_history)
            db.session.commit()
            
        yield
        
        # Cleanup
        with app.app_context():
            AssetValueHistory.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            Asset.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.admin_user_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it004_update_asset_value_creates_history(self, client, app):
        """
        IT-004-A: Updating asset value creates new value history record
        
        Steps:
        1. POST to /assets/:id/values/adjust with new value
        2. Verify response success
        3. Verify asset value is updated in database
        4. Verify new value history record is created
        5. Verify old history record still exists
        """
        # Arrange
        new_value = 75000.00
        adjustment_data = {
            'value': new_value,
            'reason': 'Market appreciation',
            'adjusted_by': self.admin_user_id
        }
        
        # Act
        response = client.post(f'/assets/{self.asset_id}/values/adjust',
                             data=json.dumps(adjustment_data),
                             content_type='application/json')
        
        # Assert - API returns 201 CREATED when creating a new value history record
        assert response.status_code in [200, 201], f"Value adjustment should succeed, got {response.status_code}"
        
        # Verify asset value updated
        with app.app_context():
            asset = db.session.get(Asset, self.asset_id)
            assert float(asset.total_value) == new_value, "Asset value should be updated"
            
            # Verify history records
            history_records = AssetValueHistory.query.filter_by(
                asset_id=self.asset_id
            ).order_by(AssetValueHistory.recorded_at).all()
            
            assert len(history_records) == 2, "Should have 2 history records"
            
            # Check old record
            assert float(history_records[0].value) == 50000.00
            assert history_records[0].source == 'initial_creation'
            
            # Check new record
            assert float(history_records[1].value) == new_value
            assert history_records[1].source == 'manual_adjust'
            assert history_records[1].adjustment_reason == 'Market appreciation'
            assert history_records[1].adjusted_by == self.admin_user_id
    
    def test_it004_non_manager_cannot_adjust_value(self, client, app):
        """
        IT-004-B: Non-manager users cannot adjust asset values
        
        Steps:
        1. Create regular (non-manager) user
        2. Try to adjust value with their user_id
        3. Verify rejection
        4. Verify value not changed in database
        """
        # Arrange - Create regular user
        with app.app_context():
            regular_user = User(
                user_name='regular_user_test',
                email='regular@test.com',
                password='user123',
                is_manager=False,
                created_at=datetime.utcnow()
            )
            db.session.add(regular_user)
            db.session.commit()
            regular_user_id = regular_user.user_id
        
        adjustment_data = {
            'value': 80000.00,
            'reason': 'Unauthorized adjustment',
            'adjusted_by': regular_user_id
        }
        
        # Act
        response = client.post(f'/assets/{self.asset_id}/values/adjust',
                             data=json.dumps(adjustment_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 403, "Non-manager should be denied"
        
        # Verify value not changed
        with app.app_context():
            asset = db.session.get(Asset, self.asset_id)
            assert float(asset.total_value) == 50000.00, "Value should not change"
            
            # Cleanup
            User.query.filter_by(user_id=regular_user_id).delete(synchronize_session=False)
            db.session.commit()

