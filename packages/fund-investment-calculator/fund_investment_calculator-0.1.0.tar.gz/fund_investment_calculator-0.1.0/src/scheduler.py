"""
定投日期调度器
负责根据定投规则生成投资日期
"""

from datetime import date, timedelta
from typing import List, Dict, Callable, Set
import calendar


class RegularInvestmentScheduler:
    """定投日期生成器"""

    def __init__(
        self,
        regular_rule: Dict,
        skip_dates: Set[date],
        adjust_to_trading_day: Callable[[date], date]
    ):
        """
        Args:
            regular_rule: 定投规则字典
            skip_dates: 需要跳过的日期集合
            adjust_to_trading_day: 交易日调整函数
        """
        self.regular_rule = regular_rule
        self.skip_dates = skip_dates
        self.adjust_to_trading_day = adjust_to_trading_day

    def generate_dates(self, end_date: date = None) -> Set[date]:
        """
        生成定投日期

        Args:
            end_date: 截止日期，默认为今天

        Returns:
            定投日期集合
        """
        if not self.regular_rule:
            return set()

        start_date = self.regular_rule.get("start_date")
        if not start_date:
            raise ValueError("regular_rule 必须包含 start_date")

        interval = self.regular_rule.get("interval", "monthly")
        end_date = end_date or date.today()

        if interval == "monthly":
            return self._generate_monthly(start_date, end_date)
        elif interval == "weekly":
            return self._generate_weekly(start_date, end_date)
        elif interval == "biweekly":
            return self._generate_biweekly(start_date, end_date)
        else:
            raise ValueError(f"不支持的间隔类型: {interval}")

    def _generate_monthly(self, start_date: date, end_date: date) -> Set[date]:
        """生成月度定投日期"""
        day = self.regular_rule.get("day")
        if day is None:
            raise ValueError("monthly 间隔必须指定 day 参数")

        dates = set()
        current = start_date

        while current <= end_date:
            target_date = self.adjust_to_trading_day(current)

            if target_date <= end_date and target_date not in self.skip_dates:
                dates.add(target_date)

            # 计算下个月同一天
            if current.month == 12:
                current = date(current.year + 1, 1, day)
            else:
                try:
                    current = date(current.year, current.month + 1, day)
                except ValueError:
                    # 处理月末日期（如31号在2月不存在）
                    next_month = current.month + 1
                    next_year = current.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    last_day = calendar.monthrange(next_year, next_month)[1]
                    current = date(next_year, next_month, min(day, last_day))

        return dates

    def _generate_weekly(self, start_date: date, end_date: date) -> Set[date]:
        """生成周定投日期"""
        weekday = self.regular_rule.get("weekday")
        if weekday is None:
            raise ValueError("weekly 间隔必须指定 weekday 参数（0=周一）")

        dates = set()
        current = start_date

        while current <= end_date:
            if current.weekday() == weekday:
                target_date = self.adjust_to_trading_day(current)
                if target_date <= end_date and target_date not in self.skip_dates:
                    dates.add(target_date)

            current += timedelta(days=1)

        return dates

    def _generate_biweekly(self, start_date: date, end_date: date) -> Set[date]:
        """生成双周定投日期"""
        weekday = self.regular_rule.get("weekday")
        if weekday is None:
            raise ValueError("biweekly 间隔必须指定 weekday 参数（0=周一）")

        dates = set()
        current = start_date

        while current <= end_date:
            if current.weekday() == weekday:
                target_date = self.adjust_to_trading_day(current)
                if target_date <= end_date and target_date not in self.skip_dates:
                    dates.add(target_date)

                current += timedelta(weeks=2)
            else:
                current += timedelta(days=1)

        return dates
