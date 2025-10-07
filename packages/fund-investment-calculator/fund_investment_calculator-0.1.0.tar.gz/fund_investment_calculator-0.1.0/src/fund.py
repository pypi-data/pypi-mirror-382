"""
基金定投计算模块
使用 akshare 获取基金净值数据
使用 exchange_calendars 判断交易日
"""

from datetime import date
from typing import Optional, List, Dict
import akshare as ak
from scipy.optimize import newton
from .scheduler import RegularInvestmentScheduler
from .trading_calendar import TradingCalendar
from .nav_provider import NavProvider


class Fund:
    """基金定投计算类"""

    def __init__(
        self,
        fund_code: str,
        fund_name: Optional[str] = None,
        buy_fee_rate: float = 0.0015,
        regular_rule: Optional[Dict] = None,
        skip_dates: Optional[List[date]] = None,
        manual_investments: Optional[List[Dict]] = None
    ):
        """
        初始化基金对象

        Args:
            fund_code: 基金代码（6位数字）
            fund_name: 基金名称（可选，不填会自动获取）
            buy_fee_rate: 申购费率，默认0.15%
            regular_rule: 定投规则字典
                {
                    "start_date": date(2024, 1, 15),
                    "interval": "monthly",  # "monthly", "weekly", "biweekly"
                    "day": 15,              # 每月的日期（monthly时）
                    "weekday": 5,           # 星期几，0=周一（weekly/biweekly时）
                    "amount": 1000          # 每次定投金额
                }
            skip_dates: 定投失败日期列表
            manual_investments: 手动投资列表
                [{"date": date(2024, 2, 10), "amount": 5000}, ...]
        """
        self.fund_code = fund_code
        self.fund_name = fund_name
        self.buy_fee_rate = buy_fee_rate
        self.regular_rule = regular_rule or {}
        self.skip_dates = set(skip_dates or [])
        self.manual_investments = manual_investments or []

        # 初始化交易日历（上交所）
        self.trading_calendar = TradingCalendar("XSHG")

        # 初始化净值提供者
        self._nav_provider = NavProvider(fund_code)

        # 如果没有提供基金名称，尝试从第一次获取净值时获取
        if not self.fund_name:
            self._fetch_fund_info()

        # 预计算所有投资日期和金额并缓存
        self._investment_schedule = self._compute_investment_schedule()

    def set_fund_name(self, fund_name: str):
        """
        设置基金名称

        Args:
            fund_name: 基金名称
        """
        self.fund_name = fund_name

    def _fetch_fund_info(self):
        """获取基金基本信息"""
        try:
            df = ak.fund_individual_basic_info_xq(symbol=self.fund_code)
            if df.empty:
                raise ValueError(f"无法获取基金 {self.fund_code} 的基本信息")

            # 从 DataFrame 中提取基金名称（item='基金名称'）
            fund_name_row = df[df['item'] == '基金名称']
            if fund_name_row.empty:
                raise ValueError(f"无法获取基金 {self.fund_code} 的名称")

            self.fund_name = fund_name_row['value'].iloc[0]
        except Exception as e:
            raise ValueError(f"获取基金信息失败: {e}")

    def _compute_investment_schedule(self) -> Dict[date, float]:
        """
        计算所有投资日期和金额

        Returns:
            {日期: 投资金额} 字典
        """
        schedule = {}

        # 1. 添加定投日期和金额
        if self.regular_rule:
            scheduler = RegularInvestmentScheduler(
                self.regular_rule,
                self.skip_dates,
                self.trading_calendar.adjust_to_trading_day
            )
            regular_amount = self.regular_rule.get("amount", 0)
            for d in scheduler.generate_dates():
                schedule[d] = regular_amount

        # 2. 添加手动投资日期和金额（与定投金额累加）
        for investment in self.manual_investments:
            inv_date = self.trading_calendar.adjust_to_trading_day(investment["date"])
            schedule[inv_date] = schedule.get(inv_date, 0) + investment["amount"]

        return schedule

    def get_all_investment_dates(self) -> List[date]:
        """
        获取所有投资日期（定投+手动）

        Returns:
            排序后的日期列表
        """
        return sorted(self._investment_schedule.keys())

    def get_investment_records(self) -> List[Dict]:
        """
        获取每笔投资的详细记录

        Returns:
            [{
                "date": date,
                "amount": float,      # 投入本金
                "fee": float,         # 手续费
                "net_amount": float,  # 扣费后金额
                "nav": float,         # 买入净值
                "shares": float       # 买入份额
            }, ...]
        """
        all_dates = sorted(self._investment_schedule.keys())

        if not all_dates:
            return []

        records = []

        # 遍历所有投资日期，使用缓存的金额
        for d in all_dates:
            inv_amount = self._investment_schedule[d]
            fee = inv_amount * self.buy_fee_rate
            net_amount = inv_amount - fee
            nav = self._nav_provider.get(d)
            shares = net_amount / nav

            records.append({
                "date": d,
                "amount": inv_amount,
                "fee": fee,
                "net_amount": net_amount,
                "nav": nav,
                "shares": shares
            })

        return records

    def calculate_return(self, as_of_date: Optional[date] = None) -> Dict:
        """
        计算总体收益

        Args:
            as_of_date: 计算截止日期，不传则使用最新净值

        Returns:
            {
                "as_of_date": date,           # 计算日期
                "total_cost": float,          # 总投入（含手续费）
                "total_net_cost": float,      # 总投入（扣除手续费）
                "total_shares": float,        # 总份额
                "current_nav": float,         # 当前净值
                "current_value": float,       # 当前价值
                "profit": float,              # 收益金额
                "return_rate": float,         # 收益率（%）
                "annualized_return": float,   # 年化收益率（%）
                "irr": float                  # 内部收益率（%）
            }
        """
        records = self.get_investment_records()

        if not records:
            raise ValueError("没有投资记录")

        # 确定计算日期和净值
        if as_of_date:
            # 调整为交易日（如果不是交易日，取之前最近的交易日）
            calc_date = self.trading_calendar.get_trading_day_or_previous(as_of_date)
            current_nav = self._nav_provider.get(calc_date)
        else:
            calc_date, current_nav = self._nav_provider.get_latest()

        # 计算总投入和总份额
        total_cost = sum(r["amount"] for r in records)
        total_net_cost = sum(r["net_amount"] for r in records)
        total_shares = sum(r["shares"] for r in records)

        # 当前价值
        current_value = total_shares * current_nav

        # 收益
        profit = current_value - total_cost
        return_rate = (profit / total_cost * 100) if total_cost > 0 else 0

        # 年化收益率（简单算法）
        first_date = records[0]["date"]
        holding_days = (calc_date - first_date).days
        if holding_days > 0:
            annualized_return = (profit / total_cost) / holding_days * 365 * 100
        else:
            annualized_return = 0

        # 计算IRR
        irr = self._calculate_irr(records, current_value, calc_date)

        return {
            "as_of_date": calc_date,
            "total_cost": round(total_cost, 2),
            "total_net_cost": round(total_net_cost, 2),
            "total_shares": round(total_shares, 4),
            "current_nav": round(current_nav, 4),
            "current_value": round(current_value, 2),
            "profit": round(profit, 2),
            "return_rate": round(return_rate, 2),
            "annualized_return": round(annualized_return, 2),
            "irr": round(irr, 2)
        }

    def _calculate_irr(self, records: List[Dict], final_value: float, calc_date: date) -> float:
        """
        计算内部收益率（IRR）

        Args:
            records: 投资记录
            final_value: 最终价值
            calc_date: 计算日期

        Returns:
            IRR（%）
        """
        if not records:
            return 0

        # 构建现金流
        cash_flows = []
        first_date = records[0]["date"]

        # 所有投入为负现金流
        for record in records:
            days = (record["date"] - first_date).days
            cash_flows.append((days, -record["amount"]))

        # 最终价值为正现金流
        final_days = (calc_date - first_date).days
        cash_flows.append((final_days, final_value))

        # 定义NPV函数
        def npv(rate):
            return sum(cf / (1 + rate) ** (days / 365) for days, cf in cash_flows)

        # 使用牛顿法求解IRR
        try:
            irr = newton(npv, 0.1, maxiter=100)  # 初始猜测10%
            return irr * 100  # 转换为百分比
        except:
            # 如果求解失败，返回简单收益率
            total_cost = sum(r["amount"] for r in records)
            profit = final_value - total_cost
            holding_days = final_days
            if holding_days > 0:
                return (profit / total_cost) / holding_days * 365 * 100
            return 0

    def calculate_each_investment_return(self, as_of_date: Optional[date] = None) -> List[Dict]:
        """
        计算每笔投资的收益

        Args:
            as_of_date: 计算截止日期，不传则使用最新净值

        Returns:
            [{
                "date": date,
                "amount": float,          # 投入金额
                "buy_nav": float,         # 买入净值
                "shares": float,          # 买入份额
                "current_nav": float,     # 当前净值
                "current_value": float,   # 当前价值
                "profit": float,          # 该笔收益
                "return_rate": float      # 该笔收益率（%）
            }, ...]
        """
        records = self.get_investment_records()

        if not records:
            return []

        # 确定计算日期和净值
        if as_of_date:
            # 调整为交易日（如果不是交易日，取之前最近的交易日）
            calc_date = self.trading_calendar.get_trading_day_or_previous(as_of_date)
            current_nav = self._nav_provider.get(calc_date)
        else:
            calc_date, current_nav = self._nav_provider.get_latest()

        results = []
        for record in records:
            shares = record["shares"]
            current_value = shares * current_nav
            profit = current_value - record["amount"]
            return_rate = (profit / record["amount"] * 100) if record["amount"] > 0 else 0

            results.append({
                "date": record["date"],
                "amount": round(record["amount"], 2),
                "buy_nav": round(record["nav"], 4),
                "shares": round(shares, 4),
                "current_nav": round(current_nav, 4),
                "current_value": round(current_value, 2),
                "profit": round(profit, 2),
                "return_rate": round(return_rate, 2)
            })

        return results
