# Import the classes from your newly installed package
from layerlearn import FlexibleStackedClassifier, FlexibleStackedRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

print("[SUCCESS] Successfully imported from the layerlearn package!")

# You can even instantiate the classes to make sure they work
try:
    # We need to pass dummy models to test instantiation
    base_model = LinearRegression()
    meta_model = RandomForestClassifier()
    
    classifier = FlexibleStackedClassifier(base_model, meta_model)
    regressor = FlexibleStackedRegressor(base_model, meta_model)
    print("[SUCCESS] Successfully created a FlexibleStackedClassifier instance.")
    print("[SUCCESS] Successfully created a FlexibleStackedRegressor instance.")
except Exception as e:
    print(f"[ERROR] Failed to instantiate classes. Error: {e}")