"""
RegularInvestmentScheduler 测试
使用 pytest 框架
"""

import pytest
from datetime import date, timedelta
from src.scheduler import RegularInvestmentScheduler


class TestRegularInvestmentScheduler:
    """RegularInvestmentScheduler 测试类"""

    def test_monthly_basic(self):
        """测试基本月度定投"""
        regular_rule = {
            "start_date": date(2024, 1, 15),
            "interval": "monthly",
            "day": 15
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 3, 31))

        expected = {
            date(2024, 1, 15),
            date(2024, 2, 15),
            date(2024, 3, 15)
        }
        assert dates == expected

    def test_monthly_with_skip_dates(self):
        """测试月度定投跳过指定日期"""
        regular_rule = {
            "start_date": date(2024, 1, 15),
            "interval": "monthly",
            "day": 15
        }
        skip_dates = {date(2024, 2, 15)}

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 3, 31))

        expected = {
            date(2024, 1, 15),
            date(2024, 3, 15)
        }
        assert dates == expected

    def test_monthly_end_of_month(self):
        """测试月末日期处理（如31号在2月不存在）"""
        regular_rule = {
            "start_date": date(2024, 1, 31),
            "interval": "monthly",
            "day": 31
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 4, 30))

        # 2月29日（2024是闰年），3月31日，4月30日
        expected = {
            date(2024, 1, 31),
            date(2024, 2, 29),  # 2024年是闰年
            date(2024, 3, 31),
            date(2024, 4, 30)   # 4月只有30天
        }
        assert dates == expected

    def test_monthly_cross_year(self):
        """测试跨年月度定投"""
        regular_rule = {
            "start_date": date(2023, 11, 10),
            "interval": "monthly",
            "day": 10
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 2, 15))

        expected = {
            date(2023, 11, 10),
            date(2023, 12, 10),
            date(2024, 1, 10),
            date(2024, 2, 10)
        }
        assert dates == expected

    def test_weekly_basic(self):
        """测试基本周定投"""
        regular_rule = {
            "start_date": date(2024, 1, 1),  # 2024-1-1 是周一
            "interval": "weekly",
            "weekday": 4  # 周五
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 1, 31))

        # 1月的所有周五
        expected = {
            date(2024, 1, 5),
            date(2024, 1, 12),
            date(2024, 1, 19),
            date(2024, 1, 26)
        }
        assert dates == expected

    def test_biweekly_basic(self):
        """测试双周定投"""
        regular_rule = {
            "start_date": date(2024, 1, 1),  # 周一
            "interval": "biweekly",
            "weekday": 0  # 周一
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 2, 29))

        # 每隔两周的周一
        expected = {
            date(2024, 1, 1),
            date(2024, 1, 15),
            date(2024, 1, 29),
            date(2024, 2, 12),
            date(2024, 2, 26)
        }
        assert dates == expected

    def test_with_trading_day_adjustment(self):
        """测试交易日调整"""
        regular_rule = {
            "start_date": date(2024, 1, 15),
            "interval": "monthly",
            "day": 15
        }
        skip_dates = set()

        # 模拟交易日调整：如果是周末则顺延到下周一
        def mock_adjust(d):
            if d.weekday() == 5:  # 周六
                return d + timedelta(days=2)
            elif d.weekday() == 6:  # 周日
                return d + timedelta(days=1)
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)

        # 假设某个15号是周六
        test_date = date(2024, 6, 15)  # 2024-6-15 是周六
        regular_rule["start_date"] = test_date
        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2024, 6, 30))

        # 应该调整到6月17日（周一）
        expected = {date(2024, 6, 17)}
        assert dates == expected

    def test_empty_rule(self):
        """测试空规则"""
        regular_rule = {}
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates()

        assert dates == set()

    def test_missing_start_date(self):
        """测试缺少 start_date"""
        regular_rule = {
            "interval": "monthly",
            "day": 15
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)

        with pytest.raises(ValueError, match="必须包含 start_date"):
            scheduler.generate_dates()

    def test_monthly_missing_day(self):
        """测试月度定投缺少 day 参数"""
        regular_rule = {
            "start_date": date(2024, 1, 15),
            "interval": "monthly"
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)

        with pytest.raises(ValueError, match="必须指定 day 参数"):
            scheduler.generate_dates()

    def test_weekly_missing_weekday(self):
        """测试周定投缺少 weekday 参数"""
        regular_rule = {
            "start_date": date(2024, 1, 1),
            "interval": "weekly"
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)

        with pytest.raises(ValueError, match="必须指定 weekday 参数"):
            scheduler.generate_dates()

    def test_invalid_interval(self):
        """测试不支持的间隔类型"""
        regular_rule = {
            "start_date": date(2024, 1, 1),
            "interval": "daily"
        }
        skip_dates = set()

        def mock_adjust(d):
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)

        with pytest.raises(ValueError, match="不支持的间隔类型"):
            scheduler.generate_dates()

    def test_adjusted_date_exceeds_end_date(self):
        """测试交易日调整后超过截止日期的情况"""
        regular_rule = {
            "start_date": date(2025, 9, 6),
            "interval": "monthly",
            "day": 6
        }
        skip_dates = set()

        # 模拟 10.06 是非交易日，调整到 10.09
        def mock_adjust(d):
            if d == date(2025, 10, 6):
                return date(2025, 10, 9)
            return d

        scheduler = RegularInvestmentScheduler(regular_rule, skip_dates, mock_adjust)
        dates = scheduler.generate_dates(end_date=date(2025, 10, 7))

        # 10.06 调整后变成 10.09，超过了截止日期 10.07，不应包含
        expected = {date(2025, 9, 6)}
        assert dates == expected
