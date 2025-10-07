"""
交易日历服务
负责交易日相关的判断和调整
"""

from datetime import date
import exchange_calendars as xcals
import pandas as pd


class TradingCalendar:
    """交易日历"""

    def __init__(self, exchange: str = "XSHG"):
        """
        Args:
            exchange: 交易所代码，默认上交所
        """
        self.calendar = xcals.get_calendar(exchange)

    def is_trading_day(self, d: date) -> bool:
        """判断是否为交易日"""
        return self.calendar.is_session(pd.Timestamp(d))

    def adjust_to_trading_day(self, d: date) -> date:
        """将日期调整为交易日（如果不是交易日则顺延到下一个）"""
        ts = pd.Timestamp(d)
        if self.calendar.is_session(ts):
            return d
        else:
            next_session = self.calendar.date_to_session(ts, direction="next")
            return next_session.date()

    def get_next_trading_day(self, d: date) -> date:
        """获取下一个交易日（如果d本身是交易日，返回下一个）"""
        ts = pd.Timestamp(d)
        if self.calendar.is_session(ts):
            next_session = self.calendar.next_session(ts)
        else:
            next_session = self.calendar.date_to_session(ts, direction="next")
        return next_session.date()

    def get_previous_trading_day(self, d: date) -> date:
        """获取上一个交易日（如果d本身是交易日，返回上一个）"""
        ts = pd.Timestamp(d)
        if self.calendar.is_session(ts):
            prev_session = self.calendar.previous_session(ts)
        else:
            prev_session = self.calendar.date_to_session(ts, direction="previous")
        return prev_session.date()

    def get_trading_day_or_previous(self, d: date) -> date:
        """如果d是交易日返回d，否则返回之前最近的交易日"""
        ts = pd.Timestamp(d)
        if self.calendar.is_session(ts):
            return d
        else:
            prev_session = self.calendar.date_to_session(ts, direction="previous")
            return prev_session.date()
