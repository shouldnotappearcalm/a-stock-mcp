"""
Realtime quote use cases for live stock data.
Provides real-time quotes using minute K-line aggregation.
"""
from datetime import datetime, date, time
from typing import List

import pandas as pd

from src.ashare_data_source import AshareDataSource
from src.formatting.markdown_formatter import format_table_output
from src.services.validation import validate_output_format


def _get_market_status() -> str:
    """
    Determine current market status.
    
    Returns:
        'trading': 当前交易时段
        'closed': 休市
        'pre_market': 盘前
        'post_market': 盘后
    """
    now = datetime.now()
    current_time = now.time()
    
    # Weekend
    if now.weekday() >= 5:
        return 'closed'
    
    # Trading hours: 9:30-11:30, 13:00-15:00
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    if morning_start <= current_time <= morning_end:
        return 'trading'
    elif afternoon_start <= current_time <= afternoon_end:
        return 'trading'
    elif time(9, 0) <= current_time < morning_start:
        return 'pre_market'
    elif current_time > afternoon_end:
        return 'post_market'
    else:
        return 'closed'


def _aggregate_intraday_data(df_min: pd.DataFrame, today: date) -> dict:
    """
    Aggregate minute K-line data to today's summary.
    
    Args:
        df_min: Minute K-line DataFrame
        today: Today's date
    
    Returns:
        Dict with today's OHLCV summary
    """
    # Filter today's data
    df_today = df_min[df_min.index.date == today].copy()
    
    if df_today.empty:
        return None
    
    return {
        'open': df_today.iloc[0]['open'],
        'high': df_today['high'].max(),
        'low': df_today['low'].min(),
        'close': df_today.iloc[-1]['close'],
        'volume': df_today['volume'].sum(),
    }


def fetch_realtime_quote(
    ashare_data_source: AshareDataSource,
    code: str,
    format: str = 'markdown',
) -> str:
    """
    Fetch realtime quote snapshot for a stock.
    
    Core fix: Use minute K-line aggregation for today's data instead of daily data.
    
    Steps:
    1. Get yesterday's close from daily K-line (iloc[-2])
    2. Get 5-minute K-line tail(48), filter today's data, aggregate OHLCV
    3. Calculate change percentage: (latest - prev_close) / prev_close
    4. Fallback to 15-minute K-line if 5m fails
    5. Mark as "最近" if today has no data
    6. Add market status indicator
    
    Args:
        ashare_data_source: AshareDataSource instance
        code: Stock code
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Realtime quote data with correct date and change calculation
    """
    validate_output_format(format)
    
    normalized_code = ashare_data_source.normalize_code(code)
    today = date.today()
    now = datetime.now()
    
    try:
        # Step 1: Get daily K-line for yesterday's close
        df_day = ashare_data_source.get_historical_k_data(
            code=normalized_code,
            start_date='',
            end_date='',
            frequency='1d',
        )
        
        if df_day is None or df_day.empty or len(df_day) < 2:
            return f"未找到股票 {code} 的日线数据"
        
        # Yesterday's close (iloc[-2] because iloc[-1] might be today if market is open)
        # Actually, we need to check: if the last row is today, use iloc[-2] as yesterday
        # If the last row is not today, then iloc[-1] is the most recent trading day
        last_date = df_day.index[-1].date()
        
        if last_date == today:
            # Market is open or after hours today
            prev_close = df_day.iloc[-2]['close']
            prev_date = df_day.index[-2].date()
        else:
            # Market is closed, last row is most recent trading day
            prev_close = df_day.iloc[-1]['close']
            prev_date = last_date
        
        # Step 2: Get minute K-line for today's data
        today_data = None
        minute_freq = '5m'
        
        # Try 5m first
        try:
            df_min = ashare_data_source.get_historical_k_data(
                code=normalized_code,
                start_date='',
                end_date='',
                frequency='5m',
            )
            if df_min is not None and not df_min.empty:
                today_data = _aggregate_intraday_data(df_min, today)
        except Exception:
            pass
        
        # Fallback to 15m if 5m fails
        if today_data is None:
            minute_freq = '15m'
            try:
                df_min = ashare_data_source.get_historical_k_data(
                    code=normalized_code,
                    start_date='',
                    end_date='',
                    frequency='15m',
                )
                if df_min is not None and not df_min.empty:
                    today_data = _aggregate_intraday_data(df_min, today)
            except Exception:
                pass
        
        # Determine display values
        if today_data:
            # Today has data
            latest_price = today_data['close']
            today_open = today_data['open']
            today_high = today_data['high']
            today_low = today_data['low']
            today_volume = today_data['volume']
            display_date = today.strftime('%Y-%m-%d')
            date_label = '今日'
        else:
            # No data today, use most recent daily data
            latest_row = df_day.iloc[-1]
            latest_price = latest_row['close']
            today_open = latest_row['open']
            today_high = latest_row['high']
            today_low = latest_row['low']
            today_volume = latest_row['volume']
            display_date = last_date.strftime('%Y-%m-%d')
            date_label = '最近'
        
        # Step 3: Calculate change
        change = latest_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close > 0 else 0
        
        # Step 4: Determine market status
        market_status = _get_market_status()
        status_map = {
            'trading': '交易中',
            'closed': '休市',
            'pre_market': '盘前',
            'post_market': '盘后',
        }
        
        # Build result
        result = {
            '代码': code,
            '日期': display_date,
            '最新价': round(latest_price, 2),
            '今开': round(today_open, 2),
            '最高': round(today_high, 2),
            '最低': round(today_low, 2),
            '昨收': round(prev_close, 2),
            '涨跌额': round(change, 2),
            '涨跌幅(%)': round(change_pct, 2),
            '成交量': int(today_volume),
            '市场状态': status_map.get(market_status, market_status),
        }
        
        # Add date label if not today
        if today_data is None:
            result['备注'] = f'非交易日或休市，显示最近交易日({date_label})数据'
        
        df_result = pd.DataFrame([result])
        
        meta = {
            'code': code,
            'normalized_code': normalized_code,
            'data_source': 'Sina/Tencent (AshareDataSource)',
            'update_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'minute_freq': minute_freq if today_data else 'N/A',
        }
        
        return format_table_output(df_result, format=format, max_rows=1, meta=meta)
        
    except Exception as e:
        return f"获取实时行情失败: {str(e)}"


def fetch_intraday_minute_kline(
    ashare_data_source: AshareDataSource,
    code: str,
    frequency: str = '5m',
    format: str = 'markdown',
) -> str:
    """
    Fetch intraday minute K-line data for a stock (today only).
    
    Args:
        ashare_data_source: AshareDataSource instance
        code: Stock code
        frequency: Minute frequency: '1m', '5m', '15m', '30m', '60m'
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Today's minute K-line data with Chinese column names
    """
    validate_output_format(format)
    
    valid_freqs = ['1m', '5m', '15m', '30m', '60m']
    if frequency not in valid_freqs:
        raise ValueError(f"Invalid frequency '{frequency}'. Valid: {valid_freqs}")
    
    normalized_code = ashare_data_source.normalize_code(code)
    today = date.today()
    
    try:
        df = ashare_data_source.get_historical_k_data(
            code=normalized_code,
            start_date='',
            end_date='',
            frequency=frequency,
        )
        
        if df is None or df.empty:
            return f"未找到股票 {code} 的分钟K线数据"
        
        # Filter today's data only
        df_today = df[df.index.date == today].copy()
        
        if df_today.empty:
            return f"股票 {code} 今日({today})暂无分钟K线数据"
        
        # Reset index and rename columns to Chinese
        df_result = df_today.reset_index()
        df_result.columns = ['时间', '开盘', '最高', '最低', '收盘', '成交量']
        
        # Round numeric columns
        df_result['开盘'] = df_result['开盘'].round(2)
        df_result['最高'] = df_result['最高'].round(2)
        df_result['最低'] = df_result['最低'].round(2)
        df_result['收盘'] = df_result['收盘'].round(2)
        
        meta = {
            'code': code,
            'normalized_code': normalized_code,
            'frequency': frequency,
            'date': today.strftime('%Y-%m-%d'),
            'data_source': 'Sina/Tencent (AshareDataSource)',
        }
        
        return format_table_output(df_result, format=format, max_rows=len(df_result), meta=meta)
        
    except Exception as e:
        return f"获取分钟K线失败: {str(e)}"


def fetch_realtime_multi_quote(
    ashare_data_source: AshareDataSource,
    codes: List[str],
    format: str = 'markdown',
) -> str:
    """
    Batch query for realtime quotes (max 10 stocks).
    
    Args:
        ashare_data_source: AshareDataSource instance
        codes: List of stock codes (max 10)
        format: Output format: 'markdown' | 'json' | 'csv'
    
    Returns:
        Realtime quotes sorted by change percentage (descending)
    """
    validate_output_format(format)
    
    if not codes:
        return "请提供股票代码列表"
    
    if len(codes) > 10:
        return "批量查询最多支持10只股票"
    
    results = []
    
    for code in codes:
        try:
            normalized_code = ashare_data_source.normalize_code(code)
            today = date.today()
            
            # Get daily data
            df_day = ashare_data_source.get_historical_k_data(
                code=normalized_code,
                start_date='',
                end_date='',
                frequency='1d',
            )
            
            if df_day is None or df_day.empty or len(df_day) < 2:
                results.append({
                    '代码': code,
                    '名称': 'N/A',
                    '最新价': 'N/A',
                    '涨跌幅(%)': None,
                    '状态': '无数据',
                })
                continue
            
            # Get yesterday's close and latest price
            last_date = df_day.index[-1].date()
            
            if last_date == today:
                prev_close = df_day.iloc[-2]['close']
            else:
                prev_close = df_day.iloc[-1]['close']
            
            # Try to get today's latest price from minute data
            latest_price = None
            try:
                df_min = ashare_data_source.get_historical_k_data(
                    code=normalized_code,
                    start_date='',
                    end_date='',
                    frequency='5m',
                )
                if df_min is not None and not df_min.empty:
                    df_today = df_min[df_min.index.date == today]
                    if not df_today.empty:
                        latest_price = df_today.iloc[-1]['close']
            except Exception:
                pass
            
            # Fallback to daily close
            if latest_price is None:
                latest_price = df_day.iloc[-1]['close']
            
            # Calculate change
            change_pct = ((latest_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            
            results.append({
                '代码': code,
                '名称': 'N/A',  # Name requires additional API call, omitted for simplicity
                '最新价': round(latest_price, 2),
                '涨跌幅(%)': round(change_pct, 2),
                '昨收': round(prev_close, 2),
                '状态': '成功',
            })
            
        except Exception as e:
            results.append({
                '代码': code,
                '名称': 'N/A',
                '最新价': 'N/A',
                '涨跌幅(%)': None,
                '状态': f'失败: {str(e)}',
            })
    
    # Sort by change percentage (descending)
    results.sort(key=lambda x: x['涨跌幅(%)'] if x['涨跌幅(%)'] is not None else float('-inf'), reverse=True)
    
    df_result = pd.DataFrame(results)
    
    meta = {
        'query_count': len(codes),
        'success_count': sum(1 for r in results if r['状态'] == '成功'),
        'data_source': 'Sina/Tencent (AshareDataSource)',
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return format_table_output(df_result, format=format, max_rows=len(results), meta=meta)