"""
Ashare data source implementation.
Encapsulates Sina and Tencent HTTP APIs for fetching stock data.
Based on Ashare library (https://github.com/mpquant/Ashare)
"""
import json
from datetime import datetime, date
from typing import Optional, List

import pandas as pd
import requests

from src.data_source_interface import FinancialDataSource, DataSourceError, NoDataFoundError


class AshareDataSource(FinancialDataSource):
    """
    Data source implementation using Sina and Tencent APIs.
    Provides historical K-line data without requiring login.
    """

    # API endpoints (matching Ashare library)
    SINA_KLINE_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
    TENCENT_DAY_URL = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    TENCENT_MIN_URL = "http://ifzq.gtimg.cn/appstock/app/kline/mkline"

    # Request timeout
    TIMEOUT = 10

    # Frequency mapping for Sina (minutes)
    SINA_FREQ_MAP = {
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '60m': 60,
        '1d': 240,    # Daily = 240 minutes
        '1w': 1200,   # Weekly = 1200 minutes
        '1M': 7200,   # Monthly = 7200 minutes
    }

    # Tencent frequency mapping
    TENCENT_DAY_FREQ_MAP = {
        '1d': 'day',
        '1w': 'week',
        '1M': 'month',
    }

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    @staticmethod
    def normalize_code(code: str) -> str:
        """
        Normalize stock code to Ashare format (e.g., 'sh600000', 'sz000001').

        Supports formats:
        - sh600000, sz000001 (Tongdaxin format)
        - 600000, 000001 (pure number)
        - sh.600000, sz.000001 (Baostock format)
        - 600519.XSHG, 000001.XSHE (JoinQuant format)
        """
        code = code.strip()

        # JoinQuant format: 600519.XSHG or 000001.XSHE
        if '.XSHG' in code:
            return 'sh' + code.replace('.XSHG', '')
        if '.XSHE' in code:
            return 'sz' + code.replace('.XSHE', '')

        # Baostock format: sh.600000 -> sh600000
        if '.' in code:
            parts = code.split('.')
            if len(parts) == 2:
                prefix, suffix = parts[0].lower(), parts[1]
                # Baostock: sh.600000 or sz.000001
                if prefix in ('sh', 'sz') and suffix.isdigit():
                    return f"{prefix}{suffix}"

        # Already in correct format
        if code.startswith('sh') or code.startswith('sz'):
            return code.lower()

        # Pure number: determine exchange
        if code.isdigit():
            if code.startswith('6'):
                return f"sh{code}"
            elif code.startswith(('0', '2', '3')):
                return f"sz{code}"

        return code.lower()

    def get_historical_k_data(
        self,
        code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
        adjust_flag: str = "3",
        fields: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Fetch historical K-line data.

        Args:
            code: Stock code
            start_date: Start date (not used for Sina/Tencent, data is count-based)
            end_date: End date (used as reference point)
            frequency: '1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M'
            adjust_flag: '1' qfq, '2' hfq, '3' no adjust (default)
            fields: Not used, returns standard OHLCV columns

        Returns:
            DataFrame with columns: date, open, close, high, low, volume
        """
        normalized_code = self.normalize_code(code)

        # Determine count
        if frequency in ('1m', '5m', '15m', '30m', '60m'):
            count = 320  # More minute bars
        else:
            count = 500  # About 2 years of daily data

        # Daily/Weekly/Monthly: Try Sina first, then Tencent
        if frequency in ('1d', '1w', '1M'):
            try:
                df = self._get_price_sina(normalized_code, end_date, count, frequency)
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass

            try:
                df = self._get_price_day_tx(normalized_code, end_date, count, frequency)
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass

        # Minute data: 1m only available from Tencent
        elif frequency == '1m':
            try:
                df = self._get_price_min_tx(normalized_code, end_date, count, frequency)
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass
        else:
            # Other minute frequencies: Try Sina first, then Tencent
            try:
                df = self._get_price_sina(normalized_code, end_date, count, frequency)
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass

            try:
                df = self._get_price_min_tx(normalized_code, end_date, count, frequency)
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass

        raise NoDataFoundError(f"No data found for {code}")

    def _get_price_sina(
        self, code: str, end_date: str, count: int, frequency: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data from Sina API (matching Ashare implementation).
        Sina supports all frequencies except 1m.
        """
        # Convert frequency to minutes
        freq_min = self.SINA_FREQ_MAP.get(frequency, 240)

        params = {
            "symbol": code,
            "scale": freq_min,
            "ma": 5,
            "datalen": count,
        }

        try:
            resp = self._session.get(
                self.SINA_KLINE_URL,
                params=params,
                timeout=self.TIMEOUT
            )

            data = json.loads(resp.content)
            if not data or isinstance(data, dict):
                return None

            # Parse records
            df = pd.DataFrame(data, columns=['day', 'open', 'high', 'low', 'close', 'volume'])
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)

            df['day'] = pd.to_datetime(df['day'])
            df = df.set_index('day')
            df.index.name = ''

            return df

        except Exception:
            return None

    def _get_price_day_tx(
        self, code: str, end_date: str, count: int, frequency: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch daily/weekly/monthly data from Tencent API (matching Ashare implementation).
        """
        unit = self.TENCENT_DAY_FREQ_MAP.get(frequency, 'day')

        # Format end_date
        if end_date:
            if isinstance(end_date, date):
                end_date = end_date.strftime('%Y-%m-%d')
            else:
                end_date = str(end_date).split(' ')[0]
            # If end_date is today, make it empty
            if end_date == datetime.now().strftime('%Y-%m-%d'):
                end_date = ''

        # Build URL (matching Ashare format)
        url = f"{self.TENCENT_DAY_URL}?param={code},{unit},,{end_date},{count},qfq"

        try:
            resp = self._session.get(url, timeout=self.TIMEOUT)
            st = json.loads(resp.content)

            if 'data' not in st or code not in st['data']:
                return None

            stk = st['data'][code]
            ms = 'qfq' + unit
            buf = stk[ms] if ms in stk else stk.get(unit)

            if not buf:
                return None

            df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume'], dtype='float')
            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')
            df.index.name = ''

            return df

        except Exception:
            return None

    def _get_price_min_tx(
        self, code: str, end_date: str, count: int, frequency: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch minute K-line data from Tencent API (matching Ashare implementation).
        """
        # Extract minute number from frequency (e.g., '5m' -> 5)
        ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1

        # Build URL (matching Ashare format)
        url = f"{self.TENCENT_MIN_URL}?param={code},m{ts},,{count}"

        try:
            resp = self._session.get(url, timeout=self.TIMEOUT)
            st = json.loads(resp.content)

            if 'data' not in st or code not in st['data']:
                return None

            mkey = 'm' + str(ts)
            buf = st['data'][code].get(mkey)
            if not buf:
                return None

            df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'n1', 'n2'])
            df = df[['time', 'open', 'close', 'high', 'low', 'volume']]
            df[['open', 'close', 'high', 'low', 'volume']] = df[['open', 'close', 'high', 'low', 'volume']].astype(float)

            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')
            df.index.name = ''

            # Update latest close price from qt data
            if 'qt' in st['data'][code] and code in st['data'][code]['qt']:
                try:
                    df['close'].iloc[-1] = float(st['data'][code]['qt'][code][3])
                except Exception:
                    pass

            return df

        except Exception:
            return None

    # --- Methods not supported by this data source ---

    def get_stock_basic_info(self, code: str) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support stock basic info")

    def get_trade_dates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support trade dates")

    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support all stock list")

    def get_deposit_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support deposit rate data")

    def get_loan_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support loan rate data")

    def get_required_reserve_ratio_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0') -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support reserve ratio data")

    def get_money_supply_data_month(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support money supply data")

    def get_money_supply_data_year(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support money supply data")

    def get_dividend_data(self, code: str, year: str, year_type: str = "report") -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support dividend data")

    def get_adjust_factor_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support adjust factor data")

    def get_profit_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial reports")

    def get_operation_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial reports")

    def get_growth_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial reports")

    def get_balance_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial reports")

    def get_cash_flow_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial reports")

    def get_dupont_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial reports")

    def get_performance_express_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support performance express reports")

    def get_forecast_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support forecast reports")

    def get_fina_indicator(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support financial indicators")

    def get_stock_industry(self, code: Optional[str] = None, date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support industry data")

    def get_hs300_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support index constituents")

    def get_sz50_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support index constituents")

    def get_zz500_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        raise NotImplementedError("AshareDataSource does not support index constituents")