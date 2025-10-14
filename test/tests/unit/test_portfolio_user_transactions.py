"""
Unit tests for PortfolioService.user_transactions (transaction history display).
Tests mock the SQLAlchemy query chain including join/filter/order_by/paginate.
"""

from unittest.mock import Mock, patch
from app.services.portfolio_service import PortfolioService


class TestPortfolioUserTransactions:
    def test_user_transactions_basic(self):
        """基本返回：按时间倒序，分页对象包含 items 与 total。"""
        user_id = 10
        fake_items = [Mock(), Mock()]

        with patch("app.services.portfolio_service.db") as mock_db, \
             patch("app.services.portfolio_service.Transaction") as mock_tx_cls, \
             patch("app.services.portfolio_service.Fraction") as mock_frac_cls:

            q = Mock()
            mock_db.session.query.return_value = q
            q.join.return_value = q
            q.filter.return_value = q
            q.order_by.return_value = q

            # paginate 返回一个带 items/total 的对象
            pagination = Mock()
            pagination.items = fake_items
            pagination.total = 2
            q.paginate.return_value = pagination

            items, total = PortfolioService.user_transactions(user_id=user_id, page=1, per_page=20)

            assert items == fake_items
            assert total == 2
            # 断言链路
            mock_db.session.query.assert_called_once()
            assert q.join.called and q.filter.called and q.order_by.called
            q.paginate.assert_called_once_with(page=1, per_page=20, error_out=False)

    def test_user_transactions_with_asset_filter(self):
        """带 asset_id 过滤应仍能正确返回分页结果。"""
        user_id = 10
        asset_id = 2
        fake_items = [Mock()]

        with patch("app.services.portfolio_service.db") as mock_db, \
             patch("app.services.portfolio_service.Transaction") as mock_tx_cls, \
             patch("app.services.portfolio_service.Fraction") as mock_frac_cls:

            q = Mock()
            mock_db.session.query.return_value = q
            q.join.return_value = q
            q.filter.return_value = q
            q.order_by.return_value = q

            pagination = Mock()
            pagination.items = fake_items
            pagination.total = 1
            q.paginate.return_value = pagination

            items, total = PortfolioService.user_transactions(
                user_id=user_id, asset_id=asset_id, page=2, per_page=5
            )

            assert items == fake_items and total == 1
            q.paginate.assert_called_once_with(page=2, per_page=5, error_out=False)

    def test_user_transactions_empty(self):
        """分页 items 为空时应返回空列表与 0 总数（或真实 total 值）。"""
        user_id = 99

        with patch("app.services.portfolio_service.db") as mock_db, \
             patch("app.services.portfolio_service.Transaction") as mock_tx_cls, \
             patch("app.services.portfolio_service.Fraction") as mock_frac_cls:

            q = Mock()
            mock_db.session.query.return_value = q
            q.join.return_value = q
            q.filter.return_value = q
            q.order_by.return_value = q

            pagination = Mock()
            pagination.items = []
            pagination.total = 0
            q.paginate.return_value = pagination

            items, total = PortfolioService.user_transactions(user_id=user_id)
            assert items == [] and total == 0
