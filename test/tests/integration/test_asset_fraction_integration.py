"""
Integration Tests for Asset-Fraction Module Integration
Tests AssetService ↔ FractionService ↔ ValueHistoryService interactions
"""

import pytest
import json
from app import create_app, db
from app.models import User, Asset, Fraction, AssetValueHistory
from app.services.asset_service import AssetService
from app.services.fraction_service import FractionService
from datetime import datetime


# ============================================================================
# IT-003: Verify creating asset automatically creates fraction and value history
# ============================================================================
# Test Case ID: IT-003
# Objective: Verify that AssetService.create_asset_with_initial_fraction()
#            correctly integrates with FractionService and ValueHistoryService
# Description: Test the multi-service integration where one operation creates
#             records in three different tables atomically
# Expected Result: Asset, Fraction, and AssetValueHistory all created in one
#                 transaction, or all rolled back on failure
# ============================================================================

class TestAssetFractionValueIntegration:
    """Integration tests for asset creation with fraction and value history"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Setup test users"""
        with app.app_context():
            # Create admin and owner users
            self.admin = User(
                user_name='admin_svc_test',
                email='admin_svc@test.com',
                password='admin123',
                is_manager=True,
                created_at=datetime.utcnow()
            )
            self.owner = User(
                user_name='owner_svc_test',
                email='owner_svc@test.com',
                password='owner123',
                is_manager=False,
                created_at=datetime.utcnow()
            )
            db.session.add_all([self.admin, self.owner])
            db.session.commit()
            self.admin_id = self.admin.user_id
            self.owner_id = self.owner.user_id
        
        yield
        
        # Cleanup
        with app.app_context():
            # Delete test data in correct order (children before parents)
            # First delete AssetValueHistory records
            test_assets = Asset.query.filter(Asset.asset_name.like('test_svc_%')).all()
            for asset in test_assets:
                AssetValueHistory.query.filter_by(asset_id=asset.asset_id).delete(synchronize_session=False)
            # Then delete Fractions
            Fraction.query.filter_by(owner_id=self.owner_id).delete(synchronize_session=False)
            # Then delete Assets
            Asset.query.filter(Asset.asset_name.like('test_svc_%')).delete(synchronize_session=False)
            # Finally delete Users
            User.query.filter_by(user_id=self.admin_id).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.owner_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it003_create_asset_creates_all_related_records(self, app):
        """
        IT-003-A: Asset creation creates Asset + Fraction + ValueHistory
        
        Steps:
        1. Call AssetService.create_asset_with_initial_fraction()
        2. Verify asset is created
        3. Verify initial fraction is created with all units
        4. Verify value history record is created
        5. Verify all foreign keys are correct
        6. Verify value_perunit is calculated correctly
        """
        # Arrange
        asset_data = {
            'asset_name': 'test_svc_asset_001',
            'asset_description': 'Service integration test',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 500,
            'total_value': '100000.00'
        }
        
        # Act
        with app.app_context():
            result = AssetService.create_asset_with_initial_fraction(
                asset_data,
                owner_id=self.owner_id,
                admin_user_id=self.admin_id
            )
            
            # Assert - Check returned objects
            assert 'asset' in result
            assert 'fraction' in result
            assert 'value_history' in result
            
            asset = result['asset']
            fraction = result['fraction']
            history = result['value_history']
            
            # Verify asset
            assert asset.asset_name == asset_data['asset_name']
            assert asset.total_unit == asset_data['total_unit']
            assert float(asset.total_value) == float(asset_data['total_value'])
            
            # Verify fraction
            assert fraction.asset_id == asset.asset_id
            assert fraction.owner_id == self.owner_id
            assert fraction.units == asset_data['total_unit'], "Should have ALL units initially"
            assert fraction.is_active is True
            assert fraction.parent_fraction_id is None
            
            # Verify value_perunit calculation
            expected_value_per_unit = 100000.00 / 1000  # total_value / total_unit
            assert float(fraction.value_perunit) == expected_value_per_unit
            
            # Verify value history
            assert history.asset_id == asset.asset_id
            assert float(history.value) == float(asset_data['total_value'])
            assert history.source == 'initial_creation'
            assert history.adjusted_by == self.admin_id
            
            # Verify database persistence
            db_asset = db.session.get(Asset, asset.asset_id)
            db_fraction = db.session.get(Fraction, fraction.fraction_id)
            db_history = AssetValueHistory.query.filter_by(asset_id=asset.asset_id).first()
            
            assert db_asset is not None
            assert db_fraction is not None
            assert db_history is not None
    
    def test_it003_rollback_on_fraction_creation_failure(self, app):
        """
        IT-003-B: If fraction creation fails, asset is rolled back
        
        Steps:
        1. Try to create asset with invalid owner_id
        2. Verify exception is raised
        3. Verify no asset is created in database
        4. Verify no fraction is created
        5. Verify no value history is created
        6. Verify transaction rollback worked
        """
        # Arrange
        asset_data = {
            'asset_name': 'test_svc_rollback',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 500,
            'total_value': '100000.00'
        }
        
        # Act & Assert
        with app.app_context():
            with pytest.raises(ValueError, match="Owner user not found"):
                AssetService.create_asset_with_initial_fraction(
                    asset_data,
                    owner_id=99999,  # Non-existent owner
                    admin_user_id=self.admin_id
                )
            
            # Verify rollback - nothing should be in database
            asset = Asset.query.filter_by(asset_name='test_svc_rollback').first()
            assert asset is None, "Asset should not exist after rollback"
            
            fractions = Fraction.query.filter_by(owner_id=99999).all()
            assert len(fractions) == 0, "No fractions should exist"
            
            history = AssetValueHistory.query.filter_by(
                adjustment_reason='Initial value'
            ).filter(
                AssetValueHistory.asset_id.in_(
                    db.session.query(Asset.asset_id).filter_by(asset_name='test_svc_rollback')
                )
            ).all()
            assert len(history) == 0, "No history records should exist"
    
    def test_it003_only_manager_can_create_asset(self, app):
        """
        IT-003-C: Only managers can create assets
        
        Steps:
        1. Create regular user (non-manager)
        2. Try to create asset with non-manager as admin_user_id
        3. Verify permission error
        4. Verify no asset created
        """
        # Arrange
        asset_data = {
            'asset_name': 'test_svc_unauthorized',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 500,
            'total_value': '100000.00'
        }
        
        # Act & Assert
        with app.app_context():
            # owner_id is a regular user (not manager)
            with pytest.raises(PermissionError, match="Only managers can create assets"):
                AssetService.create_asset_with_initial_fraction(
                    asset_data,
                    owner_id=self.owner_id,
                    admin_user_id=self.owner_id  # Regular user trying to create
                )
            
            # Verify no asset created
            asset = Asset.query.filter_by(asset_name='test_svc_unauthorized').first()
            assert asset is None


# ============================================================================
# IT-005: Verify Fraction ↔ Asset Integration
# ============================================================================
# Test Case ID: IT-005
# Objective: Verify fractions respect asset constraints (unit_min, unit_max)
# Description: Test that FractionService validates against Asset table
#             constraints when creating fractions
# Expected Result: Fractions within limits are created, outside limits rejected
# ============================================================================

class TestFractionAssetIntegration:
    """Integration tests for Fraction-Asset relationship"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Setup test asset"""
        with app.app_context():
            # Create owner user
            self.owner = User(
                user_name='owner_frac_int',
                email='owner_frac_int@test.com',
                password='owner123',
                is_manager=False,
                created_at=datetime.utcnow()
            )
            db.session.add(self.owner)
            db.session.commit()
            self.owner_id = self.owner.user_id
            
            # Create test asset
            self.asset = Asset(
                asset_name='test_asset_frac_int',
                total_unit=1000,
                unit_min=10,   # Minimum 10 units
                unit_max=500,  # Maximum 500 units
                total_value='100000.00',
                created_at=datetime.utcnow()
            )
            db.session.add(self.asset)
            db.session.commit()
            self.asset_id = self.asset.asset_id
        
        yield
        
        # Cleanup
        with app.app_context():
            # Delete in correct order (children before parents)
            AssetValueHistory.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            Fraction.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            Asset.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.owner_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it005_fraction_respects_asset_unit_min(self, app):
        """
        IT-005-A: Fraction creation validates against asset unit_min
        
        Steps:
        1. Try to create fraction with units < asset.unit_min
        2. Verify ValueError is raised
        3. Verify no fraction created in database
        """
        # Arrange
        fraction_data = {
            'asset_id': self.asset_id,
            'owner_id': self.owner_id,
            'units': 5  # Less than asset.unit_min (10)
        }
        
        # Act & Assert
        with app.app_context():
            with pytest.raises(ValueError, match="Units must be between"):
                FractionService.create_fraction(fraction_data)
            
            # Verify no fraction created
            fractions = Fraction.query.filter_by(
                asset_id=self.asset_id,
                units=5
            ).all()
            assert len(fractions) == 0
    
    def test_it005_fraction_respects_asset_unit_max(self, app):
        """
        IT-005-B: Fraction creation validates against asset unit_max
        
        Steps:
        1. Try to create fraction with units > asset.unit_max
        2. Verify ValueError is raised
        3. Verify no fraction created in database
        """
        # Arrange
        fraction_data = {
            'asset_id': self.asset_id,
            'owner_id': self.owner_id,
            'units': 600  # More than asset.unit_max (500)
        }
        
        # Act & Assert
        with app.app_context():
            with pytest.raises(ValueError, match="Units must be between"):
                FractionService.create_fraction(fraction_data)
            
            # Verify no fraction created
            fractions = Fraction.query.filter_by(
                asset_id=self.asset_id,
                units=600
            ).all()
            assert len(fractions) == 0
    
    def test_it005_fraction_within_limits_succeeds(self, app):
        """
        IT-005-C: Fraction within asset limits is created successfully
        
        Steps:
        1. Create fraction with valid units (within min/max)
        2. Verify fraction is created
        3. Verify database persistence
        4. Verify relationship with asset
        """
        # Arrange
        fraction_data = {
            'asset_id': self.asset_id,
            'owner_id': self.owner_id,
            'units': 100,  # Within range [10, 500]
            'value_perunit': 100.00
        }
        
        # Act
        with app.app_context():
            fraction = FractionService.create_fraction(fraction_data)
            
            # Assert
            assert fraction is not None
            assert fraction.asset_id == self.asset_id
            assert fraction.owner_id == self.owner_id
            assert fraction.units == 100
            assert fraction.is_active is True
            
            # Verify in database
            db_fraction = db.session.get(Fraction, fraction.fraction_id)
            assert db_fraction is not None
            
            # Verify asset relationship
            asset = db.session.get(Asset, self.asset_id)
            assert any(f.fraction_id == fraction.fraction_id for f in asset.fractions)

