"""Realtime market use cases for live stock data."""
import sys
import os
import json
import urllib.request
from typing import Optional, List
from datetime import datetime, timedelta

# Add Ashare library path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Ashare'))

import pandas as pd
import akshare as ak
from Ashare import get_price
from MyTT import (
    MA, EMA, MACD, KDJ, RSI, WR, BOLL, BIAS, CCI, ATR, 
    DMI, TAQ, TRIX, VR, EMV, DPO, BRAR, DMA, MTM, ROC, BBI
)

from src.formatting.markdown_formatter import format_table_output
from src.services.validation import validate_output_format


# Frequency mapping: user-friendly to Ashare format
FREQUENCY_MAP = {
    '1m': '1m',    # 1分钟
    '5m': '5m',    # 5分钟
    '15m': '15m',  # 15分钟
    '30m': '30m',  # 30分钟
    '60m': '60m',  # 60分钟
    '1d': '1d',    # 日线
    '1w': '1w',    # 周线
    '1M': '1M',    # 月线
}

# HTTP headers for external APIs
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.eastmoney.com",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def normalize_code(code: str) -> str:
    """
    Normalize stock code to Ashare format.
    Supports formats: sh600000, 600000, sh.600000, sz000001, 000001.XSHE, 600519.XSHG
    """
    code = code.strip()
    
    # Baostock format: sh.600000 -> sh600000 (handle this first before sh prefix check)
    if '.' in code:
        parts = code.split('.')
        if len(parts) == 2:
            prefix, suffix = parts[0].lower(), parts[1].upper()
            # Baostock format: sh.600000 or sz.000001
            if prefix in ('sh', 'sz') and suffix.isdigit():
                return f"{prefix}{suffix}"
            # JQ format: 600519.XSHG or 000001.XSHE
            if suffix == 'XSHG':
                return f"sh{prefix}"
            if suffix == 'XSHE':
                return f"sz{prefix}"
    
    # Already in correct format (sh/sz prefix with number)
    if code.startswith('sh') or code.startswith('sz'):
        return code
    
    # Pure number: determine exchange by code rules
    if code.isdigit():
        # 上海: 6开头
        if code.startswith('6'):
            return f"sh{code}"
        # 深圳: 0开头(主板), 3开头(创业板), 2开头(中小板)
        elif code.startswith(('0', '2', '3')):
            return f"sz{code}"
    
    return code


def _fetch_url(url: str, extra_headers: dict = None, timeout: int = 10) -> str:
    """Helper function to fetch URL content."""
    req = urllib.request.Request(url, headers=HEADERS)
    if extra_headers:
        for k, v in extra_headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception:
        return ""


def _get_turnover_from_eastmoney(code: str) -> dict:
    """Get turnover rate and amount from Eastmoney API."""
    normalized = normalize_code(code)
    market = 1 if normalized.startswith('sh') else 0
    clean_code = normalized[2:]
    
    url = (
        f"http://push2.eastmoney.com/api/qt/stock/get"
        f"?secid={market}.{clean_code}"
        f"&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f107,f169,f170,f171"
    )
    
    raw = _fetch_url(url, {"Referer": "https://www.eastmoney.com"})
    
    if raw:
        try:
            obj = json.loads(raw)
            d = obj.get("data", {}) or {}
            if d.get("f43"):
                return {
                    "turnover_rate": round(d.get("f171", 0) / 100, 2),
                    "amount_yi": round(d.get("f48", 0) / 1e8, 2),
                }
        except Exception:
            pass
    
    return {"turnover_rate": None, "amount_yi": None}


def fetch_realtime_kline(
    code: str,
    frequency: str = '1d',
    count: int = 60,
    format: str = 'markdown',
) -> str:
    """
    Fetch realtime K-line data for a stock.
    
    Args:
        code: Stock code (supports multiple formats: sh600000, 600000, sh.600000, 600519.XSHG)
        frequency: K-line frequency. Options: '1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M'
        count: Number of K-line bars to fetch (default 60)
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    if frequency not in FREQUENCY_MAP:
        raise ValueError(f"Invalid frequency '{frequency}'. Valid options: {list(FREQUENCY_MAP.keys())}")
    
    normalized_code = normalize_code(code)
    ashare_freq = FREQUENCY_MAP[frequency]
    
    try:
        df = get_price(normalized_code, frequency=ashare_freq, count=count)
        
        if df is None or df.empty:
            return f"未找到股票 {code} 的数据"
        
        # Reset index for display
        df = df.reset_index()
        df.columns = ['time', 'open', 'close', 'high', 'low', 'volume']
        
        # Format numbers
        df['open'] = df['open'].round(2)
        df['close'] = df['close'].round(2)
        df['high'] = df['high'].round(2)
        df['low'] = df['low'].round(2)
        
        meta = {
            'code': code,
            'normalized_code': normalized_code,
            'frequency': frequency,
            'count': count,
            'data_source': 'Ashare (腾讯/新浪)',
        }
        
        return format_table_output(df, format=format, max_rows=count, meta=meta)
        
    except Exception as e:
        return f"获取实时K线数据失败: {str(e)}"


def fetch_technical_indicators(
    code: str,
    frequency: str = '1d',
    count: int = 120,
    indicators: Optional[List[str]] = None,
    format: str = 'markdown',
) -> str:
    """
    Calculate technical indicators for a stock.
    
    Args:
        code: Stock code
        frequency: K-line frequency. Options: '1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M'
        count: Number of K-line bars to fetch (default 120 for accurate indicator calculation)
        indicators: List of indicators to calculate. 
                    Options: 'MA', 'EMA', 'MACD', 'KDJ', 'RSI', 'WR', 'BOLL', 'BIAS', 'CCI', 'ATR', 'DMI', 'TAQ'
                    Default: ['MA', 'MACD', 'KDJ', 'BOLL', 'RSI']
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    if frequency not in FREQUENCY_MAP:
        raise ValueError(f"Invalid frequency '{frequency}'. Valid options: {list(FREQUENCY_MAP.keys())}")
    
    if indicators is None or len(indicators) == 0:
        indicators = ['MA', 'MACD', 'KDJ', 'BOLL', 'RSI']
    
    normalized_code = normalize_code(code)
    ashare_freq = FREQUENCY_MAP[frequency]
    
    try:
        df = get_price(normalized_code, frequency=ashare_freq, count=count)
        
        if df is None or df.empty:
            return f"未找到股票 {code} 的数据"
        
        # Extract OHLCV data
        CLOSE = df['close'].values
        OPEN = df['open'].values
        HIGH = df['high'].values
        LOW = df['low'].values
        VOL = df['volume'].values if 'volume' in df.columns else None
        
        # Reset index and prepare result dataframe
        result_df = df.reset_index()
        result_df.columns = ['time', 'open', 'close', 'high', 'low', 'volume']
        
        # Calculate requested indicators
        calculated = []
        
        for ind in indicators:
            ind = ind.upper()
            
            if ind == 'MA':
                result_df['MA5'] = MA(CLOSE, 5)
                result_df['MA10'] = MA(CLOSE, 10)
                result_df['MA20'] = MA(CLOSE, 20)
                calculated.append('MA(5,10,20)')
                
            elif ind == 'EMA':
                result_df['EMA12'] = EMA(CLOSE, 12)
                result_df['EMA26'] = EMA(CLOSE, 26)
                calculated.append('EMA(12,26)')
                
            elif ind == 'MACD':
                DIF, DEA, MACD_val = MACD(CLOSE)
                result_df['MACD_DIF'] = DIF
                result_df['MACD_DEA'] = DEA
                result_df['MACD'] = MACD_val
                calculated.append('MACD(12,26,9)')
                
            elif ind == 'KDJ':
                K, D, J = KDJ(CLOSE, HIGH, LOW)
                result_df['KDJ_K'] = K
                result_df['KDJ_D'] = D
                result_df['KDJ_J'] = J
                calculated.append('KDJ(9,3,3)')
                
            elif ind == 'RSI':
                result_df['RSI'] = RSI(CLOSE)
                calculated.append('RSI(24)')
                
            elif ind == 'WR':
                WR1, WR2 = WR(CLOSE, HIGH, LOW)
                result_df['WR10'] = WR1
                result_df['WR6'] = WR2
                calculated.append('WR(10,6)')
                
            elif ind == 'BOLL':
                UP, MID, LOW_BOLL = BOLL(CLOSE)
                result_df['BOLL_UP'] = UP
                result_df['BOLL_MID'] = MID
                result_df['BOLL_LOW'] = LOW_BOLL
                calculated.append('BOLL(20,2)')
                
            elif ind == 'BIAS':
                BIAS1, BIAS2, BIAS3 = BIAS(CLOSE)
                result_df['BIAS6'] = BIAS1
                result_df['BIAS12'] = BIAS2
                result_df['BIAS24'] = BIAS3
                calculated.append('BIAS(6,12,24)')
                
            elif ind == 'CCI':
                result_df['CCI'] = CCI(CLOSE, HIGH, LOW)
                calculated.append('CCI(14)')
                
            elif ind == 'ATR':
                result_df['ATR'] = ATR(CLOSE, HIGH, LOW)
                calculated.append('ATR(20)')
                
            elif ind == 'DMI':
                PDI, MDI, ADX, ADXR = DMI(CLOSE, HIGH, LOW)
                result_df['DMI_PDI'] = PDI
                result_df['DMI_MDI'] = MDI
                result_df['DMI_ADX'] = ADX
                result_df['DMI_ADXR'] = ADXR
                calculated.append('DMI(14,6)')
                
            elif ind == 'TAQ':
                UP, MID, DOWN = TAQ(HIGH, LOW, 20)
                result_df['TAQ_UP'] = UP
                result_df['TAQ_MID'] = MID
                result_df['TAQ_DOWN'] = DOWN
                calculated.append('TAQ(20)')
        
        # Round numeric columns
        for col in result_df.columns:
            if result_df[col].dtype in ['float64', 'float32']:
                result_df[col] = result_df[col].round(2)
        
        meta = {
            'code': code,
            'normalized_code': normalized_code,
            'frequency': frequency,
            'indicators': ', '.join(calculated),
            'data_source': 'Ashare + MyTT',
        }
        
        return format_table_output(result_df, format=format, max_rows=min(count, 50), meta=meta)
        
    except Exception as e:
        return f"计算技术指标失败: {str(e)}"


def fetch_realtime_quote(
    code: str,
    format: str = 'markdown',
) -> str:
    """
    Fetch realtime quote snapshot for a stock.
    Returns the latest K-line data with key metrics including turnover rate.
    
    Args:
        code: Stock code
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    normalized_code = normalize_code(code)
    
    try:
        # Get latest daily data
        df_day = get_price(normalized_code, frequency='1d', count=5)
        
        if df_day is None or df_day.empty:
            return f"未找到股票 {code} 的数据"
        
        # Get latest minute data (if market is open)
        try:
            df_min = get_price(normalized_code, frequency='1m', count=5)
            has_intraday = df_min is not None and not df_min.empty
        except:
            has_intraday = False
        
        # Latest daily data
        latest = df_day.iloc[-1]
        prev = df_day.iloc[-2] if len(df_day) > 1 else None
        
        # Calculate change
        change = latest['close'] - prev['close'] if prev is not None else 0
        change_pct = (change / prev['close'] * 100) if prev is not None and prev['close'] > 0 else 0
        
        result = {
            '代码': code,
            '日期': str(latest.name)[:10] if hasattr(latest, 'name') else '',
            '开盘价': round(latest['open'], 2),
            '最高价': round(latest['high'], 2),
            '最低价': round(latest['low'], 2),
            '收盘价': round(latest['close'], 2),
            '成交量': int(latest['volume']),
            '涨跌额': round(change, 2),
            '涨跌幅(%)': round(change_pct, 2),
        }
        
        # Get turnover rate from Eastmoney
        extra_data = _get_turnover_from_eastmoney(code)
        if extra_data.get('turnover_rate') is not None:
            result['换手率(%)'] = extra_data['turnover_rate']
        if extra_data.get('amount_yi') is not None:
            result['成交额(亿)'] = extra_data['amount_yi']
        
        if has_intraday:
            latest_min = df_min.iloc[-1]
            result['最新价(分钟)'] = round(latest_min['close'], 2)
        
        df_result = pd.DataFrame([result])
        
        meta = {
            'code': code,
            'normalized_code': normalized_code,
            'data_source': 'Ashare + 东方财富',
        }
        
        return format_table_output(df_result, format=format, max_rows=1, meta=meta)
        
    except Exception as e:
        return f"获取实时行情失败: {str(e)}"


def fetch_hot_sectors(
    top_n: int = 20,
    format: str = 'markdown',
) -> str:
    """
    Fetch hot concept sectors with top gains using Akshare.
    
    Args:
        top_n: Number of top sectors to return (default 20)
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Hot concept sectors sorted by change percentage.
    """
    validate_output_format(format)
    
    try:
        # Get concept board data from Akshare
        df = ak.stock_board_concept_name_em()
        
        if df is None or df.empty:
            return "获取热点板块数据失败"
        
        # Sort by change rate and get top N
        df = df.sort_values(by='涨跌幅', ascending=False).head(top_n)
        
        # Prepare result
        results = []
        for i, (_, row) in enumerate(df.iterrows(), 1):
            results.append({
                '排名': i,
                '板块名称': row.get('板块名称', ''),
                '板块代码': row.get('板块代码', ''),
                '涨跌幅(%)': round(row.get('涨跌幅', 0), 2),
                '总市值(亿)': round(row.get('总市值', 0) / 1e8, 2) if row.get('总市值') else 0,
                '换手率(%)': round(row.get('换手率', 0), 2) if row.get('换手率') else 0,
            })
        
        df_result = pd.DataFrame(results)
        
        meta = {
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=top_n, meta=meta)
        
    except Exception as e:
        return f"获取热点板块数据失败: {str(e)}"


def fetch_market_index(
    format: str = 'markdown',
) -> str:
    """
    Fetch realtime market index data using Akshare.
    
    Args:
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Realtime data for major market indices.
    """
    validate_output_format(format)
    
    try:
        # Get index data from Akshare (Sina source)
        df = ak.stock_zh_index_spot_sina()
        
        if df is None or df.empty:
            return "获取大盘指数数据失败"
        
        # Filter major indices
        major_indices = ['sh000001', 'sh000002', 'sz399001', 'sz399006', 'sh000688']
        df_filtered = df[df['代码'].isin(major_indices)]
        
        # Prepare result
        results = []
        name_map = {
            'sh000001': '上证指数',
            'sh000002': 'A股指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000688': '科创50',
        }
        
        for _, row in df_filtered.iterrows():
            code = row.get('代码', '')
            results.append({
                '指数名称': row.get('名称', name_map.get(code, '')),
                '代码': code,
                '当前点位': round(float(row.get('今开', 0)), 2),
                '最新价': round(float(row.get('最新价', 0)), 2),
                '涨跌额': round(float(row.get('涨跌额', 0)), 2),
                '涨跌幅(%)': round(float(row.get('涨跌幅', 0)), 2),
            })
        
        df_result = pd.DataFrame(results)
        
        meta = {
            'data_source': '新浪财经 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=10, meta=meta)
        
    except Exception as e:
        return f"获取大盘指数数据失败: {str(e)}"


def fetch_lhb_detail(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    top_n: int = 20,
    format: str = 'markdown',
) -> str:
    """
    Fetch Long-Hu-Bang (龙虎榜) detail data.
    
    Args:
        start_date: Start date in format 'YYYYMMDD' (default: 3 days ago)
        end_date: End date in format 'YYYYMMDD' (default: today)
        top_n: Number of records to return (default 20)
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Long-Hu-Bang data including stock code, name, net buy amount, buy/sell amounts, and reason.
    """
    validate_output_format(format)
    
    # Default date range
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
    
    try:
        df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
        
        if df is None or df.empty:
            return f"未找到 {start_date} 至 {end_date} 的龙虎榜数据"
        
        # Select and rename columns
        columns_map = {
            '代码': '代码',
            '名称': '名称',
            '上榜日': '上榜日期',
            '收盘价': '收盘价',
            '涨跌幅': '涨跌幅(%)',
            '龙虎榜净买额': '净买额(万)',
            '龙虎榜买入额': '买入额(万)',
            '龙虎榜卖出额': '卖出额(万)',
            '上榜原因': '上榜原因',
            '解读': '解读',
            '换手率': '换手率(%)',
            '流通市值': '流通市值',
        }
        
        # Keep only existing columns
        available_cols = [c for c in columns_map.keys() if c in df.columns]
        df_result = df[available_cols].copy()
        
        # Rename columns
        df_result.columns = [columns_map[c] for c in available_cols]
        
        # Convert amounts to 万元
        amount_cols = ['净买额(万)', '买入额(万)', '卖出额(万)']
        for col in amount_cols:
            if col in df_result.columns:
                df_result[col] = (df_result[col] / 1e4).round(2)
        
        # Round other numeric columns
        for col in ['收盘价', '涨跌幅(%)', '换手率(%)']:
            if col in df_result.columns:
                df_result[col] = df_result[col].round(2)
        
        # Convert date to string
        if '上榜日期' in df_result.columns:
            df_result['上榜日期'] = df_result['上榜日期'].astype(str).str[:10]
        
        # Limit rows
        df_result = df_result.head(top_n)
        
        # Add row number
        df_result.insert(0, '序号', range(1, len(df_result) + 1))
        
        meta = {
            'start_date': start_date,
            'end_date': end_date,
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=top_n, meta=meta)
        
    except Exception as e:
        return f"获取龙虎榜数据失败: {str(e)}"


def fetch_north_money(
    format: str = 'markdown',
) -> str:
    """
    Fetch northbound money flow data (北向资金) using Akshare.
    
    Args:
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Northbound money flow data including daily inflow/outflow.
    """
    validate_output_format(format)
    
    try:
        # Get northbound money summary
        df = ak.stock_hsgt_fund_flow_summary_em()
        
        if df is None or df.empty:
            return "获取北向资金数据失败"
        
        # Filter northbound data
        df_north = df[df['资金方向'] == '北向'].copy()
        
        # Prepare result
        results = []
        for _, row in df_north.iterrows():
            results.append({
                '日期': row.get('交易日', ''),
                '板块': row.get('板块', ''),
                '成交净买额(亿)': round(row.get('成交净买额', 0), 2),
                '资金净流入(亿)': round(row.get('资金净流入', 0), 2),
                '相关指数': row.get('相关指数', ''),
                '指数涨跌幅(%)': round(row.get('指数涨跌幅', 0), 2),
            })
        
        df_result = pd.DataFrame(results)
        
        meta = {
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=5, meta=meta)
        
    except Exception as e:
        return f"获取北向资金数据失败: {str(e)}"


def fetch_limit_up_down(
    format: str = 'markdown',
) -> str:
    """
    Fetch daily limit up and limit down statistics (涨跌停统计) using Akshare.
    
    Args:
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Statistics on limit up and limit down stocks.
    """
    validate_output_format(format)
    
    try:
        today = datetime.now().strftime("%Y%m%d")
        
        # Get limit up stocks
        df_up = ak.stock_zt_pool_em(date=today)
        limit_up_count = len(df_up) if df_up is not None else 0
        
        # Get limit down stocks
        try:
            df_down = ak.stock_zt_pool_dtgc_em(date=today)
            limit_down_count = len(df_down) if df_down is not None else 0
        except:
            limit_down_count = 0
        
        result = [{
            '日期': datetime.now().strftime("%Y-%m-%d"),
            '涨停数量': limit_up_count,
            '跌停数量': limit_down_count,
        }]
        
        df = pd.DataFrame(result)
        
        meta = {
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df, format=format, max_rows=1, meta=meta)
        
    except Exception as e:
        return f"获取涨跌停统计失败: {str(e)}"
