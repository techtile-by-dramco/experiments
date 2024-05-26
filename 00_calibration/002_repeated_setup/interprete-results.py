import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



df = pd.read_csv('data_scope_20240523141330.txt', names=[
                 "meas_id", "phase_diff"], header=None, sep='\s+')

df.loc[(df['phase_diff'] < 180), 'phase_diff'] = df['phase_diff'].add(360)

df['phase_diff'] -= 360

fig, axes = plt.subplots(nrows=1, ncols=2)
df["phase_diff"].plot.hist(figsize=(10, 8), ax=axes[0], bins=180)
df.boxplot(column=['phase_diff'], ax=axes[1])

fields = ["meas_id", "hostname", "meas_type", "tx_ch0", "tx_ch1", "rx_ch0", "rx_ch1", "_0", "_1"]

df1 = pd.read_csv('data_T03_20240523141330.txt',
                  names=fields, header=None, sep=';')

df2 = pd.read_csv('data_T04_20240523141330.txt',
                  names=fields, header=None, sep=';')

# substitute nans where required 
# df1.loc[df1.where(df1['meas_type'] == "PLL"), "rx_ch1"] = np.nan
# df2.loc[df1.where(df2['meas_type'] == "PLL"), "rx_ch1"] = np.nan



df1.drop(columns=["_0", "_1"], inplace=True)
df2.drop(columns=["_0", "_1"], inplace=True)


merged_df = pd.merge(df1, df2, on=['meas_id', "meas_type"], how = 'outer',
                     suffixes=('_df1', '_df2'))

merged_df["phase_diff"] = None

# Iterate over rows
for index, row in df.iterrows():
    merged_df.loc[merged_df['meas_id'] == row['meas_id'], "phase_diff"] = row["phase_diff"]


merged_df["rx_ch0_diff"] = np.abs(merged_df["rx_ch0_df1"] - merged_df["rx_ch0_df2"])

merged_df["rx_ch0_abs_add"] = np.abs(merged_df["rx_ch0_df1"]-np.pi) + np.abs(merged_df["rx_ch0_df2"]-np.pi)

merged_df.where(merged_df['meas_type'] == "PLL").plot.scatter(x='rx_ch0_diff',
                y='phase_diff')


merged_df.where(merged_df['meas_type'] == "PLLCK").plot.scatter(x='rx_ch0_diff',
                                                              y='phase_diff')

merged_df.where(merged_df['meas_type'] == "LBCK").plot.scatter(x='rx_ch1_df1',
                                                                y='phase_diff',title="LBCK 1")
merged_df.where(merged_df['meas_type'] == "LBCK").plot.scatter(x='rx_ch1_df2',
                                                               y='phase_diff', title="LBCK 2")

merged_df.where(merged_df['meas_type'] == "PLLCK").plot.scatter(x='rx_ch0_abs_add',
                                                                y='phase_diff', title="PLLCK rx_ch0_abs_add")

plt.show()

print(merged_df.head(10))

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.inspection import plot_partial_dependence
# import shap

# # Assuming df is your DataFrame with input parameters X1, X2, X3, X4 and output Y
# # Load your data into a DataFrame
# # df = pd.read_csv('your_data.csv')

# # Data Preparation
# X = df[['X1', 'X2', 'X3', 'X4']]
# y = df['Y']

# # 1. Correlation Analysis
# correlation_matrix = df.corr()
# print(correlation_matrix['Y'].sort_values(ascending=False))
# # Interpretation: Higher absolute values indicate stronger linear relationships between inputs and output.

# # 2. Scatter Plots
# sns.pairplot(df, x_vars=['X1', 'X2', 'X3', 'X4'], y_vars='Y', kind='scatter')
# plt.show()
# # Interpretation: Visual inspection for relationships (linear, non-linear, etc.) between each input and the output.

# # 3. Multiple Linear Regression
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.2, random_state=42)

# linear_model = LinearRegression()
# linear_model.fit(X_train, y_train)

# y_pred = linear_model.predict(X_test)
# mse = mean_squared_error(y_test, y_pred)
# print(f'Mean Squared Error: {mse}')
# print(f'Coefficients: {dict(zip(X.columns, linear_model.coef_))}')
# # Interpretation: Coefficients indicate the direction and magnitude of each input's effect on the output.

# # 4. Feature Importance Using Random Forest
# rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
# rf_model.fit(X_train, y_train)

# importances = rf_model.feature_importances_
# indices = np.argsort(importances)[::-1]

# print("Feature importances:")
# for f in range(X.shape[1]):
#     print(f"{X.columns[indices[f]]}: {importances[indices[f]]}")
# # Interpretation: Higher importance values indicate more influential parameters.

# # 5. Partial Dependence Plots
# plot_partial_dependence(rf_model, X, features=[
#                         0, 1, 2, 3], feature_names=X.columns, grid_resolution=50)
# plt.show()
# # Interpretation: Visualize the effect of each parameter on the output while averaging out the others.

# # 6. SHAP Values
# explainer = shap.TreeExplainer(rf_model)
# shap_values = explainer.shap_values(X)
# shap.summary_plot(shap_values, X)
# # Interpretation: SHAP values show the contribution of each parameter to individual predictions and provide a global view of feature importance.

# # Note: Ensure you have the required packages installed, e.g., pandas, numpy, matplotlib, seaborn, sklearn, shap
# # You can install them using pip if not already installed:
# # !pip install pandas numpy matplotlib seaborn scikit-learn shap
