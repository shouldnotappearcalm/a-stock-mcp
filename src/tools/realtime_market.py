"""
Realtime market tools for the MCP server.
Provides live stock data using Ashare library (Tencent/Sina data sources) and Akshare.
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from src.use_cases.realtime_market import (
    fetch_realtime_kline,
    fetch_technical_indicators,
    fetch_realtime_quote,
    fetch_hot_sectors,
    fetch_market_index,
    fetch_lhb_detail,
    fetch_north_money,
    fetch_limit_up_down,
)

logger = logging.getLogger(__name__)


def register_realtime_market_tools(app: FastMCP):
    """
    Register realtime market data tools with the MCP app.
    
    These tools use Ashare library which fetches data from Tencent/Sina APIs.
    No login required, supports intraday data.
    
    Args:
        app: The FastMCP app instance
    """

    @app.tool()
    def get_realtime_kline(
        code: str,
        frequency: str = "1d",
        count: int = 60,
        format: str = "markdown",
    ) -> str:
        """
        Fetches realtime K-line (OHLCV) data for a Chinese A-share stock.
        
        This tool uses Ashare library which fetches live data from Tencent/Sina APIs.
        No login required, supports intraday data during trading hours.

        Args:
            code: The stock code. Supports multiple formats:
                  - 'sh600000' or 'sz000001' (Tongdaxin format)
                  - '600000' or '000001' (pure number, auto-detect exchange)
                  - 'sh.600000' or 'sz.000001' (Baostock format)
                  - '600519.XSHG' or '000001.XSHE' (JoinQuant format)
            frequency: K-line frequency. Valid options:
                       '1m': 1 minute
                       '5m': 5 minutes
                       '15m': 15 minutes
                       '30m': 30 minutes
                       '60m': 60 minutes
                       '1d': daily (default)
                       '1w': weekly
                       '1M': monthly
            count: Number of K-line bars to fetch. Defaults to 60.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            K-line data table with columns: time, open, close, high, low, volume
        """
        logger.info(
            f"Tool 'get_realtime_kline' called for {code} (freq={frequency}, count={count})"
        )
        return fetch_realtime_kline(
            code=code,
            frequency=frequency,
            count=count,
            format=format,
        )

    @app.tool()
    def get_technical_indicators(
        code: str,
        frequency: str = "1d",
        count: int = 120,
        indicators: Optional[List[str]] = None,
        format: str = "markdown",
    ) -> str:
        """
        Calculates technical indicators for a Chinese A-share stock.
        
        This tool fetches K-line data using Ashare and calculates indicators using MyTT library.
        Combines realtime data with technical analysis.

        Args:
            code: The stock code. Supports multiple formats (same as get_realtime_kline).
            frequency: K-line frequency. Valid options:
                       '1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M'.
                       Defaults to '1d'.
            count: Number of K-line bars to fetch. Defaults to 120 for accurate indicator calculation.
            indicators: List of indicators to calculate. Valid options:
                        - 'MA': Moving Average (5, 10, 20日均线)
                        - 'EMA': Exponential Moving Average (12, 26日)
                        - 'MACD': Moving Average Convergence Divergence
                        - 'KDJ': Stochastic Oscillator
                        - 'RSI': Relative Strength Index
                        - 'WR': Williams %R
                        - 'BOLL': Bollinger Bands
                        - 'BIAS': Bias Ratio
                        - 'CCI': Commodity Channel Index
                        - 'ATR': Average True Range
                        - 'DMI': Directional Movement Index
                        - 'TAQ': Donchian Channel (唐安奇通道)
                        Defaults to ['MA', 'MACD', 'KDJ', 'BOLL', 'RSI'] if not specified.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            K-line data with calculated technical indicators.
        """
        logger.info(
            f"Tool 'get_technical_indicators' called for {code} (freq={frequency}, indicators={indicators})"
        )
        return fetch_technical_indicators(
            code=code,
            frequency=frequency,
            count=count,
            indicators=indicators,
            format=format,
        )

    @app.tool()
    def get_realtime_quote(
        code: str,
        format: str = "markdown",
    ) -> str:
        """
        Fetches realtime quote snapshot for a Chinese A-share stock.
        
        Returns the latest trading data including price, volume, daily change, and turnover rate.
        Quick overview of current stock status.

        Args:
            code: The stock code. Supports multiple formats (same as get_realtime_kline).
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Latest quote data with: 日期, 开盘价, 最高价, 最低价, 收盘价, 成交量, 涨跌额, 涨跌幅, 换手率, 成交额
        """
        logger.info(f"Tool 'get_realtime_quote' called for {code}")
        return fetch_realtime_quote(
            code=code,
            format=format,
        )

    @app.tool()
    def get_hot_sectors(
        top_n: int = 20,
        format: str = "markdown",
    ) -> str:
        """
        Fetches hot concept sectors with top gains.
        
        Returns top gaining concept sectors with leading stocks and trading volume.
        Data source: Eastmoney (东方财富).

        Args:
            top_n: Number of top sectors to return. Defaults to 20.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Hot sectors data with: 板块名称, 涨跌幅, 龙头股, 龙头涨幅, 成交额
        """
        logger.info(f"Tool 'get_hot_sectors' called (top_n={top_n})")
        return fetch_hot_sectors(
            top_n=top_n,
            format=format,
        )

    @app.tool()
    def get_market_index(
        format: str = "markdown",
    ) -> str:
        """
        Fetches realtime market index data for major Chinese stock indices.
        
        Returns realtime data for: 上证指数, 深证成指, 创业板指, 科创50.
        Data source: Sina Finance (新浪财经).

        Args:
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Market index data with: 指数名称, 当前点位, 涨跌点数, 涨跌幅, 成交量, 成交额
        """
        logger.info("Tool 'get_market_index' called")
        return fetch_market_index(
            format=format,
        )

    @app.tool()
    def get_lhb_detail(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        top_n: int = 20,
        format: str = "markdown",
    ) -> str:
        """
        Fetches Long-Hu-Bang (龙虎榜) detail data.
        
        Long-Hu-Bang shows stocks with significant trading activity by institutional investors.
        Data source: Eastmoney via Akshare.

        Args:
            start_date: Start date in format 'YYYYMMDD'. Defaults to 3 days ago.
            end_date: End date in format 'YYYYMMDD'. Defaults to today.
            top_n: Number of records to return. Defaults to 20.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Long-Hu-Bang data with: 代码, 名称, 上榜日期, 收盘价, 涨跌幅, 净买额, 买入额, 卖出额, 上榜原因, 解读
        """
        logger.info(f"Tool 'get_lhb_detail' called (start={start_date}, end={end_date})")
        return fetch_lhb_detail(
            start_date=start_date,
            end_date=end_date,
            top_n=top_n,
            format=format,
        )

    @app.tool()
    def get_north_money(
        format: str = "markdown",
    ) -> str:
        """
        Fetches northbound money flow data (北向资金).
        
        Northbound money refers to foreign capital flowing into A-shares via Hong Kong.
        Data source: Eastmoney via Akshare.

        Args:
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Northbound money flow data with: 日期, 当日净买额, 当日资金流入, 当日资金余额
        """
        logger.info("Tool 'get_north_money' called")
        return fetch_north_money(
            format=format,
        )

    @app.tool()
    def get_limit_up_down(
        format: str = "markdown",
    ) -> str:
        """
        Fetches daily limit up and limit down stock statistics (涨跌停统计).
        
        Shows count of stocks hitting daily price limit (up or down).
        Data source: Eastmoney via Akshare.

        Args:
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Statistics with: 日期, 涨停数量, 跌停数量
        """
        logger.info("Tool 'get_limit_up_down' called")
        return fetch_limit_up_down(
            format=format,
        )