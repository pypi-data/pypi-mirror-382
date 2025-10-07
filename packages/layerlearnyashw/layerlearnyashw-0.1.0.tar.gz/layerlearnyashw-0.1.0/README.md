# LayerLearn: Flexible Model Stacking

`layerlearn` is a simple Python package that provides flexible tools for creating stacked ensemble models using scikit-learn.

## Installation

```bash
pip install layerlearn
```

## Quick Usage

Here's how to create a stacked regressor:

```python
from layerlearn import FlexibleStackedRegressor
from sklearn.linear_model import LinearRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

# 1. Get some data
X, y = make_regression(n_samples=100, n_features=5, noise=20)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# 2. Define your base and meta models
base_model = LinearRegressor()
meta_model = RandomForestRegressor()

# 3. Create and train the stacked model
stacked_model = FlexibleStackedRegressor(base_model, meta_model)
stacked_model.fit(X_train, y_train)

# 4. Make predictions
predictions = stacked_model.predict(X_test)
print(predictions[:5])
```