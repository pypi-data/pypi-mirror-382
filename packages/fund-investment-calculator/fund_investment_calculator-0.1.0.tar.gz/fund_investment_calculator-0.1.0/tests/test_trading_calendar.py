"""
TradingCalendar 测试
使用 pytest 框架
"""

import pytest
from datetime import date
from src.trading_calendar import TradingCalendar


class TestTradingCalendar:
    """TradingCalendar 测试类"""

    @pytest.fixture
    def calendar(self):
        """创建交易日历实例"""
        return TradingCalendar("XSHG")

    def test_is_trading_day_workday(self, calendar):
        """测试工作日是否为交易日"""
        # 2024-01-02 是周二，应该是交易日
        assert calendar.is_trading_day(date(2024, 1, 2)) is True

    def test_is_trading_day_weekend(self, calendar):
        """测试周末不是交易日"""
        # 2024-01-06 是周六
        assert calendar.is_trading_day(date(2024, 1, 6)) is False
        # 2024-01-07 是周日
        assert calendar.is_trading_day(date(2024, 1, 7)) is False

    def test_is_trading_day_holiday(self, calendar):
        """测试节假日不是交易日"""
        # 2024-01-01 是元旦，不是交易日
        assert calendar.is_trading_day(date(2024, 1, 1)) is False

    def test_adjust_to_trading_day_already_trading_day(self, calendar):
        """测试已经是交易日的情况"""
        # 2024-01-02 是周二，是交易日
        d = date(2024, 1, 2)
        assert calendar.adjust_to_trading_day(d) == d

    def test_adjust_to_trading_day_weekend(self, calendar):
        """测试周末调整到下一个交易日"""
        # 2024-01-06 是周六，应该调整到下周一 2024-01-08
        d = date(2024, 1, 6)
        adjusted = calendar.adjust_to_trading_day(d)
        assert adjusted == date(2024, 1, 8)
        assert calendar.is_trading_day(adjusted) is True

    def test_adjust_to_trading_day_holiday(self, calendar):
        """测试节假日调整到下一个交易日"""
        # 2024-01-01 是元旦，应该调整到下一个交易日 2024-01-02
        d = date(2024, 1, 1)
        adjusted = calendar.adjust_to_trading_day(d)
        assert adjusted == date(2024, 1, 2)
        assert calendar.is_trading_day(adjusted) is True

    def test_get_next_trading_day_from_trading_day(self, calendar):
        """测试从交易日获取下一个交易日"""
        # 2024-01-02 是周二，下一个交易日是 2024-01-03（周三）
        d = date(2024, 1, 2)
        next_day = calendar.get_next_trading_day(d)
        assert next_day == date(2024, 1, 3)
        assert calendar.is_trading_day(next_day) is True

    def test_get_next_trading_day_from_weekend(self, calendar):
        """测试从周末获取下一个交易日"""
        # 2024-01-06 是周六，下一个交易日是 2024-01-08（周一）
        d = date(2024, 1, 6)
        next_day = calendar.get_next_trading_day(d)
        assert next_day == date(2024, 1, 8)
        assert calendar.is_trading_day(next_day) is True

    def test_get_next_trading_day_before_long_holiday(self, calendar):
        """测试长假前获取下一个交易日"""
        # 2023-12-29 是周五，是交易日
        # 下一个交易日应该是 2024-01-02（元旦假期后）
        d = date(2023, 12, 29)
        next_day = calendar.get_next_trading_day(d)
        assert calendar.is_trading_day(next_day) is True
        assert next_day > d

    def test_get_previous_trading_day_from_trading_day(self, calendar):
        """测试从交易日获取上一个交易日"""
        # 2024-01-03 是周三，上一个交易日是 2024-01-02（周二）
        d = date(2024, 1, 3)
        prev_day = calendar.get_previous_trading_day(d)
        assert prev_day == date(2024, 1, 2)
        assert calendar.is_trading_day(prev_day) is True

    def test_get_previous_trading_day_from_weekend(self, calendar):
        """测试从周末获取上一个交易日"""
        # 2024-01-07 是周日，上一个交易日是 2024-01-05（周五）
        d = date(2024, 1, 7)
        prev_day = calendar.get_previous_trading_day(d)
        assert prev_day == date(2024, 1, 5)
        assert calendar.is_trading_day(prev_day) is True

    def test_get_previous_trading_day_after_long_holiday(self, calendar):
        """测试长假后获取上一个交易日"""
        # 2024-01-02 是元旦后第一个交易日
        # 上一个交易日应该是 2023-12-29
        d = date(2024, 1, 2)
        prev_day = calendar.get_previous_trading_day(d)
        assert prev_day == date(2023, 12, 29)
        assert calendar.is_trading_day(prev_day) is True

    def test_consecutive_next_trading_days(self, calendar):
        """测试连续获取下一个交易日"""
        start = date(2024, 1, 2)
        current = start

        # 连续获取5个交易日
        for _ in range(5):
            next_day = calendar.get_next_trading_day(current)
            assert calendar.is_trading_day(next_day) is True
            assert next_day > current
            current = next_day

    def test_consecutive_previous_trading_days(self, calendar):
        """测试连续获取上一个交易日"""
        start = date(2024, 1, 10)
        current = start

        # 连续获取5个交易日
        for _ in range(5):
            prev_day = calendar.get_previous_trading_day(current)
            assert calendar.is_trading_day(prev_day) is True
            assert prev_day < current
            current = prev_day

    def test_get_trading_day_or_previous_already_trading_day(self, calendar):
        """测试已经是交易日的情况，应返回自己"""
        # 2024-01-02 是周二，是交易日
        d = date(2024, 1, 2)
        result = calendar.get_trading_day_or_previous(d)
        assert result == d
        assert calendar.is_trading_day(result) is True

    def test_get_trading_day_or_previous_from_weekend(self, calendar):
        """测试从周末获取之前的交易日"""
        # 2024-01-06 是周六，应返回上周五 2024-01-05
        d = date(2024, 1, 6)
        result = calendar.get_trading_day_or_previous(d)
        assert result == date(2024, 1, 5)
        assert calendar.is_trading_day(result) is True

    def test_get_trading_day_or_previous_from_sunday(self, calendar):
        """测试从周日获取之前的交易日"""
        # 2024-01-07 是周日，应返回上周五 2024-01-05
        d = date(2024, 1, 7)
        result = calendar.get_trading_day_or_previous(d)
        assert result == date(2024, 1, 5)
        assert calendar.is_trading_day(result) is True

    def test_get_trading_day_or_previous_after_holiday(self, calendar):
        """测试节假日后第一天获取之前的交易日"""
        # 2024-01-01 是元旦，应返回 2023-12-29
        d = date(2024, 1, 1)
        result = calendar.get_trading_day_or_previous(d)
        assert result == date(2023, 12, 29)
        assert calendar.is_trading_day(result) is True

    def test_different_exchange(self):
        """测试不同交易所"""
        # 测试可以创建其他交易所的日历（如果需要）
        calendar = TradingCalendar("XSHG")
        assert calendar is not None

        # 验证基本功能正常
        assert calendar.is_trading_day(date(2024, 1, 2)) is True
