from .base import BaseStrategy
import numpy as np
from typing import List, Dict
import sys
sys.path.append('..')


from app.ml.feature_engineering import FeatureEnginnering
from app.ml.linear_regression import LinearRegressionModel
from app.ml.logisitic_regression import LogisticRegressionModel

class MLPredictionStrategy(BaseStrategy):

    def __init__(
            self,
            lookback: int = 10,
            prediction_thresold: float = 0.01,
            confidence_threshold: float = 0.6
    ):
        super().__init__('ML Prediction Strategy')
        self.lookback = lookback
        self.prediction_threshold = prediction_thresold
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.is_trained = False
    
    def train_model(self, data: List[Dict]) -> Dict:
        if len(data) < 50:
            return {
                'error': 'Need at least 50 candles for training',
                'status': 'failed'
            }
        
        fe = FeatureEnginnering()
        df_features = fe.create_features(data, lookback=self.lookback)

        X_train, X_test, y_train, y_test = fe.prepare_train_test_split(
            df_features, test_size=0.2
        )

        self.model = LinearRegressionModel()
        train_metrics = self.model.train(X_train, y_train)
        test_metrics = self.model.evaluate(X_test, y_test)
        self.is_trained = True

        return {
            "status": "trained",
            "train_metrics": train_metrics,
            "test_metrics": test_metrics
        }
    
    def generate_signals(self, data: List[Dict]) -> Dict:
        if not self.is_trained:
            train_result = self.train_model(data)
            if 'errror' in train_result:
                return train_result
        
        fe = FeatureEnginnering()
        df_features = fe.create_features(data, lookback=self.lookback)
        df_clean = df_features.dropna()

        feature_cols = [col for col in df_clean.columns
                        if col not in ['timestamp', 'target_price', 'target_direction']]
        
        signals = []
        predictions = []
        position_open = False

        for i in range(len(df_clean)):
            X = df_clean[feature_cols].iloc[[i]]
            current_idx = df_clean.index[i]

            if current_idx >= len(data):
                continue

            candle = data[current_idx]
            current_price = candle['close']

            predicted_price = self.model.predict(X)[0]
            predicted_change_pct = ((predicted_price - current_price) / current_price)

            
        predictions.append({
                "index": current_idx,
                "timestamp": candle['timestamp'],
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "predicted_change_percent": round(predicted_change_pct * 100, 2)
            })
        if predicted_change_pct > self.prediction_threshold and not position_open:
            signal = {
                "index": current_idx,
                "timestamp": candle['timestamp'],
                "type": "BUY",
                "price": current_price,
                "predicted_price": round(predicted_price, 2),
                "predicted_gain": round(predicted_change_pct * 100, 2),
                "reason": f"ML predicts {predicted_change_pct*100:.2f}% increase (threshold: {self.prediction_threshold*100}%)"
                }
            signals.append(signal)
            position_open = True
            
        elif predicted_change_pct < -self.prediction_threshold and position_open:
                signal = {
                    "index": current_idx,
                    "timestamp": candle['timestamp'],
                    "type": "SELL",
                    "price": current_price,
                    "predicted_price": round(predicted_price, 2),
                    "predicted_loss": round(predicted_change_pct * 100, 2),
                    "reason": f"ML predicts {predicted_change_pct*100:.2f}% decrease"
                }
                signals.append(signal)
                position_open = False
        
        return {
            "strategy": self.name,
            "parameters": {
                "lookback": self.lookback,
                "prediction_threshold": self.prediction_threshold,
                "model_type": "linear_regression"
            },
            "model_metrics": self.model.metrics if self.is_trained else None,
            "total_candles": len(data),
            "signals": signals,
            "predictions": predictions[-10:],  # Last 10 predictions
            "buy_signals": sum(1 for s in signals if s['type'] == 'BUY'),
            "sell_signals": sum(1 for s in signals if s['type'] == 'SELL')
        }

class MLDirectionStrategy(BaseStrategy):
    def __init__(
        self,
        lookback: int = 10,
        confidence_threshold: float = 0.65  
    ):
        super().__init__("ML Direction Strategy")
        self.lookback = lookback
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.is_trained = False
    
    def train_model(self, data: List[Dict]) -> Dict:
        if len(data) < 50:
            return {
                "error": "Need at least 50 candles for training",
                "status": "failed"
            }
        
        fe = FeatureEnginnering()
        df_features = fe.create_features(data, lookback=self.lookback)
        df_clean = df_features.dropna()
        
        feature_cols = [col for col in df_clean.columns 
                       if col not in ['timestamp', 'target_price', 'target_direction']]
        
        X = df_clean[feature_cols]
        y = df_clean['target_direction']
        
        split_idx = int(len(X) * 0.8)
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]
        
        self.model = LogisticRegressionModel()
        train_metrics = self.model.train(X_train, y_train)
        test_metrics = self.model.evaluate(X_test, y_test)
        self.is_trained = True
        
        return {
            "status": "trained",
            "train_metrics": train_metrics,
            "test_metrics": test_metrics
        }
    
    def generate_signals(self, data: List[Dict]) -> Dict:
        if not self.is_trained:
            train_result = self.train_model(data)
            if "error" in train_result:
                return train_result
        
        fe = FeatureEnginnering()
        df_features = fe.create_features(data, lookback=self.lookback)
        df_clean = df_features.dropna()
        
        feature_cols = [col for col in df_clean.columns 
                       if col not in ['timestamp', 'target_price', 'target_direction']]
        
        signals = []
        predictions = []
        position_open = False
        
        for i in range(len(df_clean)):
            X = df_clean[feature_cols].iloc[[i]]
            current_idx = df_clean.index[i]
            
            if current_idx >= len(data):
                continue
            
            candle = data[current_idx]
     
            direction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = max(probabilities)
            
            predictions.append({
                "index": current_idx,
                "timestamp": candle['timestamp'],
                "predicted_direction": "UP" if direction == 1 else "DOWN",
                "confidence": round(confidence * 100, 2)
            })
            
            if direction == 1 and confidence > self.confidence_threshold and not position_open:
                signal = {
                    "index": current_idx,
                    "timestamp": candle['timestamp'],
                    "type": "BUY",
                    "price": candle['close'],
                    "confidence": round(confidence * 100, 2),
                    "reason": f"ML predicts UP with {confidence*100:.1f}% confidence (threshold: {self.confidence_threshold*100}%)"
                }
                signals.append(signal)
                position_open = True
            
            elif direction == 0 and confidence > self.confidence_threshold and position_open:
                signal = {
                    "index": current_idx,
                    "timestamp": candle['timestamp'],
                    "type": "SELL",
                    "price": candle['close'],
                    "confidence": round(confidence * 100, 2),
                    "reason": f"ML predicts DOWN with {confidence*100:.1f}% confidence"
                }
                signals.append(signal)
                position_open = False
        
        return {
            "strategy": self.name,
            "parameters": {
                "lookback": self.lookback,
                "confidence_threshold": self.confidence_threshold,
                "model_type": "logistic_regression"
            },
            "model_metrics": self.model.metrics if self.is_trained else None,
            "total_candles": len(data),
            "signals": signals,
            "predictions": predictions[-10:],
            "buy_signals": sum(1 for s in signals if s['type'] == 'BUY'),
            "sell_signals": sum(1 for s in signals if s['type'] == 'SELL')
        }     
