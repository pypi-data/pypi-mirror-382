import pandas as pd
from clickhouse_driver import Client
import os
import numpy as np


ch_client = Client(
    host=os.getenv("CLICKHOUSE_HOST", "localhost"),
    port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
    user=os.getenv("CLICKHOUSE_USER", "default"),
    password=os.getenv("CLICKHOUSE_PASSWORD", ""),
    database="us_stocks"
)

# 指標定義
INDICATORS = {
    'rsi_14': {
        'name': 'RSI 14',
        'indicator': 'rsi',
        'description': 'RSI 14',
        'params': {'period': 14},
    },
    'ma_5': {
        'name': 'MA 5',
        'indicator': 'ma',
        'description': 'MA 5',
        'params': {'period': 5},
    },
    'ma_10': {
        'name': 'MA 10',
        'indicator': 'ma',
        'description': 'MA 10',
        'params': {'period': 10},
    },
    'ma_20': {
        'name': 'MA 20',
        'indicator': 'ma',
        'description': 'MA 20',
        'params': {'period': 20},
    },
    'ma_50': {
        'name': 'MA 50',
        'indicator': 'ma',
        'description': 'MA 50',
        'params': {'period': 50},
    },
    'ma_100': {
        'name': 'MA 100',
        'indicator': 'ma',
        'description': 'MA 100',
        'params': {'period': 100},
    },
    'ma_200': {
        'name': 'MA 200',
        'indicator': 'ma',
        'description': 'MA 200',
        'params': {'period': 200},
    },
    'sar': {
        'name': 'SAR',
        'indicator': 'sar',
        'description': 'SAR',
        'params': {},
    },
    'bollinger_bands_upper': {
        'name': 'Bollinger Bands Upper',
        'indicator': 'bollinger_bands_upper',
        'description': 'Bollinger Bands Upper',
        'params': {'period': 20, 'std_dev': 2},
    },
    'bollinger_bands_middle': {
        'name': 'Bollinger Bands Middle',
        'indicator': 'bollinger_bands_middle',
        'description': 'Bollinger Bands Middle',
        'params': {'period': 20, 'std_dev': 2},
    },
    'bollinger_bands_lower': {
        'name': 'Bollinger Bands Lower',
        'indicator': 'bollinger_bands_lower',
        'description': 'Bollinger Bands Lower',
        'params': {'period': 20, 'std_dev': 2},
    },
    'bbi': {
        'name': 'BBI',
        'indicator': 'bbi',
        'description': 'BBI',
        'params': {'period': 10},
    },
    'macd_line': {
        'name': 'MACD Line',
        'indicator': 'macd_line',
        'description': 'MACD Line',
        'params': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},

    },
    'macd_signal': {
        'name': 'MACD Signal',
        'indicator': 'macd_signal',
        'description': 'MACD Signal',
        'params': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},
    },
    'macd_histogram': {
        'name': 'MACD Histogram',
        'indicator': 'macd_histogram',
        'description': 'MACD Histogram',
        'params': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},
    },
    'kdj_k': {
        'name': 'KDJ K',
        'indicator': 'kdj_k',
        'description': 'KDJ K',
        'params': {'period': 9, 'smoothk': 3, 'smoothd': 3},
    },
    'kdj_d': {
        'name': 'KDJ D',
        'indicator': 'kdj_d',
        'description': 'KDJ D',
        'params': {'period': 9, 'smoothk': 3, 'smoothd': 3},
    },
    'kdj_j': {
        'name': 'KDJ J',
        'indicator': 'kdj_j',
        'description': 'KDJ J',
        'params': {'period': 9, 'smoothk': 3, 'smoothd': 3},
    },
    'td_index': {
        'name': 'TD Index',
        'indicator': 'td_index',
        'description': 'TD Index',
        'params': {'period': 9},
    }
}


US_STOCKS_DATABASE = "us_stocks"
US_STOCKS_DAILY_AGGS_TABLE = "daily_aggs"
US_STOCKS_WEEKLY_AGGS_TABLE = "weekly_aggs"
US_STOCKS_MONTHLY_AGGS_TABLE = "monthly_aggs"
US_STOCKS_DAILY_SNAPSHOT_TABLE = "daily_snapshot"
US_STOCKS_WEEKLY_SNAPSHOT_TABLE = "weekly_snapshot"
US_STOCKS_MONTHLY_SNAPSHOT_TABLE = "monthly_snapshot"
US_STOCKS_INDICATORS_TABLE = "indicator_values"

TW_FUTURES_DATABASE = "tw_futures"
TW_FUTURES_DAILY_AGGS_TABLE = "daily_aggs"
TW_MINUTES_AGGS_TABLE = "minute_aggs"

class BullinvQuote:

    @staticmethod
    def get_data(ticker, start_date=None, end_date=None, limit=1000, include_indicators=False,period="day",market="us_stock"):
        if market == "us_stock":
            return BullinvQuote.get_us_stock_data(ticker, start_date, end_date, limit, include_indicators,period)
        elif market == "tw_futures":
            return BullinvQuote.get_tw_futures_data(ticker, start_date, end_date, limit, include_indicators,period)
        else:
            raise ValueError(f"Market {market} not supported")

    @staticmethod
    def get_us_stock_data(ticker, start_date=None, end_date=None, limit=1000, include_indicators=False, period="day"):
        if period == "day":
            table = US_STOCKS_DAILY_AGGS_TABLE
            date_column = "window_start"
        elif period == "week":
            table = US_STOCKS_WEEKLY_AGGS_TABLE
            date_column = "week_start"
        elif period == "month":
            table = US_STOCKS_MONTHLY_AGGS_TABLE
            date_column = "month_start"
        else:
            raise ValueError(f"Period {period} not supported")

        # 获取基本的OHLCV数据
        query = f"""SELECT 
            ticker,
            volume,
            open,
            high,
            low,
            close,
            {date_column} as datetime
        FROM {US_STOCKS_DATABASE}.{table} 
        WHERE ticker = '{ticker}'
        """

        # 添加日期过滤条件
        if start_date:
            query += f" AND {date_column} >= '{start_date}'"
        if end_date:
            query += f" AND {date_column} <= '{end_date}'"

        # 添加排序和限制
        query += f" ORDER BY {date_column}"
        if limit:
            query += f" LIMIT {limit}"

        # 使用with_column_types=True获取列信息
        data, columns = ch_client.execute(query, with_column_types=True)

        # 将data转换为DataFrame
        df = pd.DataFrame(data, columns=[col[0] for col in columns])

        # 转换日期列
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])

        # 如果需要包含指标数据
        if include_indicators and not df.empty:
            # 根据周期选择对应的snapshot表
            if period == "day":
                snapshot_table = US_STOCKS_DAILY_SNAPSHOT_TABLE
                snapshot_date_column = "date"
            elif period == "week":
                snapshot_table = US_STOCKS_WEEKLY_SNAPSHOT_TABLE
                snapshot_date_column = "week_start"
            elif period == "month":
                snapshot_table = US_STOCKS_MONTHLY_SNAPSHOT_TABLE
                snapshot_date_column = "month_start"
            
            # 从对应的snapshot表获取指标数据
            snapshot_query = f"""SELECT *
            FROM {US_STOCKS_DATABASE}.{snapshot_table}
            WHERE ticker = '{ticker}'
            """
            
            if start_date:
                snapshot_query += f" AND {snapshot_date_column} >= '{start_date}'"
            if end_date:
                snapshot_query += f" AND {snapshot_date_column} <= '{end_date}'"
            
            snapshot_query += f" ORDER BY {snapshot_date_column}"
            if limit:
                snapshot_query += f" LIMIT {limit}"
            
            snapshot_data, snapshot_columns = ch_client.execute(snapshot_query, with_column_types=True)
            snapshot_df = pd.DataFrame(snapshot_data, columns=[col[0] for col in snapshot_columns])
            
            # 转换日期列
            if snapshot_date_column in snapshot_df.columns:
                snapshot_df['datetime'] = pd.to_datetime(snapshot_df[snapshot_date_column])
            
            # 合并OHLCV和指标数据
            df = snapshot_df

        # sort by datetime
        df = df.sort_values('datetime')
        # reset index
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def get_us_stock_list():
        query = f"""SELECT 
            DISTINCT ticker
        FROM {US_STOCKS_DATABASE}.{US_STOCKS_DAILY_AGGS_TABLE}
        """
        data, columns = ch_client.execute(query, with_column_types=True)
        return [row[0] for row in data]
            


    @staticmethod
    def get_tw_futures_data(symbol, start_date=None, end_date=None, limit=1000, include_indicators=False,period="day"):
        if period == "minute":
            table = TW_MINUTES_AGGS_TABLE
        else:
            raise ValueError(f"Period {period} not supported")
        
        # 首先获取总记录数以确定偏移量
        count_query = f"""
        SELECT count(*) as total
        FROM {TW_FUTURES_DATABASE}.{table} 
        WHERE symbol = '{symbol}'
        """
        
        if start_date:
            count_query += f" AND datetime >= '{start_date}'"
        if end_date:
            count_query += f" AND datetime <= '{end_date}'"
            
        total_count = ch_client.execute(count_query)[0][0]
        
        # 计算偏移量以获取最后的记录
        offset = max(0, total_count - limit)
        
        query = f"""SELECT 
            symbol,
            datetime,
            open,
            high,
            low,
            close,
            volume,
            amount
        FROM {TW_FUTURES_DATABASE}.{table} 
        WHERE symbol = '{symbol}'
        """

        if start_date:
            query += f" AND datetime >= '{start_date}'"
        if end_date:
            query += f" AND datetime <= '{end_date}'"

        query += f" ORDER BY datetime"
        
        # 使用 LIMIT offset, limit 语法获取最后的记录
        if limit and not (start_date and end_date):
            query += f" LIMIT {offset}, {limit}"

        data, columns = ch_client.execute(query, with_column_types=True)
        df = pd.DataFrame(data, columns=[col[0] for col in columns])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def get_screener_date_list() -> pd.DataFrame:
        query = f"""SELECT 
            DISTINCT date
        FROM {US_STOCKS_DATABASE}.{US_STOCKS_DAILY_SNAPSHOT_TABLE}
        ORDER BY date DESC
        """
        data, columns = ch_client.execute(query, with_column_types=True)
        return pd.DataFrame(data, columns=[col[0] for col in columns])
    
    @staticmethod
    def get_screener_week_list() -> pd.DataFrame:
        query = f"""SELECT 
            DISTINCT week_start
        FROM {US_STOCKS_DATABASE}.{US_STOCKS_WEEKLY_SNAPSHOT_TABLE}
        ORDER BY week_start DESC
        """
        data, columns = ch_client.execute(query, with_column_types=True)
        return pd.DataFrame(data, columns=[col[0] for col in columns])
    
    @staticmethod
    def get_screener_month_list() -> pd.DataFrame:
        query = f"""SELECT 
            DISTINCT month_start
        FROM {US_STOCKS_DATABASE}.{US_STOCKS_MONTHLY_SNAPSHOT_TABLE}
        ORDER BY month_start DESC
        """
        data, columns = ch_client.execute(query, with_column_types=True)
        return pd.DataFrame(data, columns=[col[0] for col in columns])
    

    @staticmethod
    def stock_screener(conditions, include_columns: list[str] = ["*"], limit: int = 100, period: str = "day") -> pd.DataFrame:
        # 根据周期选择对应的表
        if period == "day":
            table = US_STOCKS_DAILY_SNAPSHOT_TABLE
            date_column = "date"
            date_list = BullinvQuote.get_screener_date_list()
        elif period == "week":
            table = US_STOCKS_WEEKLY_SNAPSHOT_TABLE
            date_column = "week_start"
            date_list = BullinvQuote.get_screener_week_list()
        elif period == "month":
            table = US_STOCKS_MONTHLY_SNAPSHOT_TABLE
            date_column = "month_start"
            date_list = BullinvQuote.get_screener_month_list()
        else:
            raise ValueError(f"Period {period} not supported. Use 'day', 'week', or 'month'")

        # 构建完整的查询条件
        where_clauses = []
        join_needed = False

        date_list = date_list[date_column].tolist()

        # 获取最后两个日期  
        t1_date = date_list[0].strftime("%Y-%m-%d")
        t2_date = date_list[1].strftime("%Y-%m-%d")

        if not isinstance(conditions, list):
            conditions = [conditions]

        for condition in conditions:
            if "cross_over" in condition:
                # 解析 cross_over 表达式
                parts = condition.split("cross_over")
                left_indicator = parts[0].strip()
                right_indicator = parts[1].strip()

                # 构建跨天比较的条件，使用最近两个交易日
                where_clauses.append(
                    f"t1.{left_indicator} > t1.{right_indicator} AND t2.{left_indicator} <= t2.{right_indicator}")
                join_needed = True

            elif "cross_under" in condition:
                # 解析 cross_under 表达式
                parts = condition.split("cross_under")
                left_indicator = parts[0].strip()
                right_indicator = parts[1].strip()

                where_clauses.append(
                    f"t1.{left_indicator} < t1.{right_indicator} AND t2.{left_indicator} >= t2.{right_indicator}")
                join_needed = True

            elif "cross_above" in condition:
                # 解析 cross_above 表达式 (等同於 cross_over)
                parts = condition.split("cross_above")
                left_indicator = parts[0].strip()
                right_indicator = parts[1].strip()

                where_clauses.append(
                    f"t1.{left_indicator} > t1.{right_indicator} AND t2.{left_indicator} <= t2.{right_indicator}")
                join_needed = True

            elif "cross_below" in condition:
                # 解析 cross_below 表达式 (等同於 cross_under)
                parts = condition.split("cross_below")
                left_indicator = parts[0].strip()
                right_indicator = parts[1].strip()

                where_clauses.append(
                    f"t1.{left_indicator} < t1.{right_indicator} AND t2.{left_indicator} >= t2.{right_indicator}")
                join_needed = True

            else:
                # 原始条件
                where_clauses.append(condition)

        # 构建查询
        if join_needed:
            columns_str = ",".join(
                [f"t1.{col}" for col in include_columns if col != "*"]) if "*" not in include_columns else "t1.*"
            query = f"""SELECT DISTINCT
                {columns_str}
            FROM {US_STOCKS_DATABASE}.{table} AS t1
            LEFT JOIN {US_STOCKS_DATABASE}.{table} AS t2
            ON t1.ticker = t2.ticker AND t2.{date_column} = '{t2_date}'
            WHERE t1.{date_column} = '{t1_date}' AND {" AND ".join(where_clauses)}
            LIMIT {limit}
            """
        else:
            columns_str = ",".join(include_columns)
            query = f"""SELECT DISTINCT
                {columns_str}
            FROM {US_STOCKS_DATABASE}.{table} 
            WHERE {date_column} = '{t1_date}' AND {" AND ".join(where_clauses)}
            LIMIT {limit}
            """

        data, columns = ch_client.execute(query, with_column_types=True)
        # 将data转换为DataFrame
        df = pd.DataFrame(data, columns=[col[0] for col in columns])

        # 检查是否有日期列
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            # 按日期排序
            df = df.sort_values(date_column)

        # 重置索引
        df = df.reset_index(drop=True)
        return df

    # def gen_filter_func(self,conditions):
    #     # conditions = [
    #     #     {"indicator": "rsi_14", "operator": ">", "value": 50},
    #     #     {"indicator": "volume", "operator": "cross_over", "value": "ma_10"}
    #     # ]
    #     filter_func = ""
    #     for condition in conditions:
    #         if condition["operator"] == "cross_over":
    #             filter_func += f"{condition['indicator']} cross_over {condition['value']} and "
    #         elif condition["operator"] == "cross_under":
    #             filter_func += f"{condition['indicator']} cross_under {condition['value']} and "
