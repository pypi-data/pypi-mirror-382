"""
基金净值数据提供者模块
"""

from datetime import date
from typing import Dict
import akshare as ak
import pandas as pd


class NavProvider:
    """基金净值数据提供者"""

    def __init__(self, fund_code: str):
        """
        初始化净值提供者

        Args:
            fund_code: 基金代码（6位数字）
        """
        self.fund_code = fund_code
        self._cache: Dict[date, float] = {}
        self._latest: tuple[date, float] | None = None  # 缓存最新净值
        self._fetched = False  # 标记是否已获取全量数据

    def get(self, d: date) -> float:
        """
        获取指定日期的净值

        Args:
            d: 日期

        Returns:
            净值
        """
        # 如果未获取过数据，获取全量数据
        if not self._fetched:
            self._fetch()

        if d not in self._cache:
            raise ValueError(f"无法获取 {d} 的净值数据")

        return self._cache[d]

    def get_latest(self) -> tuple[date, float]:
        """
        获取最新可用净值

        Returns:
            (日期, 净值)
        """
        if not self._fetched:
            self._fetch()

        if self._latest is None:
            raise ValueError("无法获取最新净值")

        return self._latest

    def _fetch(self):
        """
        获取全量净值数据并缓存
        """
        try:
            # print(f'[debug] fetching all data for {self.fund_code}')
            # 使用 akshare 获取基金净值数据（返回全量历史数据）
            df = ak.fund_open_fund_info_em(
                symbol=self.fund_code,
                indicator="单位净值走势"
            )

            if df.empty:
                raise ValueError(f"未获取到基金 {self.fund_code} 的净值数据")

            # 数据格式：净值日期, 单位净值
            df['净值日期'] = pd.to_datetime(df['净值日期']).dt.date
            df['单位净值'] = df['单位净值'].astype(float)

            # 保存最新净值
            latest_row = df.loc[df['净值日期'].idxmax()]
            self._latest = (latest_row['净值日期'], latest_row['单位净值'])

            # 缓存所有数据
            for _, row in df.iterrows():
                self._cache[row['净值日期']] = row['单位净值']

            self._fetched = True
            # print(f'[debug] cached {len(self._cache)} records')

        except Exception as e:
            raise RuntimeError(f"获取基金净值失败: {e}")
