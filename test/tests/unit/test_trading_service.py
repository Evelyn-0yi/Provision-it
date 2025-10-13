"""
Unit tests for TradingService.
Tests are isolated and do not rely on external calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from app.services.trading_service import TradingService
from app.models import Offer, Fraction, Transaction


class TestTradingService:
    """Test cases for TradingService."""
    
    def test_execute_trade_buy_offer_success(self):
        """Test successful trade execution on a buy offer (counterparty sells)."""
        offer_id = 1
        counterparty_user_id = 2
        
        # Mock buy offer
        mock_offer = Mock(spec=Offer)
        mock_offer.offer_id = offer_id
        mock_offer.user_id = 1  # Buyer
        mock_offer.is_valid = True
        mock_offer.is_buyer = True
        mock_offer.asset_id = 1
        mock_offer.units = 50
        mock_offer.price_perunit = 100.0
        
        # Mock seller's fractions
        mock_fraction = Mock(spec=Fraction)
        mock_fraction.fraction_id = 1
        mock_fraction.units = 100
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with patch('app.services.trading_service.Fraction') as mock_fraction_class:
                mock_fraction_class.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_fraction]
                
                with patch('app.services.trading_service.TradingService._process_fractions_and_transactions') as mock_process:
                    mock_process.return_value = {
                        'success': True,
                        'message': 'Trade executed successfully',
                        'trade_details': {
                            'offer_id': offer_id,
                            'units_traded': 50,
                            'price_perunit': 100.0,
                            'total_value': 5000.0
                        }
                    }
                    
                    result = TradingService.execute_trade(offer_id, counterparty_user_id)
                    
                    assert result['success'] is True
                    assert mock_offer.is_valid is False
                    mock_process.assert_called_once()
    
    def test_execute_trade_sell_offer_success(self):
        """Test successful trade execution on a sell offer (counterparty buys)."""
        offer_id = 1
        counterparty_user_id = 2
        
        # Mock sell offer
        mock_offer = Mock(spec=Offer)
        mock_offer.offer_id = offer_id
        mock_offer.user_id = 1  # Seller
        mock_offer.is_valid = True
        mock_offer.is_buyer = False
        mock_offer.asset_id = 1
        mock_offer.units = 50  # 明确设置为整数
        mock_offer.price_perunit = 100.0
        
        # Mock seller's fractions
        mock_fraction = Mock(spec=Fraction)
        mock_fraction.fraction_id = 1
        mock_fraction.units = 100  # 明确设置为整数
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with patch('app.services.trading_service.Fraction') as mock_fraction_class:
                mock_fraction_class.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_fraction]
                
                with patch('app.services.trading_service.TradingService._process_fractions_and_transactions') as mock_process:
                    mock_process.return_value = {
                        'success': True,
                        'message': 'Trade executed successfully',
                        'trade_details': {}
                    }
                    
                    result = TradingService.execute_trade(offer_id, counterparty_user_id)
                    
                    assert result['success'] is True
                    assert mock_offer.is_valid is False
    
    def test_execute_trade_offer_not_found(self):
        """Test trade execution with non-existent offer."""
        offer_id = 999
        counterparty_user_id = 2
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = None
            
            with pytest.raises(ValueError, match="Offer not found"):
                TradingService.execute_trade(offer_id, counterparty_user_id)
    
    def test_execute_trade_inactive_offer(self):
        """Test trade execution on inactive offer."""
        offer_id = 1
        counterparty_user_id = 2
        
        mock_offer = Mock(spec=Offer)
        mock_offer.is_valid = False
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with pytest.raises(ValueError, match="Offer is not active"):
                TradingService.execute_trade(offer_id, counterparty_user_id)
    
    def test_execute_trade_self_trading(self):
        """Test trade execution when user tries to trade with themselves."""
        offer_id = 1
        counterparty_user_id = 1  # Same as offer creator
        
        mock_offer = Mock(spec=Offer)
        mock_offer.user_id = 1
        mock_offer.is_valid = True
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with pytest.raises(ValueError, match="Cannot trade with yourself"):
                TradingService.execute_trade(offer_id, counterparty_user_id)
    
    def test_execute_trade_insufficient_seller_fractions(self):
        """Test trade execution when seller doesn't have enough fractions."""
        offer_id = 1
        counterparty_user_id = 2
        
        mock_offer = Mock(spec=Offer)
        mock_offer.user_id = 1
        mock_offer.is_valid = True
        mock_offer.is_buyer = False
        mock_offer.asset_id = 1
        mock_offer.units = 100  # 明确设置为整数
        
        # Mock seller only has 50 units
        mock_fraction = Mock(spec=Fraction)
        mock_fraction.units = 50  # 明确设置为整数
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with patch('app.services.trading_service.Fraction') as mock_fraction_class:
                mock_fraction_class.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_fraction]
                
                with pytest.raises(ValueError, match="Seller only has 50 units available"):
                    TradingService.execute_trade(offer_id, counterparty_user_id)
    
    def test_process_fractions_single_fraction(self):
        """Test fraction processing when trade uses single fraction."""
        mock_offer = Mock(spec=Offer)
        mock_offer.offer_id = 1
        mock_offer.asset_id = 1
        mock_offer.units = 50
        mock_offer.price_perunit = 100.0
        mock_offer.is_buyer = True
        
        buyer_id = 1
        seller_id = 2
        
        mock_fraction = Mock(spec=Fraction)
        mock_fraction.fraction_id = 1
        mock_fraction.units = 100
        mock_fraction.is_active = True  # 明确设置初始状态
        
        with patch('app.services.trading_service.db') as mock_db:
            with patch('app.services.trading_service.Fraction') as mock_fraction_class:
                mock_new_fraction = Mock()
                mock_new_fraction.fraction_id = 2
                mock_fraction_class.return_value = mock_new_fraction
                
                with patch('app.services.trading_service.Transaction') as mock_transaction_class:
                    result = TradingService._process_fractions_and_transactions(
                        mock_offer, buyer_id, seller_id, [mock_fraction]
                    )
                    
                    assert result['success'] is True
                    assert result['trade_details']['units_traded'] == 50
                    assert result['trade_details']['total_value'] == 5000.0
                    
                    # Check fraction was updated
                    assert mock_fraction.units == 50
                    assert mock_fraction.is_active is True
                    
                    # Check new fraction and transaction were created
                    mock_db.session.add.assert_called()
                    mock_db.session.commit.assert_called_once()
    
    def test_process_fractions_multiple_fractions(self):
        """Test fraction processing when trade spans multiple fractions."""
        mock_offer = Mock(spec=Offer)
        mock_offer.offer_id = 1
        mock_offer.asset_id = 1
        mock_offer.units = 150
        mock_offer.price_perunit = 100.0
        mock_offer.is_buyer = True
        
        buyer_id = 1
        seller_id = 2
        
        # Seller has two fractions
        mock_fraction1 = Mock(spec=Fraction)
        mock_fraction1.fraction_id = 1
        mock_fraction1.units = 100
        
        mock_fraction2 = Mock(spec=Fraction)
        mock_fraction2.fraction_id = 2
        mock_fraction2.units = 80
        
        with patch('app.services.trading_service.db') as mock_db:
            with patch('app.services.trading_service.Fraction') as mock_fraction_class:
                mock_new_fractions = [Mock(), Mock()]
                mock_fraction_class.side_effect = mock_new_fractions
                
                with patch('app.services.trading_service.Transaction'):
                    result = TradingService._process_fractions_and_transactions(
                        mock_offer, buyer_id, seller_id, [mock_fraction1, mock_fraction2]
                    )
                    
                    assert result['success'] is True
                    assert result['trade_details']['units_traded'] == 150
                    
                    # Check first fraction depleted
                    assert mock_fraction1.units == 0
                    assert mock_fraction1.is_active is False
                    
                    # Check second fraction partially used
                    assert mock_fraction2.units == 30
    
    def test_get_asset_offers_success(self):
        """Test getting all offers for an asset."""
        asset_id = 1
        
        # Mock buy offers
        mock_buy_offer = Mock(spec=Offer)
        mock_buy_offer.offer_id = 1
        mock_buy_offer.user_id = 1
        mock_buy_offer.units = 50
        mock_buy_offer.price_perunit = 105.0
        mock_buy_offer.create_at = datetime(2025, 1, 1)
        
        # Mock sell offers
        mock_sell_offer = Mock(spec=Offer)
        mock_sell_offer.offer_id = 2
        mock_sell_offer.user_id = 2
        mock_sell_offer.units = 30
        mock_sell_offer.price_perunit = 110.0
        mock_sell_offer.create_at = datetime(2025, 1, 2)
        
        with patch('app.services.trading_service.Offer') as mock_offer_class:
            def mock_filter_by(**kwargs):
                mock_query = Mock()
                if kwargs.get('is_buyer'):
                    mock_query.order_by.return_value.all.return_value = [mock_buy_offer]
                else:
                    mock_query.order_by.return_value.all.return_value = [mock_sell_offer]
                return mock_query
            
            mock_offer_class.query.filter_by = mock_filter_by
            
            result = TradingService.get_asset_offers(asset_id)
            
            assert result['asset_id'] == asset_id
            assert result['buy_count'] == 1
            assert result['sell_count'] == 1
            assert len(result['buy_offers']) == 1
            assert len(result['sell_offers']) == 1
            assert result['buy_offers'][0]['offer_id'] == 1
            assert result['sell_offers'][0]['offer_id'] == 2
    
    def test_get_asset_offers_no_offers(self):
        """Test getting offers when none exist for asset."""
        asset_id = 999
        
        with patch('app.services.trading_service.Offer') as mock_offer_class:
            mock_query = Mock()
            mock_query.order_by.return_value.all.return_value = []
            mock_offer_class.query.filter_by.return_value = mock_query
            
            result = TradingService.get_asset_offers(asset_id)
            
            assert result['buy_count'] == 0
            assert result['sell_count'] == 0
            assert result['buy_offers'] == []
            assert result['sell_offers'] == []
    
    def test_execute_trade_rollback_on_error(self):
        """Test that transaction is rolled back on error."""
        offer_id = 1
        counterparty_user_id = 2
        
        mock_offer = Mock(spec=Offer)
        mock_offer.user_id = 1
        mock_offer.is_valid = True
        mock_offer.is_buyer = True
        mock_offer.asset_id = 1
        mock_offer.units = 50  # 明确设置为整数
        
        mock_fraction = Mock(spec=Fraction)
        mock_fraction.units = 100  # 明确设置为整数
        
        with patch('app.services.trading_service.db') as mock_db:
            mock_db.session.get.return_value = mock_offer
            
            with patch('app.services.trading_service.Fraction') as mock_fraction_class:
                mock_fraction_class.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_fraction]
                
                with patch('app.services.trading_service.TradingService._process_fractions_and_transactions') as mock_process:
                    mock_process.side_effect = Exception("Database error")
                    
                    with pytest.raises(ValueError, match="Trade execution failed"):
                        TradingService.execute_trade(offer_id, counterparty_user_id)
                    
                    mock_db.session.rollback.assert_called_once()