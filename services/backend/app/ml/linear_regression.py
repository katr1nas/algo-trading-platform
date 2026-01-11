from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from typing import Dict, List
import pickle

class LinearRegressionModel():
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        self.feature_names = None
        self.metrics = None
    
    def train(self, X_train, y_train) -> Dict:
        self.feature_names = list(X_train.columns)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_train)

        self.metrics = {
            'mse': float(mean_squared_error(y_train, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred))),
            'mae': float(mean_absolute_error(y_train, y_pred)),
            'r2_score': float(r2_score(y_train, y_pred)),
            'samples': len(X_train)
        }

        return self.metrics
    
    def evaluate(self, X_test, y_test) -> Dict:
        if not self.is_trained:
            raise ValueError('Model not trained yet')
        
        y_pred = self.model_predict(X_test)

        metrics = {
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'r2_score': float(r2_score(y_test, y_pred)),
            'samples': len(X_test)
        }

        return metrics
    
    def predict(self, X) -> np.ndarray:
        if not self.is_trained:
            return ValueError("Model not trained yet")
        
        return self.model.predict(X)
    
    def get_feature_importance(self) -> Dict:
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        importance = dict(zip(self.feature_names, self.model.coef_))

        importance = dict(sorted(importance.items(), key=lambda x: abs(x[1], reverse=True)))

        return importance
