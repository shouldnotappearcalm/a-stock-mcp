# Main MCP server file
import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Import the interface and the concrete implementation
from src.data_source_interface import FinancialDataSource
from src.baostock_data_source import BaostockDataSource
from src.ashare_data_source import AshareDataSource
from src.utils import setup_logging

# 导入各模块工具的注册函数
from src.tools.stock_market import register_stock_market_tools
from src.tools.financial_reports import register_financial_report_tools
from src.tools.indices import register_index_tools
from src.tools.market_overview import register_market_overview_tools
from src.tools.macroeconomic import register_macroeconomic_tools
from src.tools.date_utils import register_date_utils_tools
from src.tools.analysis import register_analysis_tools
from src.tools.helpers import register_helpers_tools
from src.tools.realtime_market import register_realtime_market_tools
from src.tools.market_data import register_market_data_tools

# --- Logging Setup ---
# Call the setup function from utils
# You can control the default level here (e.g., logging.DEBUG for more verbose logs)
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Dependency Injection ---
# Instantiate the data source - easy to swap later if needed
active_data_source: FinancialDataSource = BaostockDataSource()
ashare_data_source: AshareDataSource = AshareDataSource()

# --- Get current date for system prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

# --- FastMCP App Initialization ---
app = FastMCP(
    server_name="a_share_data_provider",
    description=f"""今天是{current_date}。提供中国A股市场数据分析工具。此服务提供客观数据分析，用户需自行做出投资决策。数据分析基于公开市场信息，不构成投资建议，仅供参考。

⚠️ 重要说明:
1. 最新交易日不一定是今天，需要从 get_latest_trading_date() 获取
2. 请始终使用 get_latest_trading_date() 工具获取实际当前最近的交易日，不要依赖训练数据中的日期认知
3. 当分析"最近"或"近期"市场情况时，必须首先调用 get_market_analysis_timeframe() 工具确定实际的分析时间范围
4. 任何涉及日期的分析必须基于工具返回的实际数据，不得使用过时或假设的日期

📊 实时行情工具 (重构):
- get_realtime_quote: 获取实时行情快照（用分钟K线聚合今日数据，日期和涨跌幅语义正确）
- get_intraday_minute_kline: 获取当日分钟K线数据（支持1/5/15/30/60分钟）
- get_realtime_multi_quote: 批量查询实时行情（最多10只，按涨跌幅排序）

📈 技术分析工具:
- get_realtime_kline: 获取K线数据（支持分钟/日线/周线/月线）
- get_technical_indicators: 计算技术指标（MA/MACD/KDJ/BOLL/RSI等）

📊 市场数据工具:
- get_hot_sectors: 热点板块
- get_market_index: 大盘指数
- get_lhb_detail: 龙虎榜
- get_north_money: 北向资金
- get_limit_up_down: 涨跌停统计
- get_limit_up_pool: 涨停股池
- get_limit_down_pool: 跌停股池
- get_stock_money_flow: 个股资金流向
- get_consecutive_limit_up: 连板股
""",
    # Specify dependencies for installation if needed (e.g., when using `mcp install`)
    # dependencies=["baostock", "pandas"]
)

# --- 注册各模块的工具 ---
register_stock_market_tools(app, active_data_source)
register_financial_report_tools(app, active_data_source)
register_index_tools(app, active_data_source)
register_market_overview_tools(app, active_data_source)
register_macroeconomic_tools(app, active_data_source)
register_date_utils_tools(app, active_data_source)
register_analysis_tools(app, active_data_source)
register_helpers_tools(app)
register_realtime_market_tools(app, ashare_data_source)
register_market_data_tools(app)

# --- Main Execution Block ---
if __name__ == "__main__":
    logger.info(
        f"Starting A-Share MCP Server via stdio... Today is {current_date}")
    # Run the server using stdio transport, suitable for MCP Hosts like Claude Desktop
    app.run(transport='stdio')