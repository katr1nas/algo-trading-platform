import numpy as np

class LinearRegressionGD:
    def __init__(self, lr=0.01, epochs=1000, normalize=True):
        self.lr = lr
        self.epochs = epochs
        self.normalize = normalize

        self.w = None
        self.b = 0

        self.mean = None
        self.std = None

    def _normalize(self, X):
        if not self.normalize:
            return X
        
        if self.mean is None:
            self.mean = X.mean(axis = 0)
            self.std = X.std(axis=0) + 1e-8

        return (X - self.mean) / self.std

    def predict(self, X):
        X = np.array(X, dtype=np.float32)
        X = self._normalize(X)
        return np.dot(X, self.w) + self.b

    def fit(self, X, y):
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)

        X = self._normalize(X)

        n_samples, n_features = X.shape

        self.w = np.zeros(n_features)
        self.b = 0

        for _ in range(self.epochs):
            y_pred = np.dot(X, self.w) + self.b

            error = y_pred - y

            dw = (1/n_samples) * np.dot(X.T, error)
            db = (1/n_samples) * np.sum(error)

            self.w -= self.lr * dw
            self.b -= self.lr * db

    def mse(self, y_true, y_pred):
        return np.mean((y_true - y_pred) ** 2)