import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone

class FlexibleStackedRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, base_model, meta_model):

        # Use clone to ensure that the original models are not modified
        self.base_model = clone(base_model)
        self.meta_model = clone(meta_model)

    def fit(self, X, y):
        # Step 1: Train the base model
        self.base_model.fit(X, y)
        
        # Step 2: Get predictions from the base model
        base_predictions = self.base_model.predict(X)
        
        # Step 3: Create the new feature set by combining original features
        # with the base model's predictions.
        X_meta = np.c_[X, base_predictions]
        
        # Step 4: Train the meta model on the new feature set
        self.meta_model.fit(X_meta, y)
        
        return self

    def predict(self, X):
        # Step 1: Get predictions from the base model
        base_predictions = self.base_model.predict(X)
        
        # Step 2: Create the meta feature set for prediction
        X_meta = np.c_[X, base_predictions]
        
        # Step 3: Make the final prediction using the meta model
        return self.meta_model.predict(X_meta)