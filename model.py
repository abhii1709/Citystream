import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib


# Load your dataset
df = pd.read_csv("../simple.csv")  # Replace with your actual path

# Separate out the location column
location = df['location']
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Normalize only numeric features (excluding location)
features = [col for col in df.columns if col != 'location']
scaler = MinMaxScaler()
df_normalized = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)

# Add back location column for reference
df_normalized['location'] = location

# Save the scaler for real-time use
joblib.dump(scaler, "scaler.pkl")

# Define dummy logic to create target signal durations
df_normalized['green_duration'] = (df_normalized['vehicle_count'] * 0.5 +
                                   df_normalized['congestion_level'] * 0.3 +
                                   df_normalized['weather'] * 0.2) * 60

df_normalized['yellow_duration'] = df_normalized['green_duration'] * 0.2
df_normalized['red_duration'] = 180 - (df_normalized['green_duration'] + df_normalized['yellow_duration'])

# Clip red duration to avoid negative values
df_normalized['red_duration'] = df_normalized['red_duration'].clip(lower=5)

# Split features and target
X = df_normalized.drop(['green_duration', 'yellow_duration', 'red_duration', 'location'], axis=1)
y = df_normalized[['green_duration', 'yellow_duration', 'red_duration']]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("Mean Squared Error:", mse)
print("R^2 Score:", r2)

# Save model

joblib.dump(model,"D:\\cityStream\\ml\\model\\model.pkl" )

# Visualize feature importance (for green light only)
importances = model.estimators_[0].feature_importances_
feat_importance_df = pd.DataFrame({"Feature": X.columns, "Importance": importances})
feat_importance_df = feat_importance_df.sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x="Importance", y="Feature", data=feat_importance_df)
plt.title("Feature Importance for Green Light Duration")
plt.tight_layout()
plt.savefig("feature_importance.png")
plt.show()

# Plot actual vs predicted durations
for i, color in enumerate(['green', 'yellow', 'red']):
    plt.figure(figsize=(6, 4))
    plt.scatter(y_test.iloc[:, i], y_pred[:, i], alpha=0.6)
    plt.xlabel(f"Actual {color.title()} Duration")
    plt.ylabel(f"Predicted {color.title()} Duration")
    plt.title(f"Actual vs Predicted {color.title()} Light Duration")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{color}_duration_comparison.png")
    plt.show()
