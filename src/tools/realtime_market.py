"""
Realtime market tools for the MCP server.
Provides live stock data using AshareDataSource (Sina/Tencent data sources).
"""
import logging
from typing import List

from mcp.server.fastmcp import FastMCP

from src.ashare_data_source import AshareDataSource
from src.use_cases.realtime_market import (
    fetch_realtime_quote,
    fetch_intraday_minute_kline,
    fetch_realtime_multi_quote,
)

logger = logging.getLogger(__name__)


def register_realtime_market_tools(app: FastMCP, ashare_data_source: AshareDataSource):
    """
    Register realtime market data tools with the MCP app.
    
    These tools use AshareDataSource which fetches data from Sina/Tencent APIs.
    No login required, supports intraday data.
    
    Args:
        app: The FastMCP app instance
        ashare_data_source: AshareDataSource instance for fetching data
    """

    @app.tool()
    def get_realtime_quote(
        code: str,
        format: str = "markdown",
    ) -> str:
        """
        Fetches realtime quote snapshot for a Chinese A-share stock.
        
        Returns the latest trading data with correct date and change calculation.
        Uses minute K-line aggregation for today's data instead of daily data.
        Quick overview of current stock status.

        Args:
            code: The stock code. Supports multiple formats:
                  - 'sh600000' or 'sz000001' (Tongdaxin format)
                  - '600000' or '000001' (pure number, auto-detect exchange)
                  - 'sh.600000' or 'sz.000001' (Baostock format)
                  - '600519.XSHG' or '000001.XSHE' (JoinQuant format)
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Latest quote data with: 日期, 最新价, 今开, 最高, 最低, 昨收, 涨跌额, 涨跌幅, 成交量, 市场状态
        """
        logger.info(f"Tool 'get_realtime_quote' called for {code}")
        try:
            return fetch_realtime_quote(
                ashare_data_source=ashare_data_source,
                code=code,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_realtime_quote: {e}")
            return f"获取实时行情失败: {str(e)}"

    @app.tool()
    def get_intraday_minute_kline(
        code: str,
        frequency: str = "5m",
        format: str = "markdown",
    ) -> str:
        """
        Fetches intraday minute K-line data for a Chinese A-share stock (today only).
        
        Returns minute-level K-line data for the current trading day.
        Data source: Sina/Tencent via AshareDataSource.

        Args:
            code: The stock code. Supports multiple formats (same as get_realtime_quote).
            frequency: Minute frequency. Valid options:
                       '1m': 1 minute
                       '5m': 5 minutes (default)
                       '15m': 15 minutes
                       '30m': 30 minutes
                       '60m': 60 minutes
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Today's minute K-line data with: 时间, 开盘, 最高, 最低, 收盘, 成交量
        """
        logger.info(f"Tool 'get_intraday_minute_kline' called for {code} (freq={frequency})")
        try:
            return fetch_intraday_minute_kline(
                ashare_data_source=ashare_data_source,
                code=code,
                frequency=frequency,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_intraday_minute_kline: {e}")
            return f"获取分钟K线失败: {str(e)}"

    @app.tool()
    def get_realtime_multi_quote(
        codes: List[str],
        format: str = "markdown",
    ) -> str:
        """
        Batch query for realtime quotes (max 10 stocks).
        
        Returns realtime quotes for multiple stocks, sorted by change percentage (descending).
        Individual stock failures do not affect the overall result.

        Args:
            codes: List of stock codes (max 10). Supports multiple formats per code.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Realtime quotes with: 代码, 名称, 最新价, 涨跌幅, 昨收, 状态
        """
        logger.info(f"Tool 'get_realtime_multi_quote' called for {len(codes)} stocks")
        try:
            return fetch_realtime_multi_quote(
                ashare_data_source=ashare_data_source,
                codes=codes,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_realtime_multi_quote: {e}")
            return f"批量获取实时行情失败: {str(e)}"
