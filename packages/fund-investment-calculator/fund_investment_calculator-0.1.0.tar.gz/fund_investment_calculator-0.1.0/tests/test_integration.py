"""
集成测试 - 使用真实API请求验证计算结果
基于data.json的配置和calculate.py的输出结果
"""

import pytest
from datetime import date
from src.fund import Fund


class TestIntegration:
    """集成测试类 - 真实API调用"""

    def test_fund_160119_calculation(self):
        """测试基金 160119 (南方中证500ETF联接) 的计算

        预期结果（截至2025-09-30）:
        - 总投入: 29500.00元
        - 扣费后投入: 29464.60元
        - 持有份额: 18867.8556份
        - 当前净值: 2.0762
        - 当前市值: 39173.44元
        - 累计收益: 9673.44元
        - 收益率: 32.79%
        - 年化收益率: 8.31%
        - IRR: 16.15%
        """
        fund = Fund(
            fund_code="160119",
            buy_fee_rate=0.0012,
            regular_rule={
                "start_date": date(2021, 11, 8),
                "interval": "monthly",
                "day": 6,
                "amount": 500
            },
            skip_dates=[date(2023, 9, 6)],
            manual_investments=[
                {"date": date(2021, 10, 20), "amount": 500},
                {"date": date(2024, 8, 11), "amount": 2000},
                {"date": date(2024, 8, 29), "amount": 2000},
                {"date": date(2025, 4, 8), "amount": 2000}
            ]
        )

        # 获取投资记录
        records = fund.get_investment_records()
        assert len(records) == 50, f"预期50笔投资，实际{len(records)}笔"

        # 验证总投入
        total_amount = sum(r["amount"] for r in records)
        assert total_amount == 29500.0, f"预期总投入29500元，实际{total_amount}元"

        # 计算收益 - 使用历史日期以确保结果稳定
        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["as_of_date"] == date(2025, 9, 30)
        assert result["total_cost"] == 29500.0
        assert result["total_net_cost"] == 29464.60
        assert result["total_shares"] == 18867.8556
        assert result["current_nav"] == pytest.approx(2.0762, abs=0.0001)
        assert result["current_value"] == 39173.44
        assert result["profit"] == 9673.44
        assert result["return_rate"] == 32.79
        assert result["annualized_return"] == pytest.approx(8.31, abs=0.01)
        assert result["irr"] == pytest.approx(16.15, abs=0.01)

    def test_fund_110020_calculation(self):
        """测试基金 110020 (易方达沪深300ETF联接A) 的计算

        预期结果（截至2025-09-30）:
        - 总投入: 27000.00元
        - 扣费后投入: 26967.60元
        - 持有份额: 17955.3916份
        - 当前净值: 1.8551
        - 当前市值: 33309.05元
        - 累计收益: 6309.05元
        - 收益率: 23.37%
        - 年化收益率: 5.37%
        - IRR: 10.53%
        """
        fund = Fund(
            fund_code="110020",
            buy_fee_rate=0.0012,
            regular_rule={
                "start_date": date(2021, 5, 26),
                "interval": "weekly",
                "weekday": 2,  # 周三
                "amount": 100
            },
            skip_dates=[date(2021, 7, 28), date(2021, 8, 4)],
            manual_investments=[
                {"date": date(2021, 5, 26), "amount": 100},
                {"date": date(2021, 7, 28), "amount": 500},
                {"date": date(2024, 8, 11), "amount": 2000},
                {"date": date(2025, 4, 8), "amount": 2000}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 227, f"预期227笔投资，实际{len(records)}笔"

        total_amount = sum(r["amount"] for r in records)
        assert total_amount == 27000.0

        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["total_cost"] == 27000.0
        assert result["total_net_cost"] == 26967.60
        assert result["total_shares"] == 17955.3916
        assert result["current_nav"] == pytest.approx(1.8551, abs=0.0001)
        assert result["current_value"] == 33309.05
        assert result["profit"] == 6309.05
        assert result["return_rate"] == 23.37
        assert result["annualized_return"] == pytest.approx(5.37, abs=0.01)
        assert result["irr"] == pytest.approx(10.53, abs=0.01)

    def test_fund_090010_calculation(self):
        """测试基金 090010 (大成中证红利指数A) 的计算

        预期结果（截至2025-09-30）:
        - 总投入: 5100.00元
        - 扣费后投入: 5093.88元
        - 持有份额: 2316.6137份
        - 当前净值: 2.6006
        - 当前市值: 6024.59元
        - 累计收益: 924.59元
        - 收益率: 18.13%
        - 年化收益率: 4.61%
        - IRR: 5.43%
        """
        fund = Fund(
            fund_code="090010",
            buy_fee_rate=0.0012,
            regular_rule={
                "start_date": date(2025, 7, 25),
                "interval": "weekly",
                "weekday": 4,  # 周五
                "amount": 100
            },
            manual_investments=[
                {"date": date(2021, 10, 26), "amount": 2000},
                {"date": date(2021, 10, 28), "amount": 1000},
                {"date": date(2021, 11, 18), "amount": 1000},
                {"date": date(2025, 9, 26), "amount": 100}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 13

        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["total_cost"] == 5100.0
        assert result["total_net_cost"] == 5093.88
        assert result["total_shares"] == 2316.6137
        assert result["current_nav"] == pytest.approx(2.6006, abs=0.0001)
        assert result["current_value"] == 6024.59
        assert result["profit"] == 924.59
        assert result["return_rate"] == 18.13
        assert result["annualized_return"] == pytest.approx(4.61, abs=0.01)
        assert result["irr"] == pytest.approx(5.43, abs=0.01)

    def test_fund_164906_manual_only(self):
        """测试基金 164906 (交银中证海外中国互联网指数(LOF)A) - 纯手动投资

        预期结果（截至2025-09-29）:
        - 总投入: 2000.00元
        - 扣费后投入: 1997.60元
        - 持有份额: 1589.4152份
        - 当前净值: 1.4432
        - 当前市值: 2293.84元
        - 累计收益: 293.84元
        - 收益率: 14.69%
        - 年化收益率: 3.48%
        - IRR: 3.45%
        """
        fund = Fund(
            fund_code="164906",
            buy_fee_rate=0.0012,
            manual_investments=[
                {"date": date(2021, 7, 12), "amount": 500},
                {"date": date(2021, 7, 26), "amount": 500},
                {"date": date(2021, 7, 28), "amount": 500},
                {"date": date(2022, 3, 4), "amount": 500}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 4

        result = fund.calculate_return(as_of_date=date(2025, 9, 29))

        assert result["total_cost"] == 2000.0
        assert result["total_net_cost"] == 1997.60
        assert result["total_shares"] == 1589.4152
        assert result["current_nav"] == pytest.approx(1.4432, abs=0.0001)
        assert result["current_value"] == 2293.84
        assert result["profit"] == 293.84
        assert result["return_rate"] == 14.69
        assert result["annualized_return"] == pytest.approx(3.48, abs=0.01)
        assert result["irr"] == pytest.approx(3.45, abs=0.01)

    def test_fund_009198_recent_investment(self):
        """测试基金 009198 (前海开源黄金ETF联接A) - 近期投资

        预期结果（截至2025-09-30）:
        - 总投入: 100.00元
        - 扣费后投入: 99.94元
        - 持有份额: 50.2893份
        - 当前净值: 2.0297
        - 当前市值: 102.07元
        - 累计收益: 2.07元
        - 收益率: 2.07%
        - 年化收益率: 189.09%
        - IRR: 549.88%
        """
        fund = Fund(
            fund_code="009198",
            buy_fee_rate=0.0006,
            manual_investments=[
                {"date": date(2025, 9, 26), "amount": 100}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 1

        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["total_cost"] == 100.0
        assert result["total_net_cost"] == 99.94
        assert result["total_shares"] == 50.2893
        assert result["current_nav"] == pytest.approx(2.0297, abs=0.0001)
        assert result["current_value"] == 102.07
        assert result["profit"] == 2.07
        assert result["return_rate"] == 2.07

    def test_fund_320007_with_loss(self):
        """测试基金 320007 (诺安成长混合A) - 亏损场景

        预期结果（截至2025-09-30）:
        - 总投入: 1500.00元
        - 扣费后投入: 1497.75元
        - 持有份额: 750.2819份
        - 当前净值: 1.9730
        - 当前市值: 1480.31元
        - 累计收益: -19.69元
        - 收益率: -1.31%
        - 年化收益率: -0.34%
        - IRR: -0.35%
        """
        fund = Fund(
            fund_code="320007",
            buy_fee_rate=0.0015,
            manual_investments=[
                {"date": date(2021, 11, 7), "amount": 1000},
                {"date": date(2022, 3, 9), "amount": 500}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 2

        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["total_cost"] == 1500.0
        assert result["total_net_cost"] == 1497.75
        assert result["total_shares"] == 750.2819
        assert result["current_nav"] == pytest.approx(1.9730, abs=0.0001)
        assert result["current_value"] == 1480.31
        assert result["profit"] == -19.69
        assert result["return_rate"] == -1.31
        assert result["annualized_return"] == pytest.approx(-0.34, abs=0.01)
        assert result["irr"] == pytest.approx(-0.35, abs=0.01)

    def test_fund_519761_zero_fee(self):
        """测试基金 519761 (交银多策略回报灵活配置混合C) - 零申购费

        预期结果（截至2025-09-30）:
        - 总投入: 20000.00元
        - 扣费后投入: 20000.00元
        - 持有份额: 13586.9565份
        - 当前净值: 1.6210
        - 当前市值: 22024.46元
        - 累计收益: 2024.46元
        - 收益率: 10.12%
        - 年化收益率: 2.60%
        - IRR: 2.51%
        """
        fund = Fund(
            fund_code="519761",
            buy_fee_rate=0.0,
            manual_investments=[
                {"date": date(2021, 11, 11), "amount": 20000}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 1
        assert records[0]["fee"] == 0.0
        assert records[0]["net_amount"] == 20000.0

        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["total_cost"] == 20000.0
        assert result["total_net_cost"] == 20000.0
        assert result["total_shares"] == 13586.9565
        assert result["current_nav"] == pytest.approx(1.6210, abs=0.0001)
        assert result["current_value"] == 22024.46
        assert result["profit"] == 2024.46
        assert result["return_rate"] == 10.12
        assert result["annualized_return"] == pytest.approx(2.60, abs=0.01)
        assert result["irr"] == pytest.approx(2.51, abs=0.01)

    def test_fund_000942_information_tech(self):
        """测试基金 000942 (广发信息技术联接A) - 高收益场景

        预期结果（截至2025-09-30）:
        - 总投入: 500.00元
        - 扣费后投入: 499.40元
        - 持有份额: 434.4120份
        - 当前净值: 1.7105
        - 当前市值: 743.06元
        - 累计收益: 243.06元
        - 收益率: 48.61%
        - 年化收益率: 13.64%
        - IRR: 11.76%
        """
        fund = Fund(
            fund_code="000942",
            buy_fee_rate=0.0012,
            manual_investments=[
                {"date": date(2022, 3, 9), "amount": 500}
            ]
        )

        records = fund.get_investment_records()
        assert len(records) == 1

        result = fund.calculate_return(as_of_date=date(2025, 9, 30))

        assert result["total_cost"] == 500.0
        assert result["total_net_cost"] == 499.40
        assert result["total_shares"] == 434.4120
        assert result["current_nav"] == pytest.approx(1.7105, abs=0.0001)
        assert result["current_value"] == 743.06
        assert result["profit"] == 243.06
        assert result["return_rate"] == 48.61
        assert result["annualized_return"] == pytest.approx(13.64, abs=0.01)
        assert result["irr"] == pytest.approx(11.76, abs=0.01)

    def test_investment_dates_generation(self):
        """测试投资日期生成的正确性"""
        # 月度定投
        fund1 = Fund(
            fund_code="160119",
            buy_fee_rate=0.0012,
            regular_rule={
                "start_date": date(2021, 11, 8),
                "interval": "monthly",
                "day": 6,
                "amount": 500
            },
            skip_dates=[date(2023, 9, 6)]
        )

        dates = fund1.get_all_investment_dates()
        # 验证跳过日期生效
        assert date(2023, 9, 6) not in dates
        # 验证日期数量合理（2021-11到2025-09约46个月）
        assert 40 <= len(dates) <= 50

    def test_each_investment_return(self):
        """测试单笔投资收益计算"""
        fund = Fund(
            fund_code="160119",
            buy_fee_rate=0.0012,
            manual_investments=[
                {"date": date(2021, 10, 20), "amount": 500},
                {"date": date(2024, 8, 11), "amount": 2000}
            ]
        )

        each_results = fund.calculate_each_investment_return(as_of_date=date(2025, 9, 30))

        assert len(each_results) == 2

        # 第一笔投资（早期）应该有更高的收益率
        first_investment = each_results[0]
        assert first_investment["date"] == date(2021, 10, 20)
        assert first_investment["amount"] == 500.0
        assert first_investment["return_rate"] > 0

        # 第二笔投资（较晚）
        second_investment = each_results[1]
        assert second_investment["date"] == date(2024, 8, 12)  # 可能有交易日调整
        assert second_investment["amount"] == 2000.0
