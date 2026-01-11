from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import sys
sys.path.append('..')

from ml.feature_engineering import FeatureEnginnering
from ml.linear_regression import LinearRegressionModel
from ml.logisitic_regression import LogisticRegressionModel
from endpoints.ohlcv import load_data

router = APIRouter()

class MLTrainRequest(BaseModel):
    ticker: str = Field(..., description='Ticker symbol')
    period: str = Field('6mo', description='Training data period')
    interval: str = Field('1d', description="Data interval")
    model_type: str = Field(..., description='Model type: linear_regression, logistic_regression')
    lookback: int = Field(10, ge=1, le=50, description='Lookback period for features')
    test_size: float = Field(0.2, ge=0.1, le=0.5, description='Test set size')

class MLPredictRequest(BaseModel):
    ticker: str = Field(..., description='Ticker symbol')
    period: str = Field('6mo', description='Training data period')
    interval: str = Field('1d', description="Data interval")
    model_type: str = Field(..., description='Model type')
    lookback: int = Field(10, description='Must match training lookback')

trained_models = {}

@router.post('/train')
def train_model(request: MLTrainRequest):
    try:
        market_data = load_data(request.ticker, request.period, request.interval)

        if not market_data.data or len(market_data.data) < 50:
            raise HTTPException(
                status_code=400,
                detail='Not enough data for training. Need at least 50 candles.'
            )
        
        data_list = [
            {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'vloume': candle.volume
            }
            for candle in market_data.data
        ]

        fe = FeatureEnginnering()
        df_features = fe.create_features(data_list, lookback=request.lookback)

        if request.model_type == 'linear_regression':
            X_train, X_test, y_train, y_test =  fe.prepare_train_test_split(
                df_features, test_size=request.test_size
                )
            
            model = LinearRegressionModel()
            train_metrics = model.train(X_train, y_train)
            test_metrics = model.evaluate(X_test, y_test)
            feature_importance = model.get_feature_importance()

            model_key = f'{request.ticker}_{request.model_type}_{request.lookback}'
            trained_models[model_key] = model

            return {
                "model_type": "linear_regression",
                "ticker": request.ticker,
                "status": "trained",
                "model_key": model_key,
                "training_metrics": train_metrics,
                "test_metrics": test_metrics,
                "feature_importance": dict(list(feature_importance.items())[:10]),  # Top 10 features
                "total_features": len(feature_importance),
                "message": f"Model trained successfully. Use model_key '{model_key}' for predictions."
            }
        
        elif request.model_type == 'logistic_regression':
            df_clean = df_features.dropna()
            featire_cols = [col for col in df_clean.columns
                            if col not in ['timestamp', 'target_price', 'targer_direction']]
            
            X = df_clean[featire_cols]
            y = df_clean['target_direction']

            split_idx = int(len(X) * (1 - request.test_size))
            X_train = X.iloc[:split_idx]
            X_test = X.iloc[split_idx:]
            y_train = X.iloc[:split_idx]
            y_test = X.iloc[split_idx:]

            model = LogisticRegressionModel()
            train_metrics = model.train(X_train, y_train)
            test_metrics = model.evaluate(X_test, y_test)

            model_key = f'{request.ticker}_{request.model_type}_{request.lookback}'
            trained_models[model_key] = model

            return {
                'model_type': 'logistic_regression',
                'ticker': request.ticker,
                'status': 'trained',
                'model_key': model_key,
                'training_metrics': train_metrics,
                'test_metrics': test_metrics,
                'message': f"Model trainde successfully. Use model_key '{model_key}' for predictions" 
            }
        
        else: 
            raise HTTPException(
                status_code=400,
                detail=f"Model type '{request.model_type}' not supported. Use: linear_regression, logistic_regression"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error training model: {str(e)}"
        )
    
router.post("/predict")
def predict_price(request: MLPredictRequest):
    try:
        model_key = f'{request.ticker}_{request.model_type}_{request.lookback}'

        if model_key not in trained_models:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_key}' not found. Train the model first."
            )
        
        model = trained_models[model_key]

        market_data = load_data(request.ticker, request.period, request.interval)

        data_list = [
            {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low, 
                'close': candle.close,
                'volume': candle.volume
            }
            for candle in market_data.data
        ]

        fe = FeatureEnginnering()
        df_features = fe.create_features(data_list, lookback=request.period)
        df_clean = df_features.dropna()

        feature_cols = [col for col in df_clean.columns
                        if col not in ['timestamp', 'tarhet_price', 'target_direction']]
        
        X_latest = df_clean[feature_cols].iloc[[-1]]

        if request.model_type == 'lienar_regression':
            prediction = model.predict(X_latest)[0]
            current_price = data_list[-1]['close']

            return {
                'model_type': 'linear_regression',
                'ticker': request.ticker,
                'current_price': round(current_price, 2),
                'predicted_next_price': round(prediction, 2),
                'predicted_change': round(prediction - current_price, 2),
                'predicted_change_percent': round(((prediction - current_price) / current_price) * 100, 2),
                'timestamp': data_list[-1]['timestamp']
            }
        
        elif request.model_type == 'logistic_regression':
            direction = model.predict(X_latest)[0]
            probabilities = model.predict_proba(X_latest)[0]

            return {
                'model_type': 'logistic_regression',
                'ticker': request.ticker,
                'current_price': round(data_list[-1]['close'], 2),
                'predicted_direction': 'UP' if direction == 1 else 'DOWN',
                'probability_down': round(probabilities[0] * 100, 2),
                'probabilities_up': round(probabilities[1] * 100, 2),
                'confidence': round(max(probabilities) * 100, 2),
                'timestamp': data_list[-1]['timestamp']
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Error making prediction: {str(e)}'
        )

@router.get("/models")
def list_trained_models():
    return {
        'total_models': len(trained_models),
        'models': list(trained_models.keys())
    }