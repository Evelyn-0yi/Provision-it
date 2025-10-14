"""
Unit tests for PortfolioService.user_owning_fractions (owning fractions display).
Tests are isolated and do not rely on real DB; everything is mocked.
"""

from types import SimpleNamespace
from unittest.mock import Mock, patch
from app.services.portfolio_service import PortfolioService


class TestPortfolioOwningFractions:
    def test_user_owning_fractions_success(self):
        """
        The user holds two assets; two records containing asset_id/asset_name/units/latest_value/estimated_value should be returned.
If there is no historical price, the latest_value will fall back to Asset.total_value.
        """
        user_id = 42

        # mock: aggregate query rows（sum units by asset_id）
        rows = [
            SimpleNamespace(asset_id=1, units=30),
            SimpleNamespace(asset_id=2, units=10),
        ]

        # mock: Asset information (for name & fallback value when no price history)
        asset1 = Mock()
        asset1.asset_id = 1
        asset1.asset_name = "Modern Art Painting"
        asset1.total_value = "500"  

        asset2 = Mock()
        asset2.asset_id = 2
        asset2.asset_name = "Technology Equity Fund A"
        asset2.total_value = "2000"

        # mock: price history (return None here to let the code fallback to total_value)

        with patch("app.services.portfolio_service.db") as mock_db, \
             patch("app.services.portfolio_service.Asset") as mock_asset_cls, \
             patch("app.services.portfolio_service.AssetValueHistory") as mock_hist_cls, \
             patch("app.services.portfolio_service.Fraction") as mock_fraction_cls:

            # db.session.query(...).filter(...).group_by(...).all() -> rows
            q = Mock()
            mock_db.session.query.return_value = q
            q.filter.return_value = q
            q.group_by.return_value = q
            q.all.return_value = rows

            # Asset.query.filter(Asset.asset_id.in_(...)).all() -> [asset1, asset2]
            mock_asset_query = Mock()
            mock_asset_cls.query = mock_asset_query
            mock_asset_query.filter.return_value.all.return_value = [asset1, asset2]

            # AssetValueHistory.query.filter(...).order_by(...).first() -> None（无历史价）
            mock_hist_query = Mock()
            mock_hist_cls.query = mock_hist_query
            mock_hist_query.filter.return_value.order_by.return_value.first.return_value = None

            result = PortfolioService.user_owning_fractions(user_id)

            assert isinstance(result, list) and len(result) == 2

            r1 = result[0]
            assert r1["asset_id"] == 1
            assert r1["asset_name"] == "Modern Art Painting"
            assert r1["units"] == 30
            assert r1["latest_value"] == 500.0
            assert r1["estimated_value"] == 30 * 500.0

            r2 = result[1]
            assert r2["asset_id"] == 2
            assert r2["asset_name"] == "Technology Equity Fund A"
            assert r2["units"] == 10
            assert r2["latest_value"] == 2000.0
            assert r2["estimated_value"] == 10 * 2000.0

           
            mock_db.session.query.assert_called_once()
            assert q.filter.called and q.group_by.called and q.all.called
            assert mock_asset_query.filter.called

    def test_user_owning_fractions_empty(self):
        """The user has no shares: an empty list should be returned."""
        user_id = 7
        with patch("app.services.portfolio_service.db") as mock_db, \
             patch("app.services.portfolio_service.Fraction") as mock_fraction_cls:

            q = Mock()
            mock_db.session.query.return_value = q
            q.filter.return_value = q
            q.group_by.return_value = q
            q.all.return_value = []  

            result = PortfolioService.user_owning_fractions(user_id)
            assert result == []
