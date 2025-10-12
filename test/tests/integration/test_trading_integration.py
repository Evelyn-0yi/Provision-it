"""
Integration Tests for Trading Module
Tests OfferService ↔ TradingService ↔ TransactionService interactions
"""

import pytest
import json
from app import create_app, db
from app.models import User, Asset, Fraction, Offer, Transaction, AssetValueHistory
from app.services.offer_service import OfferService
from app.services.trading_service import TradingService
from datetime import datetime


# ============================================================================
# IT-006: Verify trade execution integrates across all services
# ============================================================================
# Test Case ID: IT-006
# Objective: Verify that executing a trade properly updates offers, fractions,
#            and creates transaction records
# Description: Test the integration of TradingService with OfferService and
#             TransactionService, ensuring atomic operations
# Expected Result: Trade execution updates all related tables atomically
# ============================================================================

class TestTradingIntegration:
    """Integration tests for trading workflows"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Setup test data for trading"""
        with app.app_context():
            # Create users
            self.seller = User(
                user_name='seller_trade_test',
                email='seller@test.com',
                password='seller123',
                is_manager=False,
                created_at=datetime.utcnow()
            )
            self.buyer = User(
                user_name='buyer_trade_test',
                email='buyer@test.com',
                password='buyer123',
                is_manager=False,
                created_at=datetime.utcnow()
            )
            db.session.add_all([self.seller, self.buyer])
            db.session.commit()
            self.seller_id = self.seller.user_id
            self.buyer_id = self.buyer.user_id
            
            # Create asset
            self.asset = Asset(
                asset_name='test_trade_asset',
                total_unit=1000,
                unit_min=1,
                unit_max=500,
                total_value='100000.00',
                created_at=datetime.utcnow()
            )
            db.session.add(self.asset)
            db.session.commit()
            self.asset_id = self.asset.asset_id
            
            # Create fraction for seller
            self.seller_fraction = Fraction(
                asset_id=self.asset_id,
                owner_id=self.seller_id,
                units=200,
                is_active=True,
                value_perunit=100.00,
                created_at=datetime.utcnow()
            )
            db.session.add(self.seller_fraction)
            db.session.commit()
            self.seller_fraction_id = self.seller_fraction.fraction_id
        
        yield
        
        # Cleanup
        with app.app_context():
            # Delete in correct order (children before parents)
            Transaction.query.filter(
                (Transaction.from_owner_id == self.seller_id) |
                (Transaction.to_owner_id == self.buyer_id)
            ).delete(synchronize_session=False)
            Offer.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            AssetValueHistory.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            Fraction.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            Asset.query.filter_by(asset_id=self.asset_id).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.seller_id).delete(synchronize_session=False)
            User.query.filter_by(user_id=self.buyer_id).delete(synchronize_session=False)
            db.session.commit()
    
    def test_it006_trade_execution_updates_all_tables(self, app):
        """
        IT-006-A: Trade execution updates Offer, Fraction, and Transaction
        
        Steps:
        1. Create a sell offer from seller
        2. Execute trade (buyer accepts offer)
        3. Verify offer is deactivated
        4. Verify seller's fraction units reduced
        5. Verify buyer's fraction created
        6. Verify transaction record created
        7. Verify all data is consistent
        """
        # Arrange - Create sell offer
        with app.app_context():
            offer_data = {
                'asset_id': self.asset_id,
                'user_id': self.seller_id,
                'is_buyer': False,  # Sell offer
                'units': 50,
                'price_perunit': 105.00
            }
            offer = OfferService.create_offer(offer_data)
            offer_id = offer.offer_id
            
            # Act - Execute trade
            result = TradingService.execute_trade(
                offer_id=offer_id,
                counterparty_user_id=self.buyer_id
            )
            
            # Assert
            assert result['success'] is True
            assert result['trade_details']['units_traded'] == 50
            
            # Verify offer deactivated
            db_offer = db.session.get(Offer, offer_id)
            assert db_offer.is_valid is False
            
            # Verify seller's fraction reduced
            seller_fraction = db.session.get(Fraction, self.seller_fraction_id)
            assert seller_fraction.units == 150  # 200 - 50
            assert seller_fraction.is_active is True  # Still active (has units)
            
            # Verify buyer's fraction created
            buyer_fractions = Fraction.query.filter_by(
                asset_id=self.asset_id,
                owner_id=self.buyer_id
            ).all()
            assert len(buyer_fractions) == 1
            buyer_fraction = buyer_fractions[0]
            assert buyer_fraction.units == 50
            assert buyer_fraction.is_active is True
            assert float(buyer_fraction.value_perunit) == 105.00
            
            # Verify transaction created
            transactions = Transaction.query.filter_by(
                from_owner_id=self.seller_id,
                to_owner_id=self.buyer_id
            ).all()
            assert len(transactions) == 1
            transaction = transactions[0]
            assert transaction.unit_moved == 50
            assert transaction.transaction_type == 'trade'
            assert float(transaction.price_perunit) == 105.00
            assert transaction.offer_id == offer_id
    
    def test_it006_trade_validates_seller_has_units(self, app):
        """
        IT-006-B: Trade execution validates seller has enough units
        
        Steps:
        1. Create sell offer for more units than seller owns
        2. Verify offer creation fails OR
        3. If offer created, trade execution fails
        4. Verify no changes to fractions or transactions
        """
        # Arrange - Try to create sell offer for more units than available
        with app.app_context():
            offer_data = {
                'asset_id': self.asset_id,
                'user_id': self.seller_id,
                'is_buyer': False,
                'units': 300,  # Seller only has 200 units
                'price_perunit': 105.00
            }
            
            # Act & Assert
            with pytest.raises(ValueError, match="only has.*units available"):
                OfferService.create_offer(offer_data)
            
            # Verify no offer created
            offers = Offer.query.filter_by(
                asset_id=self.asset_id,
                user_id=self.seller_id,
                units=300
            ).all()
            assert len(offers) == 0
    
    def test_it006_cannot_trade_with_yourself(self, app):
        """
        IT-006-C: User cannot accept their own offer
        
        Steps:
        1. Create sell offer
        2. Try to execute trade with same user as counterparty
        3. Verify error is raised
        4. Verify no changes to database
        """
        # Arrange
        with app.app_context():
            offer_data = {
                'asset_id': self.asset_id,
                'user_id': self.seller_id,
                'is_buyer': False,
                'units': 50,
                'price_perunit': 105.00
            }
            offer = OfferService.create_offer(offer_data)
            offer_id = offer.offer_id
            
            # Act & Assert
            with pytest.raises(ValueError, match="Cannot trade with yourself"):
                TradingService.execute_trade(
                    offer_id=offer_id,
                    counterparty_user_id=self.seller_id  # Same user
                )
            
            # Verify offer still active
            db_offer = db.session.get(Offer, offer_id)
            assert db_offer.is_valid is True
            
            # Verify no transaction created
            transactions = Transaction.query.filter_by(
                from_owner_id=self.seller_id,
                to_owner_id=self.seller_id
            ).all()
            assert len(transactions) == 0

