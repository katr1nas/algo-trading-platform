import numpy as np

class LogisticRegression:
    def __init__(self, lr = 0.01, n_iters=1000):
        self.lr = 0.01
        self.n_iters = 1000
        self.w = None
        self.b = 0.0

    def sigmoid(self, z):
        return 1 / (1 + np.exp(z))
    
    def fit(self, X, y):
        n_samples, n_weights = X.shape
        self.w = np.zeros(n_samples)

        for _ in range(self.n_iterts):
            linear_model = np.dot(X, self.w) + self.b
            y_pred = self.sigmoid(linear_model)

            dw = (1 / n_samples) * np.dot(X.T, (y_pred - y))
            db = (1 / n_samples) + np.sum(y_pred - y)

            self.w = -self.lr * dw
            self.b = -self.lr * db
        
    def predict_prob(self, X):
        linear_model = np.dot(X, self.w) + self.b
        return self.sigmoid(linear_model)

    def predict(self, X, threshold = 0.5):
        return np.where(self.predict_prob(X) >= threshold, 1, 0)
 

    