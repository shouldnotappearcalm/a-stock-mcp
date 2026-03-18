"""
Market data tools for the MCP server.
Provides market-wide data using Akshare and technical indicators using MyTT.
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from src.use_cases.market_data import (
    fetch_realtime_kline,
    fetch_technical_indicators,
    fetch_hot_sectors,
    fetch_market_index,
    fetch_lhb_detail,
    fetch_north_money,
    fetch_limit_up_down,
    fetch_limit_up_pool,
    fetch_limit_down_pool,
    fetch_stock_money_flow,
    fetch_consecutive_limit_up,
)

logger = logging.getLogger(__name__)


def register_market_data_tools(app: FastMCP):
    """
    Register market data tools with the MCP app.
    
    These tools use Akshare library which fetches data from Eastmoney and other sources.
    Also includes technical indicator tools using MyTT library.
    
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
        logger.info(f"Tool 'get_realtime_kline' called for {code} (freq={frequency}, count={count})")
        try:
            return fetch_realtime_kline(
                code=code,
                frequency=frequency,
                count=count,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_realtime_kline: {e}")
            return f"获取实时K线数据失败: {str(e)}"

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
        logger.info(f"Tool 'get_technical_indicators' called for {code} (freq={frequency}, indicators={indicators})")
        try:
            return fetch_technical_indicators(
                code=code,
                frequency=frequency,
                count=count,
                indicators=indicators,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_technical_indicators: {e}")
            return f"计算技术指标失败: {str(e)}"

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
        try:
            return fetch_hot_sectors(
                top_n=top_n,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_hot_sectors: {e}")
            return f"获取热点板块数据失败: {str(e)}"

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
        try:
            return fetch_market_index(format=format)
        except Exception as e:
            logger.exception(f"Error in get_market_index: {e}")
            return f"获取大盘指数数据失败: {str(e)}"

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
        try:
            return fetch_lhb_detail(
                start_date=start_date,
                end_date=end_date,
                top_n=top_n,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_lhb_detail: {e}")
            return f"获取龙虎榜数据失败: {str(e)}"

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
        try:
            return fetch_north_money(format=format)
        except Exception as e:
            logger.exception(f"Error in get_north_money: {e}")
            return f"获取北向资金数据失败: {str(e)}"

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
        try:
            return fetch_limit_up_down(format=format)
        except Exception as e:
            logger.exception(f"Error in get_limit_up_down: {e}")
            return f"获取涨跌停统计失败: {str(e)}"

    @app.tool()
    def get_limit_up_pool(
        date: Optional[str] = None,
        top_n: int = 30,
        format: str = "markdown",
    ) -> str:
        """
        Fetches limit up stocks pool (涨停股池).
        
        Returns detailed list of stocks hitting daily upper price limit.
        Data source: Eastmoney via Akshare.

        Args:
            date: Date in format 'YYYYMMDD'. Defaults to today.
            top_n: Number of stocks to return. Defaults to 30.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Limit up stocks with: 代码, 名称, 涨跌幅, 最新价, 封板资金, 连板数, 首次封板时间, 所属行业
        """
        logger.info(f"Tool 'get_limit_up_pool' called (date={date})")
        try:
            return fetch_limit_up_pool(
                date=date,
                top_n=top_n,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_limit_up_pool: {e}")
            return f"获取涨停股池失败: {str(e)}"

    @app.tool()
    def get_limit_down_pool(
        date: Optional[str] = None,
        top_n: int = 30,
        format: str = "markdown",
    ) -> str:
        """
        Fetches limit down stocks pool (跌停股池).
        
        Returns detailed list of stocks hitting daily lower price limit.
        Data source: Eastmoney via Akshare.

        Args:
            date: Date in format 'YYYYMMDD'. Defaults to today.
            top_n: Number of stocks to return. Defaults to 30.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Limit down stocks with: 代码, 名称, 涨跌幅, 最新价, 成交额, 流通市值
        """
        logger.info(f"Tool 'get_limit_down_pool' called (date={date})")
        try:
            return fetch_limit_down_pool(
                date=date,
                top_n=top_n,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_limit_down_pool: {e}")
            return f"获取跌停股池失败: {str(e)}"

    @app.tool()
    def get_stock_money_flow(
        code: str,
        top_n: int = 10,
        format: str = "markdown",
    ) -> str:
        """
        Fetches individual stock money flow data (个股资金流向).
        
        Shows capital flow breakdown by investor size categories.
        Data source: Eastmoney via Akshare.

        Args:
            code: Stock code (e.g., '600519' or 'sh600519').
            top_n: Number of recent days to return. Defaults to 10.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Money flow data with: 主力净流入, 超大单, 大单, 中单, 小单 净额和占比
        """
        logger.info(f"Tool 'get_stock_money_flow' called for {code}")
        try:
            return fetch_stock_money_flow(
                code=code,
                top_n=top_n,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_stock_money_flow: {e}")
            return f"获取资金流向失败: {str(e)}"

    @app.tool()
    def get_consecutive_limit_up(
        date: Optional[str] = None,
        top_n: int = 30,
        format: str = "markdown",
    ) -> str:
        """
        Fetches consecutive limit up stocks (连板股).
        
        Returns stocks that have been limit up for consecutive days.
        Data source: Eastmoney via Akshare.

        Args:
            date: Date in format 'YYYYMMDD'. Defaults to today.
            top_n: Number of stocks to return. Defaults to 30.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Consecutive limit up stocks with: 代码, 名称, 连板数, 涨停统计, 所属行业
        """
        logger.info(f"Tool 'get_consecutive_limit_up' called (date={date})")
        try:
            return fetch_consecutive_limit_up(
                date=date,
                top_n=top_n,
                format=format,
            )
        except Exception as e:
            logger.exception(f"Error in get_consecutive_limit_up: {e}")
            return f"获取连板股失败: {str(e)}"
