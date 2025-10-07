from decimal import Decimal
import logging
import pandas as pd
import numpy as np
from core.utils.OPTools import OPTools

class SMCBase(object):
    HIGH_COL = "high"
    LOW_COL = "low"
    CLOSE_COL = "close"
    OPEN_COL = "open"
    VOLUME_COL = "volume"
    AMOUNT_COL = "amount"
    TIMESTAMP_COL = "timestamp"
    ATR_COL = "atr"

    BUY_SIDE = "buy"
    SELL_SIDE = "sell"
    

    def __init__(self):  
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def check_columns(df: pd.DataFrame, required_columns: list) -> bool:
        """
        检查DataFrame是否包含指定的列
        参数:
            df (pd.DataFrame): 要检查的DataFrame
            columns (list): 要检查的列名列表
        返回:
            bool: 如果DataFrame包含所有指定的列，则返回True；否则返回False
        """
        has_pass = all(col in df.columns for col in required_columns)
        if not has_pass:
            raise ValueError(f"DataFrame必须包含列: {required_columns}")
        return has_pass

    @staticmethod
    def toDecimal(value, precision:int=None) -> Decimal:
        return OPTools.toDecimal(value, precision)

    @staticmethod
    def get_precision_length(value) -> int:
        return len(f"{value:.15f}".rstrip('0').split('.')[1]) if '.' in f"{value:.15f}" else 0

    @staticmethod  
    def calculate_atr(df, period=200, multiplier=2, ema=True):
        """
        计算增强版ATR指标，等效于Pine Script中的 ta.highest(ta.atr(200),200)*2
        
        参数:
            df: 包含OHLCV数据的DataFrame
            period: ATR计算周期，默认200
            multiplier: 放大倍数，默认2
        
        返回:
            增强版ATR序列
        """
          # 计算真实波幅(TR)的三个组成部分
        df['prev_close'] = df['close'].shift(1) # 获取前一天的收盘价
        df['tr1'] = df[SMCBase.HIGH_COL] - df[SMCBase.LOW_COL] # 当日最高价 - 当日最低价
        df['tr2'] = abs(df[SMCBase.HIGH_COL] - df['prev_close']) # |当日最高价 - 前日收盘价|
        df['tr3'] = abs(df[SMCBase.LOW_COL] - df['prev_close']) # |当日最低价 - 前日收盘价|
        
        # 使用向量化操作计算真实波幅
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

        # 清理临时列
        df.drop(['prev_close', 'tr1', 'tr2', 'tr3'], axis=1, inplace=True)

            # 计算ATR
        if ema:
            # 使用指数移动平均 (Pine Script默认方式)
            df['atr_ma'] = df['tr'].ewm(span=period, adjust=False).mean()
        else:
            # 使用简单移动平均
           df['atr_ma'] = df['tr'].rolling(window=period).mean()
        
        # 计算ATR的period周期最大值
        df[SMCBase.ATR_COL] = df['atr_ma'].rolling(window=period, min_periods=1).max() * multiplier
   
        
        return df




    def calculate_atr_with_smoothing(df, length=14, smoothing='RMA'):  
        """
        计算ATR (Average True Range) 指标
        
        参数:
        df (pd.DataFrame): 包含OHLCV数据的DataFrame，需包含列：['high', 'low', 'close']
        length (int): 计算周期，默认为14
        smoothing (str): 平滑方法，支持 'RMA', 'SMA', 'EMA', 'WMA'，默认为 'RMA'
        
        返回:
        pd.Series: ATR值序列
        """
        # 确保数据包含所需的列
        required_columns = [SMCBase.HIGH_COL, SMCBase.LOW_COL, SMCBase.CLOSE_COL]
        SMCBase.check_columns(df, required_columns)
        
        # 计算真实波幅 (TR)
        high_low = df[SMCBase.HIGH_COL] - df[SMCBase.LOW_COL]
        high_close = (df[SMCBase.HIGH_COL] - df[SMCBase.CLOSE_COL].shift()).abs()
        low_close = (df[SMCBase.LOW_COL] - df[SMCBase.CLOSE_COL].shift()).abs()
        
        # 计算TR列，取三个值中的最大值
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # Apply smoothing
        if smoothing == 'RMA':
            # RMA is approximately an EMA with alpha = 1/length
            atr = tr.ewm(alpha=1/length, adjust=False).mean()
        elif smoothing == 'SMA':
            atr = tr.rolling(window=length).mean()
        elif smoothing == 'EMA':
            atr = tr.ewm(span=length, adjust=False).mean()
        elif smoothing == 'WMA':
            # WMA implementation
            weights = pd.Series(range(1, length+1))
            def wma(series):
                return (series * weights).sum() / weights.sum()
            atr = tr.rolling(window=length).apply(wma)
        else:
            raise ValueError("Invalid smoothing method. Use 'RMA', 'SMA', 'EMA', or 'WMA'")
        
        return atr

