"""
Market data use cases for stock market analysis.
Provides market-wide data using Akshare and technical indicators using MyTT.
"""
import sys
import os
from typing import Optional, List
from datetime import datetime, timedelta

# Add Ashare library path for MyTT
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
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '60m': '60m',
    '1d': '1d',
    '1w': '1w',
    '1M': '1M',
}


def normalize_code(code: str) -> str:
    """
    Normalize stock code to Ashare format.
    Supports formats: sh600000, 600000, sh.600000, sz000001, 000001.XSHE, 600519.XSHG
    """
    code = code.strip()
    
    if '.' in code:
        parts = code.split('.')
        if len(parts) == 2:
            prefix, suffix = parts[0].lower(), parts[1].upper()
            if prefix in ('sh', 'sz') and suffix.isdigit():
                return f"{prefix}{suffix}"
            if suffix == 'XSHG':
                return f"sh{prefix}"
            if suffix == 'XSHE':
                return f"sz{prefix}"
    
    if code.startswith('sh') or code.startswith('sz'):
        return code
    
    if code.isdigit():
        if code.startswith('6'):
            return f"sh{code}"
        elif code.startswith(('0', '2', '3')):
            return f"sz{code}"
    
    return code


def fetch_realtime_kline(
    code: str,
    frequency: str = '1d',
    count: int = 60,
    format: str = 'markdown',
) -> str:
    """
    Fetch realtime K-line data for a stock.
    
    Args:
        code: Stock code (supports multiple formats)
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
        
        df = df.reset_index()
        df.columns = ['time', 'open', 'close', 'high', 'low', 'volume']
        
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
        frequency: K-line frequency
        count: Number of K-line bars to fetch (default 120)
        indicators: List of indicators: 'MA', 'EMA', 'MACD', 'KDJ', 'RSI', 'WR', 'BOLL', 'BIAS', 'CCI', 'ATR', 'DMI', 'TAQ'
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
        
        CLOSE = df['close'].values
        OPEN = df['open'].values
        HIGH = df['high'].values
        LOW = df['low'].values
        VOL = df['volume'].values if 'volume' in df.columns else None
        
        result_df = df.reset_index()
        result_df.columns = ['time', 'open', 'close', 'high', 'low', 'volume']
        
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


def fetch_hot_sectors(
    top_n: int = 20,
    format: str = 'markdown',
) -> str:
    """
    Fetch hot concept sectors with top gains using Akshare.
    
    Args:
        top_n: Number of top sectors to return (default 20)
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    try:
        df = ak.stock_board_concept_name_em()
        
        if df is None or df.empty:
            return "获取热点板块数据失败"
        
        df = df.sort_values(by='涨跌幅', ascending=False).head(top_n)
        
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
    """
    validate_output_format(format)
    
    try:
        df = ak.stock_zh_index_spot_sina()
        
        if df is None or df.empty:
            return "获取大盘指数数据失败"
        
        major_indices = ['sh000001', 'sh000002', 'sz399001', 'sz399006', 'sh000688']
        df_filtered = df[df['代码'].isin(major_indices)]
        
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
    """
    validate_output_format(format)
    
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
    
    try:
        df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
        
        if df is None or df.empty:
            return f"未找到 {start_date} 至 {end_date} 的龙虎榜数据"
        
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
        
        available_cols = [c for c in columns_map.keys() if c in df.columns]
        df_result = df[available_cols].copy()
        df_result.columns = [columns_map[c] for c in available_cols]
        
        amount_cols = ['净买额(万)', '买入额(万)', '卖出额(万)']
        for col in amount_cols:
            if col in df_result.columns:
                df_result[col] = (df_result[col] / 1e4).round(2)
        
        for col in ['收盘价', '涨跌幅(%)', '换手率(%)']:
            if col in df_result.columns:
                df_result[col] = df_result[col].round(2)
        
        if '上榜日期' in df_result.columns:
            df_result['上榜日期'] = df_result['上榜日期'].astype(str).str[:10]
        
        df_result = df_result.head(top_n)
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
    """
    validate_output_format(format)
    
    try:
        df = ak.stock_hsgt_fund_flow_summary_em()
        
        if df is None or df.empty:
            return "获取北向资金数据失败"
        
        df_north = df[df['资金方向'] == '北向'].copy()
        
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
    """
    validate_output_format(format)
    
    try:
        today = datetime.now().strftime("%Y%m%d")
        
        df_up = ak.stock_zt_pool_em(date=today)
        limit_up_count = len(df_up) if df_up is not None else 0
        
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


def fetch_limit_up_pool(
    date: Optional[str] = None,
    top_n: int = 30,
    format: str = 'markdown',
) -> str:
    """
    Fetch limit up stocks pool (涨停股池).
    
    Args:
        date: Date in format 'YYYYMMDD' (default: today)
        top_n: Number of stocks to return (default 30)
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_em(date=date)
        
        if df is None or df.empty:
            return f"未找到 {date} 的涨停股数据"
        
        df_result = df[['序号', '代码', '名称', '涨跌幅', '最新价', '成交额', '流通市值', 
                        '换手率', '封板资金', '首次封板时间', '最后封板时间', '炸板次数', 
                        '连板数', '所属行业']].head(top_n).copy()
        
        df_result.columns = ['序号', '代码', '名称', '涨跌幅(%)', '最新价', '成交额', 
                             '流通市值', '换手率(%)', '封板资金', '首次封板', '最后封板', 
                             '炸板次数', '连板数', '所属行业']
        
        df_result['涨跌幅(%)'] = df_result['涨跌幅(%)'].round(2)
        df_result['最新价'] = df_result['最新价'].round(2)
        df_result['换手率(%)'] = df_result['换手率(%)'].round(2)
        df_result['成交额'] = (df_result['成交额'] / 1e8).round(2)
        df_result['流通市值'] = (df_result['流通市值'] / 1e8).round(2)
        
        df_result = df_result.rename(columns={'成交额': '成交额(亿)', '流通市值': '流通市值(亿)'})
        
        meta = {
            'date': date,
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=top_n, meta=meta)
        
    except Exception as e:
        return f"获取涨停股池失败: {str(e)}"


def fetch_limit_down_pool(
    date: Optional[str] = None,
    top_n: int = 30,
    format: str = 'markdown',
) -> str:
    """
    Fetch limit down stocks pool (跌停股池).
    
    Args:
        date: Date in format 'YYYYMMDD' (default: today)
        top_n: Number of stocks to return (default 30)
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)
        
        if df is None or df.empty:
            return f"未找到 {date} 的跌停股数据"
        
        df_result = df[['序号', '代码', '名称', '涨跌幅', '最新价', '成交额', '流通市值', 
                        '换手率']].head(top_n).copy()
        
        df_result.columns = ['序号', '代码', '名称', '涨跌幅(%)', '最新价', '成交额', 
                             '流通市值', '换手率(%)']
        
        df_result['涨跌幅(%)'] = df_result['涨跌幅(%)'].round(2)
        df_result['最新价'] = df_result['最新价'].round(2)
        df_result['换手率(%)'] = df_result['换手率(%)'].round(2)
        df_result['成交额'] = (df_result['成交额'] / 1e8).round(2)
        df_result['流通市值'] = (df_result['流通市值'] / 1e8).round(2)
        
        df_result = df_result.rename(columns={'成交额': '成交额(亿)', '流通市值': '流通市值(亿)'})
        
        meta = {
            'date': date,
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=top_n, meta=meta)
        
    except Exception as e:
        return f"获取跌停股池失败: {str(e)}"


def fetch_stock_money_flow(
    code: str,
    top_n: int = 10,
    format: str = 'markdown',
) -> str:
    """
    Fetch individual stock money flow data (个股资金流向).
    
    Args:
        code: Stock code (e.g., '600519' or 'sh600519')
        top_n: Number of recent days to return (default 10)
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    normalized = normalize_code(code)
    market = 'sh' if normalized.startswith('sh') else 'sz'
    clean_code = normalized[2:]
    
    try:
        df = ak.stock_individual_fund_flow(stock=clean_code, market=market)
        
        if df is None or df.empty:
            return f"未找到股票 {code} 的资金流向数据"
        
        df_result = df.tail(top_n).copy()
        df_result = df_result.iloc[::-1]
        
        df_result = df_result[['日期', '收盘价', '涨跌幅', '主力净流入-净额', '主力净流入-净占比',
                               '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额', 
                               '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比',
                               '小单净流入-净额', '小单净流入-净占比']].copy()
        
        df_result.columns = ['日期', '收盘价', '涨跌幅(%)', '主力净额(万)', '主力占比(%)',
                             '超大单净额(万)', '超大单占比(%)', '大单净额(万)', 
                             '大单占比(%)', '中单净额(万)', '中单占比(%)',
                             '小单净额(万)', '小单占比(%)']
        
        for col in ['主力净额(万)', '超大单净额(万)', '大单净额(万)', '中单净额(万)', '小单净额(万)']:
            df_result[col] = (df_result[col] / 1e4).round(2)
        
        for col in ['收盘价', '涨跌幅(%)', '主力占比(%)', '超大单占比(%)', '大单占比(%)', 
                    '中单占比(%)', '小单占比(%)']:
            df_result[col] = df_result[col].round(2)
        
        df_result.insert(0, '序号', range(1, len(df_result) + 1))
        
        meta = {
            'code': code,
            'normalized_code': normalized,
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=top_n, meta=meta)
        
    except Exception as e:
        return f"获取资金流向失败: {str(e)}"


def fetch_consecutive_limit_up(
    date: Optional[str] = None,
    top_n: int = 30,
    format: str = 'markdown',
) -> str:
    """
    Fetch consecutive limit up stocks (连板股).
    
    Args:
        date: Date in format 'YYYYMMDD' (default: today)
        top_n: Number of stocks to return (default 30)
        format: Output format: 'markdown' | 'json' | 'csv'
    """
    validate_output_format(format)
    
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_previous_em(date=date)
        
        if df is None or df.empty:
            return f"未找到 {date} 的连板股数据"
        
        df_result = df[['序号', '代码', '名称', '涨跌幅', '最新价', '成交额', 
                        '换手率', '昨日连板数', '涨停统计', '所属行业']].head(top_n).copy()
        
        df_result.columns = ['序号', '代码', '名称', '涨跌幅(%)', '最新价', '成交额', 
                             '换手率(%)', '连板数', '涨停统计', '所属行业']
        
        df_result['涨跌幅(%)'] = df_result['涨跌幅(%)'].round(2)
        df_result['最新价'] = df_result['最新价'].round(2)
        df_result['换手率(%)'] = df_result['换手率(%)'].round(2)
        df_result['成交额'] = (df_result['成交额'] / 1e8).round(2)
        
        df_result = df_result.rename(columns={'成交额': '成交额(亿)'})
        
        meta = {
            'date': date,
            'data_source': '东方财富 (Akshare)',
            'fetch_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return format_table_output(df_result, format=format, max_rows=top_n, meta=meta)
        
    except Exception as e:
        return f"获取连板股失败: {str(e)}"
