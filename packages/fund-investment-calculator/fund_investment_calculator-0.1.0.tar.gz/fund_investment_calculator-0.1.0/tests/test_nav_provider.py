"""
NavProvider 测试
使用 pytest 框架
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
import pandas as pd
from src.nav_provider import NavProvider


class TestNavProvider:
    """NavProvider 测试类"""

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_get_basic(self, mock_ak):
        """测试基本获取净值功能"""
        # Mock 数据
        mock_df = pd.DataFrame({
            '净值日期': ['2024-01-15', '2024-01-16', '2024-01-17'],
            '单位净值': [1.5, 1.52, 1.51]
        })
        mock_ak.return_value = mock_df

        provider = NavProvider('000001')
        nav = provider.get(date(2024, 1, 16))

        assert nav == 1.52
        mock_ak.assert_called_once()

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_get_with_cache(self, mock_ak):
        """测试缓存功能"""
        # Mock 数据
        mock_df = pd.DataFrame({
            '净值日期': ['2024-01-15', '2024-01-16'],
            '单位净值': [1.5, 1.52]
        })
        mock_ak.return_value = mock_df

        provider = NavProvider('000001')

        # 第一次调用会触发 fetch
        nav1 = provider.get(date(2024, 1, 15))
        assert nav1 == 1.5
        assert mock_ak.call_count == 1

        # 第二次调用相同日期，应使用缓存
        nav2 = provider.get(date(2024, 1, 15))
        assert nav2 == 1.5
        assert mock_ak.call_count == 1  # 不应增加调用次数

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_get_date_not_found(self, mock_ak):
        """测试查询日期不存在"""
        # Mock 返回空数据
        mock_df = pd.DataFrame({
            '净值日期': ['2024-01-15'],
            '单位净值': [1.5]
        })
        mock_ak.return_value = mock_df

        provider = NavProvider('000001')

        with pytest.raises(ValueError, match="无法获取.*的净值数据"):
            provider.get(date(2024, 1, 20))

    @patch('src.nav_provider.date')
    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_get_latest_basic(self, mock_ak, mock_date):
        """测试获取最新净值"""
        # Mock 当前日期
        mock_date.today.return_value = date(2024, 1, 20)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # Mock 数据
        mock_df = pd.DataFrame({
            '净值日期': ['2024-01-15', '2024-01-16', '2024-01-17'],
            '单位净值': [1.5, 1.52, 1.51]
        })
        mock_ak.return_value = mock_df

        provider = NavProvider('000001')
        latest_date, latest_nav = provider.get_latest()

        assert latest_date == date(2024, 1, 17)
        assert latest_nav == 1.51

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_get_latest_with_cache(self, mock_ak):
        """测试 get_latest 使用缓存"""
        # Mock 数据
        mock_df = pd.DataFrame({
            '净值日期': ['2024-01-15', '2024-01-16'],
            '单位净值': [1.5, 1.52]
        })
        mock_ak.return_value = mock_df

        provider = NavProvider('000001')

        # 第一次调用会触发 fetch
        latest_date1, latest_nav1 = provider.get_latest()
        assert latest_date1 == date(2024, 1, 16)
        assert latest_nav1 == 1.52
        assert mock_ak.call_count == 1

        # 第二次调用应使用缓存，不再触发 fetch
        latest_date2, latest_nav2 = provider.get_latest()
        assert latest_date2 == date(2024, 1, 16)
        assert latest_nav2 == 1.52
        assert mock_ak.call_count == 1  # 仍然是1次

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_get_latest_empty_data(self, mock_ak):
        """测试 get_latest 无数据时抛出异常"""
        # Mock 返回空数据
        mock_ak.return_value = pd.DataFrame()

        provider = NavProvider('000001')

        with pytest.raises(RuntimeError, match="获取基金净值失败"):
            provider.get_latest()

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_fetch_error_handling(self, mock_ak):
        """测试 fetch 错误处理"""
        # Mock 抛出异常
        mock_ak.side_effect = Exception("网络错误")

        provider = NavProvider('000001')

        with pytest.raises(RuntimeError, match="获取基金净值失败"):
            provider.get(date(2024, 1, 15))

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_fetch_empty_dataframe(self, mock_ak):
        """测试返回空 DataFrame"""
        mock_ak.return_value = pd.DataFrame()

        provider = NavProvider('000001')

        with pytest.raises(RuntimeError, match="未获取到基金.*的净值数据"):
            provider.get(date(2024, 1, 15))

    @patch('src.nav_provider.ak.fund_open_fund_info_em')
    def test_multiple_funds(self, mock_ak):
        """测试不同基金代码"""
        # Mock 不同基金的数据
        def mock_response(symbol, indicator):
            if symbol == '000001':
                return pd.DataFrame({
                    '净值日期': ['2024-01-15'],
                    '单位净值': [1.5]
                })
            elif symbol == '000002':
                return pd.DataFrame({
                    '净值日期': ['2024-01-15'],
                    '单位净值': [2.0]
                })

        mock_ak.side_effect = mock_response

        provider1 = NavProvider('000001')
        provider2 = NavProvider('000002')

        nav1 = provider1.get(date(2024, 1, 15))
        nav2 = provider2.get(date(2024, 1, 15))

        assert nav1 == 1.5
        assert nav2 == 2.0
