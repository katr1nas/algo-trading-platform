import sys
import os

# Добавляем корень проекта в PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.append(ROOT_DIR)

from services.backend.app.core.ml.linear_regression import LinearRegressionGD
import numpy as np


def test_lr():
    X = np.array([[1],[2],[3],[4],[5]])
    y = np.array([3,5,7,9,11])

    model = LinearRegressionGD(lr=0.01, epochs=2000)
    model.fit(X, y)

    print("Predict 6:", model.predict([[6]]))

test_lr()
