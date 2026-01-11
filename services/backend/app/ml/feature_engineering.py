import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

class FeatureEnginnering:
    @staticmethod
    def create_features(data: List[Dict], lookback: int = 10) -> pd.DataFrame:
        df = pd.DataFrame(data)

        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()

        df['ema_5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()

        df['momentum_5'] = df['close'] - df['close'].shift(5)
        df['momentum_10'] = df['close'] - df['close'].shift(10)

        df['volatility_5'] = df['returns'].rolling(window=5).std()
        df['volatility_10'] = df['returns'].rolling(window=10).std()

        df['high_low_range'] = df['high'] - df['low']
        df['close_open_range'] = df['close'] - df['open']

        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = -(delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        df['volume_sma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']

        for i in range(1, lookback + 1):
            df[f'close_lag_{i}'] = df['close'].shift(i)
            df[f'volume_lag_{i}'] = df['volume'].shift(i)

        df['target_price'] = df['close'].shift(-1)

        df['target_direction'] = (df['target_price']  > df['close'].astype(int))

        return df
    
    @staticmethod
    def prepare_train_test_split(
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        df_clean = df.dropna()

        feature_cols = [col for col in df_clean.columns
                        if col not in ['timestamp', 'target_price', 'target_direction']]
        
        X = df_clean[feature_cols]
        y = df_clean['target_price']

        split_idx = int(len(X)) * (1 - test_size)

        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]

        return X_train, X_test, y_train, y_test
 