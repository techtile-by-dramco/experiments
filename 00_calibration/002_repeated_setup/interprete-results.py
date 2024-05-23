import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import plot_partial_dependence
import shap

# Assuming df is your DataFrame with input parameters X1, X2, X3, X4 and output Y
# Load your data into a DataFrame
# df = pd.read_csv('your_data.csv')

# Data Preparation
X = df[['X1', 'X2', 'X3', 'X4']]
y = df['Y']

# 1. Correlation Analysis
correlation_matrix = df.corr()
print(correlation_matrix['Y'].sort_values(ascending=False))
# Interpretation: Higher absolute values indicate stronger linear relationships between inputs and output.

# 2. Scatter Plots
sns.pairplot(df, x_vars=['X1', 'X2', 'X3', 'X4'], y_vars='Y', kind='scatter')
plt.show()
# Interpretation: Visual inspection for relationships (linear, non-linear, etc.) between each input and the output.

# 3. Multiple Linear Regression
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

y_pred = linear_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')
print(f'Coefficients: {dict(zip(X.columns, linear_model.coef_))}')
# Interpretation: Coefficients indicate the direction and magnitude of each input's effect on the output.

# 4. Feature Importance Using Random Forest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

print("Feature importances:")
for f in range(X.shape[1]):
    print(f"{X.columns[indices[f]]}: {importances[indices[f]]}")
# Interpretation: Higher importance values indicate more influential parameters.

# 5. Partial Dependence Plots
plot_partial_dependence(rf_model, X, features=[
                        0, 1, 2, 3], feature_names=X.columns, grid_resolution=50)
plt.show()
# Interpretation: Visualize the effect of each parameter on the output while averaging out the others.

# 6. SHAP Values
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X)
shap.summary_plot(shap_values, X)
# Interpretation: SHAP values show the contribution of each parameter to individual predictions and provide a global view of feature importance.

# Note: Ensure you have the required packages installed, e.g., pandas, numpy, matplotlib, seaborn, sklearn, shap
# You can install them using pip if not already installed:
# !pip install pandas numpy matplotlib seaborn scikit-learn shap
