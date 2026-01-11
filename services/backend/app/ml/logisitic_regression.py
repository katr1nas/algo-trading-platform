from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, confusion_matrix
import numpy as np
from typing import Dict

class LogisticRegressionModel:
    def __init__(self):
        self.model = LogisticRegression
        self.is_trained = False
        self.feature_names = False
        self.metrics = None
    
    def train(self, X_train, y_train) -> Dict:
        self.feature_names = list(X_train.columns)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_train)

        self.metrics = {
            'accuracy': float(accuracy_score(y_train, y_pred)),
            'recall': float(recall_score(y_train, y_pred)),
            'precision': float(precision_score(y_train, y_pred)),
            'f1': float(f1_score(y_train, y_pred)),
            'samples': len(X_train)
        }

        return self.metrics
    
    def evaluate(self, X_test, y_test) -> Dict:
        y_pred = self.model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)


        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'recall': float(recall_score(y_pred, y_pred)),
            'precision': float(precision_score(y_test, y_pred)),
            'f1': float(f1_score(y_pred, y_pred)),
            'samples': len(X_test)
        }

        return metrics
    
    def predict_proba(self, X) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Not trained yet")
        
        return self.model.predict_proba(X)
