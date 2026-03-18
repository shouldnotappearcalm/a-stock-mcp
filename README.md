<div align="center">

# 📊 a-share-mcp 📈

<img src="https://img.shields.io/badge/A股数据-MCP%20工具-E6162D?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiB2aWV3Qm94PSIwIDAgMjQgMjQiPg0KPHBhdGggZmlsbD0iI2ZmZiIgZD0iTTggMTAuOGMwIDAgMC44LTEuNSAyLjQtMS41IDEuNyAwIDIuOCAxLjUgNC44IDEuNSAxLjcgMCAyLjgtMC42IDIuOC0wLjZ2LTIuMmMwIDAtMS4xIDEuMS0yLjggMS4xLTIgMC0zLjEtMS41LTQuOC0xLjUtMS42IDAtMi40IDAuOS0yLjQgMC45djIuM3pNOCAxNC44YzAgMCAwLjgtMS41IDIuNC0xLjUgMS43IDAgMi44IDEuNSA0LjggMS41IDEuNyAwIDIuOC0wLjYgMi44LTAuNnYtMi4yYzAgMC0xLjEgMS4xLTIuOCAxLjEtMiAwLTMuMS0xLjUtNC44LTEuNS0xLjYgMC0yLjQgMC45LTIuNCAwLjl2Mi4zeiI+PC9wYXRoPg0KPC9zdmc+">

[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square&logo=opensourceinitiative)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Package Manager](https://img.shields.io/badge/uv-package%20manager-5A45FF?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDEuNUwxIDEyLjVIMjNMMTIgMS41WiIgZmlsbD0id2hpdGUiLz4KPHBhdGggZD0iTTEyIDIyLjVMMSAxMS41SDIzTDEyIDIyLjVaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://github.com/astral-sh/uv)
[![MCP](https://img.shields.io/badge/MCP-Protocol-FF6B00?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48cGF0aCBkPSJNMTIgMkM2LjQ4NiAyIDIgNi40ODYgMiAxMnM0LjQ4NiAxMCAxMCAxMHMxMC00LjQ4NiAxMC0xMFMxNy41MTQgMiAxMiAyem0tMSAxNHY1LjI1QTguMDA4IDguMDA4IDAgMCAxIDQuNzUgMTZ6bTIgMGg2LjI1QTguMDA4IDguMDA4IDAgMCAxIDEzIDE2em0xLTJWOWg1LjI1QTguMDIgOC4wMiAwIDAAxIDE0IDE0em0tMiAwSDYuNzVBOC4wMiA4LjAyIDAgMDEgMTEgMTR6bTAtNlY0Ljc1QTguMDA4IDguMDA4IDAgMCAxIDE5LjI1IDh6TTEwIDh2NUg0Ljc1QTguMDA3IDguMDA3IDAgMCAxIDEwIDh6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==)](https://github.com/model-context-protocol/mcp-spec)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,15,20,24&height=200&section=header&text=A%20股%20MCP&fontSize=80&fontAlignY=35&desc=基于%20Model%20Context%20Protocol%20(MCP)&descAlignY=60&animation=fadeIn" />

</div>

A股 MCP 服务器，支持**实时行情**与历史数据查询。

本项目是一个专注于 A 股市场的 MCP 服务器，提供**盘中实时行情**、股票基本信息、历史 K 线数据、财务指标、宏观经济数据等多种查询功能。支持实时K线、技术指标计算（MACD/KDJ/RSI/BOLL等），理论上可以回答有关 A 股市场的任何问题，无论是针对大盘还是特定股票。

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 项目结构

```
a_share_mcp/
│
├── mcp_server.py           # 主服务器入口文件
├── pyproject.toml          # 项目依赖配置
├── README.md               # 项目说明文档
│
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── baostock_data_source.py   # Baostock数据源实现
│   ├── ashare_data_source.py     # Sina/Tencent数据源实现 (新增)
│   ├── data_source_interface.py  # 数据源接口定义
│   ├── utils.py                  # 通用工具函数
│   │
│   ├── formatting/         # 数据格式化模块
│   │   ├── __init__.py
│   │   └── markdown_formatter.py  # Markdown格式化工具
│   │
│   ├── use_cases/          # 业务逻辑层
│   │   ├── stock_market.py        # 股票市场业务逻辑
│   │   ├── realtime_market.py     # 实时行情业务逻辑 (重构)
│   │   ├── market_data.py         # 市场数据业务逻辑 (新增)
│   │   └── ...
│   │
│   └── tools/              # MCP工具模块
│       ├── __init__.py
│       ├── base.py                # 基础工具函数
│       ├── stock_market.py        # 股票市场数据工具
│       ├── realtime_market.py     # 实时行情数据工具 (重构)
│       ├── market_data.py         # 市场数据工具 (新增)
│       ├── financial_reports.py   # 财务报表工具
│       ├── indices.py             # 指数相关工具
│       ├── market_overview.py     # 市场概览工具
│       ├── macroeconomic.py       # 宏观经济数据工具
│       ├── date_utils.py          # 日期工具
│       └── analysis.py            # 分析工具
│
└── resource/               # 资源文件
    └── img/                # 图片资源
        ├── img_1.png       # CherryStudio配置示例
        └── img_2.png       # CherryStudio配置示例
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 功能特点

<div align="center">
<table>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/stocks-growth.png" width="30px"/><br><b>股票基础数据</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/line-chart.png" width="30px"/><br><b>历史行情数据</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/bonds.png" width="30px"/><br><b>财务报表数据</b></td>
  </tr>
  <tr>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/economic-improvement.png" width="30px"/><br><b>宏观经济数据</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/statistics.png" width="30px"/><br><b>指数成分股</b></td>
    <td align="center"><img src="https://img.icons8.com/fluency/48/null/fine-print.png" width="30px"/><br><b>数据分析报告</b></td>
  </tr>
  <tr>
    <td align="center" colspan="3"><img src="https://img.icons8.com/fluency/48/null/realtime.png" width="30px"/><br><b>实时行情数据 (新增)</b></td>
  </tr>
</table>
</div>

### 🆕 实时行情数据

- **实时行情快照**: 用分钟K线聚合今日数据，日期和涨跌幅语义正确
- **当日分钟K线**: 获取今日 1/5/15/30/60 分钟K线数据
- **批量查询**: 一次查询多只股票，按涨跌幅排序
- **实时K线**: 支持历史 K 线数据，包括 1/5/15/30/60 分钟线、日线、周线、月线
- **技术指标**: MACD, KDJ, RSI, BOLL, MA 等 12+ 种技术指标实时计算
- **市场数据**: 热点板块、大盘指数、龙虎榜、北向资金、涨跌停统计等
- **数据源**: Sina/Tencent 双核心封装，无需登录，盘中即时更新

## 先决条件

1. **Python 环境**: Python 3.10+
2. **依赖管理**: 使用 `uv` 包管理器安装依赖
3. **数据来源**: 基于 Baostock 数据源 + 腾讯/新浪实时数据源，无需付费账号

## 数据更新时间

### 📊 Baostock 历史数据（延迟数据）

> 以下是 Baostock 官方数据更新时间，请注意查询最新数据时的时间点 [Baostock 官网](http://baostock.com/baostock/index.php/%E9%A6%96%E9%A1%B5)

**每日数据更新时间：**

- 当前交易日 17:30，完成日 K 线数据入库
- 当前交易日 18:00，完成复权因子数据入库
- 第二自然日 11:00，完成分钟 K 线数据入库
- 第二自然日 1:30，完成前交易日"其它财务报告数据"入库
- 周六 17:30，完成周线数据入库

**每周数据更新时间：**

- 每周一下午，完成上证 50 成份股、沪深 300 成份股、中证 500 成份股信息数据入库

> 所以说，在交易日的当天，如果是在 17:30 之前询问当天的数据，是无法获取到的。

### 🟢 实时行情数据（盘中即时）

> 新增的实时行情工具使用腾讯/新浪数据源，**盘中即时更新，无需等待**。

**实时数据特点：**

- **盘中即时**: 交易时间内数据实时更新
- **无需登录**: 直接通过公开 API 获取
- **支持分钟线**: 1/5/15/30/60 分钟 K 线盘中可用
- **技术指标**: 基于实时数据计算，盘中可分析

**适用场景：**

- 需要当日盘中实时价格
- 需要分钟级别 K 线数据
- 需要实时技术指标分析

## 安装环境

在项目根目录下执行：

```bash
# 1. 创建虚拟环境
uv venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装所有依赖
uv sync
```

## 使用：在 MCP 客户端中配置服务器

在支持 MCP 的客户端（如 Chatbox、VS Code 插件、CherryStudio 等）中，你需要配置如何启动此服务器。 **推荐使用 `uv`**。

### 方法一：使用 JSON 配置的 IDE (例如 Cursor、VSCode、Trae 等)

对于需要编辑 JSON 文件来配置 MCP 服务器的客户端，你需要找到对应的能配置 MCP 的地方（各个 IDE 和桌面 MCP Client 可能都不一样），并在 `mcpServers` 对象中添加一个新的条目。

**JSON 配置示例 (请将路径替换为你的实际绝对路径):**

```json
{
  "mcpServers": {
    "a-share-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/YourName/Projects/a-share-mcp",
        "run",
        "python",
        "mcp_server.py"
      ],
      "transport": "stdio"
    }
  }
}
```

**注意事项:**

- **`command`**: 确保 `uv` 命令可以正常执行（可通过 `which uv` 检查路径）
- **`args`**: 确保参数列表完整且顺序正确
- **路径**: macOS/Linux 使用正斜杠 `/` 作为目录分隔符

### 方法二：在 Chatbox 中配置 (推荐)

Chatbox 也支持通过 `stdio` 启动本地 MCP 服务器。配置思路与上面的 JSON 一致，核心是：

- **传输方式**：`stdio`
- **命令**：`uv`
- **参数**：`--directory <a-share-mcp 绝对路径> run python mcp_server.py`

在 Chatbox 的 MCP 配置界面中：

- 新增一个 MCP 服务器，名称例如：`a-share-mcp`
- 选择 **Transport / 传输方式** 为 `stdio`
- 在 **Command** 中填：`uv`
- 在 **Args / 参数** 中按顺序填入：
  1. `--directory`
  2. `/Users/YourName/Projects/a-share-mcp`（替换为你本地的仓库路径）
  3. `run`
  4. `python`
  5. `mcp_server.py`

如果你已经在 Chatbox 中配置了其他 MCP（例如 `cherrystudio`），**建议把 `a-share-mcp` 这一条放在它们前面**，这样在问 A 股相关问题时，更优先使用本地的 a-share 数据源。

### 方法三：使用 CherryStudio

在 CherryStudio 的 MCP 服务器配置界面中，按如下方式填写：

- **名称**: `a-share-mcp` (或自定义)
- **描述**: `本地 A 股 MCP 服务器` (或自定义)
- **类型**: 选择 **标准输入/输出 (stdio)**
- **命令**: `uv`
- **包管理源**: 默认
- **参数**:

  1. `--directory`
  2. `/Users/YourName/Projects/a-share-mcp`
  3. `run`
  4. `python`
  5. `mcp_server.py`

- **环境变量**: (通常留空)

**CherryStudio 使用示例:**

![CherryStudio配置示例1](resource/img/img_1.png)

![CherryStudio配置示例2](resource/img/img_2.png)

## 工具列表

该 MCP 服务器目前提供 **53** 个工具，覆盖股票、财报、宏观、日期分析、实时行情等全方位数据。以下是完整列表：

<div align="center">
  <details>
    <summary><b>🔍 展开查看全部工具</b></summary>
    <br>
    <table>
      <tr>
        <th>🏛️ 股票市场数据 (Stock)</th>
        <th>📊 财务报表数据 (Finance)</th>
      </tr>
      <tr valign="top">
        <td>
          <ul>
            <li><code>get_historical_k_data</code> (历史K线)</li>
            <li><code>get_stock_basic_info</code> (基础信息)</li>
            <li><code>get_dividend_data</code> (分红配送)</li>
            <li><code>get_adjust_factor_data</code> (复权因子)</li>
          </ul>
        </td>
        <td>
          <ul>
            <li><code>get_profit_data</code> (盈利能力)</li>
            <li><code>get_operation_data</code> (营运能力)</li>
            <li><code>get_growth_data</code> (成长能力)</li>
            <li><code>get_balance_data</code> (资产负债)</li>
            <li><code>get_cash_flow_data</code> (现金流量)</li>
            <li><code>get_dupont_data</code> (杜邦分析)</li>
            <li><code>get_performance_express_report</code> (业绩快报)</li>
            <li><code>get_forecast_report</code> (业绩预告)</li>
            <li><code>get_fina_indicator</code> (财务指标汇总)</li>
          </ul>
        </td>
      </tr>
      <tr>
        <th colspan="2">🟢 实时行情数据 (Realtime) 🆕</th>
      </tr>
      <tr valign="top">
        <td colspan="2">
          <ul>
            <li><code>get_realtime_quote</code> (实时行情快照) - 今日价格、涨跌幅、市场状态</li>
            <li><code>get_intraday_minute_kline</code> (当日分钟K线) 🆕 - 今日 1/5/15/30/60 分钟K线</li>
            <li><code>get_realtime_multi_quote</code> (批量查询) 🆕 - 多只股票批量查询，按涨跌幅排序</li>
            <li><code>get_realtime_kline</code> (K线数据) - 历史 K 线，支持分钟/日线/周线/月线</li>
            <li><code>get_technical_indicators</code> (技术指标) - MACD/KDJ/RSI/BOLL 等 12+ 指标</li>
            <li><code>get_market_index</code> (大盘指数) - 上证/深证/创业板/科创50</li>
            <li><code>get_hot_sectors</code> (热点板块) - 概念板块涨幅榜</li>
            <li><code>get_lhb_detail</code> (龙虎榜) - 龙虎榜详情数据</li>
            <li><code>get_north_money</code> (北向资金) - 沪深股通资金流向</li>
            <li><code>get_limit_up_down</code> (涨跌停统计) - 当日涨停跌停数量</li>
            <li><code>get_limit_up_pool</code> (涨停股池) - 涨停股详情列表</li>
            <li><code>get_limit_down_pool</code> (跌停股池) - 跌停股详情列表</li>
            <li><code>get_stock_money_flow</code> (个股资金流向) - 主力/大单/小单净流入</li>
            <li><code>get_consecutive_limit_up</code> (连板股) - 连续涨停股统计</li>
          </ul>
        </td>
      </tr>
      <tr>
        <th>🔎 市场 & 指数 (Market & Index)</th>
        <th>🌐 宏观 & 其它 (Macro & Utils)</th>
      </tr>
      <tr valign="top">
        <td>
          <ul>
            <li><code>get_trade_dates</code> (交易日历)</li>
            <li><code>get_all_stock</code> (全市场证券)</li>
            <li><code>search_stocks</code> (股票搜索)</li>
            <li><code>get_suspensions</code> (停牌信息)</li>
            <li><code>get_stock_industry</code> (行业分类)</li>
            <li><code>get_index_constituents</code> (指数成分)</li>
            <li><code>get_sz50_stocks</code> (上证50)</li>
            <li><code>get_hs300_stocks</code> (沪深300)</li>
            <li><code>get_zz500_stocks</code> (中证500)</li>
            <li><code>list_industries</code> (行业列表)</li>
            <li><code>get_industry_members</code> (行业个股)</li>
          </ul>
        </td>
        <td>
          <ul>
            <li><code>get_deposit_rate_data</code> (存款利率)</li>
            <li><code>get_loan_rate_data</code> (贷款利率)</li>
            <li><code>get_required_reserve_ratio_data</code> (存款准备金)</li>
            <li><code>get_money_supply_data_month</code> (货币供应月)</li>
            <li><code>get_money_supply_data_year</code> (货币供应年)</li>
            <li><code>get_latest_trading_date</code> (最新交易日)</li>
            <li><code>get_market_analysis_timeframe</code> (智能分析周期)</li>
            <li><code>is_trading_day</code> (判断交易日)</li>
            <li><code>previous_trading_day</code> (上一交易日)</li>
            <li><code>next_trading_day</code> (下一交易日)</li>
            <li><code>get_last_n_trading_days</code> (最近N日)</li>
            <li><code>get_recent_trading_range</code> (近期范围)</li>
            <li><code>get_month_end_trading_dates</code> (月末交易日)</li>
            <li><code>get_stock_analysis</code> (生成分析报告)</li>
            <li><code>normalize_stock_code</code> (代码标准化)</li>
            <li><code>normalize_index_code</code> (指数代码标准化)</li>
            <li><code>list_tool_constants</code> (常量查询)</li>
          </ul>
        </td>
      </tr>
    </table>
  </details>
</div>

## 贡献指南

欢迎提交 Issue 或 Pull Request 来帮助改进项目。贡献前请先查看现有 Issue 和文档。

## 许可证

本项目采用 MIT 许可证 - 详情请查看 LICENSE 文件

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,15,20,24&section=footer&height=100&animation=fadeIn" />
</div>
