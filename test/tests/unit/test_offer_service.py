"""
Complete unit tests for OfferService.
Tests are isolated and do not rely on external calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.offer_service import OfferService
from app.models import Offer, Fraction


class TestOfferService:
    """Test cases for OfferService."""
    
    # ==================== Create Offer Tests ====================
    
    def test_create_offer_buy_success(self):
        """Test successful buy offer creation."""
        offer_data = {
            'asset_id': 1,
            'user_id': 1,
            'is_buyer': True,
            'units': 100,
            'price_perunit': 50.00
        }
        
        with patch('app.services.offer_service.db') as mock_db:
            with patch('app.services.offer_service.Offer') as mock_offer_class:
                # Mock no existing offer
                mock_offer_class.query.filter_by.return_value.first.return_value = None
                
                # Mock offer creation
                mock_offer = Mock(spec=Offer)
                mock_offer_class.return_value = mock_offer
                
                result = OfferService.create_offer(offer_data)
                
                assert result == mock_offer
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
    
    def test_create_offer_sell_success(self):
        """Test successful sell offer creation with sufficient fractions."""
        offer_data = {
            'asset_id': 1,
            'user_id': 2,
            'is_buyer': False,
            'units': 50,
            'price_perunit': 55.00
        }
        
        with patch('app.services.offer_service.db') as mock_db:
            with patch('app.services.offer_service.Offer') as mock_offer_class:
                mock_offer_class.query.filter_by.return_value.first.return_value = None
                
                # Mock seller has enough fractions
                mock_db.session.query.return_value.filter.return_value.scalar.return_value = 100
                
                mock_offer = Mock(spec=Offer)
                mock_offer_class.return_value = mock_offer
                
                result = OfferService.create_offer(offer_data)
                
                assert result == mock_offer
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
    
    def test_create_offer_missing_required_field(self):
        """Test offer creation with missing required field."""
        offer_data = {
            'asset_id': 1,
            'user_id': 1,
            'is_buyer': True,
            'units': 100
            # Missing 'price_perunit'
        }
        
        with pytest.raises(ValueError, match="Missing required field: price_perunit"):
            OfferService.create_offer(offer_data)
    
    def test_create_offer_none_value(self):
        """Test offer creation with None value for required field."""
        offer_data = {
            'asset_id': 1,
            'user_id': 1,
            'is_buyer': True,
            'units': None,
            'price_perunit': 50.00
        }
        
        with pytest.raises(ValueError, match="Missing required field: units"):
            OfferService.create_offer(offer_data)
    
    def test_create_offer_duplicate_active_offer(self):
        """Test creating offer when user already has active offer for same asset."""
        offer_data = {
            'asset_id': 1,
            'user_id': 1,
            'is_buyer': True,
            'units': 100,
            'price_perunit': 50.00
        }
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            # Mock existing active offer
            mock_existing = Mock(spec=Offer)
            mock_offer_class.query.filter_by.return_value.first.return_value = mock_existing
            
            with pytest.raises(ValueError, match="User already has an active buy offer"):
                OfferService.create_offer(offer_data)
    
    def test_create_offer_sell_insufficient_fractions(self):
        """Test sell offer creation when seller doesn't have enough fractions."""
        offer_data = {
            'asset_id': 1,
            'user_id': 2,
            'is_buyer': False,
            'units': 100,
            'price_perunit': 55.00
        }
        
        with patch('app.services.offer_service.db') as mock_db:
            with patch('app.services.offer_service.Offer') as mock_offer_class:
                mock_offer_class.query.filter_by.return_value.first.return_value = None
                
                # Mock seller only has 50 units
                mock_db.session.query.return_value.filter.return_value.scalar.return_value = 50
                
                with pytest.raises(ValueError, match="Seller only has 50 units available"):
                    OfferService.create_offer(offer_data)
    
    
    # def test_create_offer_zero_price(self):
    #     """Test creating offer with zero price."""
    #     offer_data = {
    #         'asset_id': 1,
    #         'user_id': 1,
    #         'is_buyer': True,
    #         'units': 10,
    #         'price_perunit': 0.00
    #     }
        
    #     with pytest.raises(ValueError, match="Price per unit must be positive"):
    #         OfferService.create_offer(offer_data)
    
    # ==================== Get Offer Tests ====================
    
    def test_get_offer_by_id_success(self):
        """Test successful offer retrieval by ID."""
        offer_id = 1
        mock_offer = Mock(spec=Offer)
        mock_offer.offer_id = 1
        mock_offer.asset_id = 1
        mock_offer.user_id = 1
        mock_offer.is_buyer = True
        mock_offer.units = 100
        mock_offer.price_perunit = 50.00
        mock_offer.is_valid = True
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            result = OfferService.get_offer_by_id(offer_id)
            
            assert result == mock_offer
            mock_db.session.get.assert_called_once_with(Offer, offer_id)
    
    def test_get_offer_by_id_not_found(self):
        """Test offer retrieval with non-existent ID."""
        offer_id = 999
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = None
            
            result = OfferService.get_offer_by_id(offer_id)
            
            assert result is None
    
    def test_get_all_offers_active_only(self):
        """Test getting all active offers with pagination."""
        page = 1
        per_page = 20
        mock_offers = [Mock(spec=Offer), Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_paginate = Mock()
            mock_paginate.items = mock_offers
            mock_paginate.total = 2
            mock_paginate.page = 1
            mock_paginate.per_page = 20
            mock_paginate.pages = 1
            
            mock_query = Mock()
            mock_query.filter_by.return_value.order_by.return_value.paginate.return_value = mock_paginate
            mock_offer_class.query = mock_query
            
            result = OfferService.get_all_offers(page, per_page, active_only=True)
            
            assert result['offers'] == mock_offers
            assert result['total'] == 2
            mock_query.filter_by.assert_called_once_with(is_valid=True)
    
    def test_get_all_offers_include_inactive(self):
        """Test getting all offers including inactive ones."""
        page = 1
        per_page = 20
        mock_offers = [Mock(spec=Offer), Mock(spec=Offer), Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_paginate = Mock()
            mock_paginate.items = mock_offers
            mock_paginate.total = 3
            
            mock_query = Mock()
            mock_query.order_by.return_value.paginate.return_value = mock_paginate
            mock_offer_class.query = mock_query
            
            result = OfferService.get_all_offers(page, per_page, active_only=False)
            
            assert result['offers'] == mock_offers
            assert result['total'] == 3
    
    def test_get_offers_by_user_active_only(self):
        """Test getting user's active offers."""
        user_id = 1
        mock_offers = [Mock(spec=Offer), Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            mock_query.filter_by.return_value.filter_by.return_value.order_by.return_value.all.return_value = mock_offers
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_user(user_id, active_only=True)
            
            assert result == mock_offers
    
    def test_get_offers_by_user_all_offers(self):
        """Test getting all user's offers including inactive."""
        user_id = 1
        mock_offers = [Mock(spec=Offer), Mock(spec=Offer), Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            mock_query.filter_by.return_value.order_by.return_value.all.return_value = mock_offers
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_user(user_id, active_only=False)
            
            assert result == mock_offers
            assert len(result) == 3
    
    def test_get_offers_by_asset_all_types(self):
        """Test getting all offers for an asset."""
        asset_id = 1
        mock_offers = [Mock(spec=Offer), Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            mock_query.filter_by.return_value.filter_by.return_value.order_by.return_value.all.return_value = mock_offers
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_asset(asset_id, active_only=True, is_buyer=None)
            
            assert result == mock_offers
    
    def test_get_offers_by_asset_buy_only(self):
        """Test getting only buy offers for an asset."""
        asset_id = 1
        mock_buy_offers = [Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            filter_chain = mock_query.filter_by.return_value.filter_by.return_value.filter_by.return_value
            filter_chain.order_by.return_value.all.return_value = mock_buy_offers
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_asset(asset_id, active_only=True, is_buyer=True)
            
            assert result == mock_buy_offers
    
    def test_get_offers_by_asset_sell_only(self):
        """Test getting only sell offers for an asset."""
        asset_id = 1
        mock_sell_offers = [Mock(spec=Offer)]
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            filter_chain = mock_query.filter_by.return_value.filter_by.return_value.filter_by.return_value
            filter_chain.order_by.return_value.all.return_value = mock_sell_offers
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_asset(asset_id, active_only=True, is_buyer=False)
            
            assert result == mock_sell_offers
    
    def test_get_buy_offers(self):
        """Test getting only buy offers for an asset."""
        asset_id = 1
        mock_buy_offers = [Mock(spec=Offer)]
        
        with patch('app.services.offer_service.OfferService.get_offers_by_asset') as mock_get:
            mock_get.return_value = mock_buy_offers
            
            result = OfferService.get_buy_offers(asset_id)
            
            assert result == mock_buy_offers
            mock_get.assert_called_once_with(asset_id, True, is_buyer=True)
    
    def test_get_sell_offers(self):
        """Test getting only sell offers for an asset."""
        asset_id = 1
        mock_sell_offers = [Mock(spec=Offer)]
        
        with patch('app.services.offer_service.OfferService.get_offers_by_asset') as mock_get:
            mock_get.return_value = mock_sell_offers
            
            result = OfferService.get_sell_offers(asset_id)
            
            assert result == mock_sell_offers
            mock_get.assert_called_once_with(asset_id, True, is_buyer=False)
    
    # ==================== Update Offer Tests ====================
    
    def test_update_offer_success(self):
        """Test successful offer update."""
        offer_id = 1
        offer_data = {'units': 150, 'price_perunit': 52.00}
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = True
        mock_offer.is_buyer = True
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            result = OfferService.update_offer(offer_id, offer_data)
            
            assert result == mock_offer
            assert mock_offer.units == 150
            assert mock_offer.price_perunit == 52.00
            mock_db.session.commit.assert_called_once()
    
    def test_update_offer_not_found(self):
        """Test offer update with non-existent ID."""
        offer_id = 999
        offer_data = {'units': 150}
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = None
            
            result = OfferService.update_offer(offer_id, offer_data)
            
            assert result is None
    
    def test_update_offer_inactive_offer(self):
        """Test updating an inactive offer."""
        offer_id = 1
        offer_data = {'units': 150}
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = False
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with pytest.raises(ValueError, match="Cannot update an inactive offer"):
                OfferService.update_offer(offer_id, offer_data)
    
    def test_update_sell_offer_insufficient_fractions(self):
        """Test updating sell offer when seller doesn't have enough fractions."""
        offer_id = 1
        offer_data = {'units': 200}
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = True
        mock_offer.is_buyer = False
        mock_offer.asset_id = 1
        mock_offer.user_id = 2
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            # Mock seller only has 100 units
            mock_db.session.query.return_value.filter.return_value.scalar.return_value = 100
            
            with pytest.raises(ValueError, match="Seller only has 100 units available"):
                OfferService.update_offer(offer_id, offer_data)
    
    def test_update_offer_only_price(self):
        """Test updating only price of an offer."""
        offer_id = 1
        offer_data = {'price_perunit': 60.00}
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = True
        mock_offer.is_buyer = True
        mock_offer.units = 100  # Original units
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            result = OfferService.update_offer(offer_id, offer_data)
            
            assert result == mock_offer
            assert mock_offer.price_perunit == 60.00
            assert mock_offer.units == 100  # Should remain unchanged
    
    # def test_update_offer_negative_units(self):
    #     """Test updating offer with negative units."""
    #     offer_id = 1
    #     offer_data = {'units': -50}
    #     mock_offer = Mock(spec=Offer)
    #     mock_offer.is_valid = True
    #     mock_offer.is_buyer = True
        
    #     with patch('app.services.offer_service.db') as mock_db:
    #         mock_db.session.get.return_value = mock_offer
            
    #         with pytest.raises(ValueError, match="Units must be positive"):
    #             OfferService.update_offer(offer_id, offer_data)
    
    # def test_update_offer_zero_price(self):
    #     """Test updating offer with zero price."""
    #     offer_id = 1
    #     offer_data = {'price_perunit': 0.00}
    #     mock_offer = Mock(spec=Offer)
    #     mock_offer.is_valid = True
    #     mock_offer.is_buyer = True
        
    #     with patch('app.services.offer_service.db') as mock_db:
    #         mock_db.session.get.return_value = mock_offer
            
    #         with pytest.raises(ValueError, match="Price per unit must be positive"):
    #             OfferService.update_offer(offer_id, offer_data)
    
    # ==================== Delete Offer Tests ====================
    
    def test_delete_offer_success(self):
        """Test successful offer deletion (deactivation)."""
        offer_id = 1
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = True
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            result = OfferService.delete_offer(offer_id)
            
            assert result['success'] is True
            assert mock_offer.is_valid is False
            mock_db.session.commit.assert_called_once()
    
    def test_delete_offer_not_found(self):
        """Test offer deletion with non-existent ID."""
        offer_id = 999
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = None
            
            result = OfferService.delete_offer(offer_id)
            
            assert result['success'] is False
            assert 'message' in result
    
    def test_delete_offer_already_inactive(self):
        """Test deleting an already inactive offer."""
        offer_id = 1
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = False
        
        with patch('app.services.offer_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            result = OfferService.delete_offer(offer_id)
            
            assert result['success'] is False
            assert 'already inactive' in result['message'].lower()
    
    # ==================== Edge Cases ====================
    
    def test_create_offer_empty_data(self):
        """Test creating offer with empty data."""
        offer_data = {}
        
        with pytest.raises(ValueError, match="Missing required field"):
            OfferService.create_offer(offer_data)
    
    def test_get_offers_by_user_no_offers(self):
        """Test getting offers for user with no offers."""
        user_id = 999
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_user(user_id, active_only=False)
            
            assert result == []
    
    def test_get_offers_by_asset_no_offers(self):
        """Test getting offers for asset with no offers."""
        asset_id = 999
        
        with patch('app.services.offer_service.Offer') as mock_offer_class:
            mock_query = Mock()
            mock_query.filter_by.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
            mock_offer_class.query = mock_query
            
            result = OfferService.get_offers_by_asset(asset_id, active_only=True)
            
            assert result == []