# -*- coding: utf-8 -*-
"""Untitled15.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_d9zPIit_6BdqZmNLMV5hhxDRj6RXpM9
"""

import pandas as pd
import numpy as np

# file_path = '/content/pr_project.xlsx'
file_path = './labeled_data_with_clusters.xlsx'

df = pd.read_excel(file_path, sheet_name='Sheet1')

df = df.dropna()
df = df.reset_index(drop=True)

import numpy as np
#df['pitch'] = np.arctan2(-df['ax'], np.sqrt(df['ay']**2 + df['az']**2)) * (180 / np.pi)
#df['roll'] = np.arctan2(df['ay'], df['az']) * (180 / np.pi)
df['pitch'] = np.arctan2(-df['ax'], np.sqrt(df['ay']**2 + df['az']**2)) * (180 / np.pi)
df['roll'] = np.arctan2(df['ay'], np.sqrt(df['ax']**2 + df['az']**2)) * (180 / np.pi)

# output_path = '/content/pr_project.xlsx'
output_path = './labeled_data_with_clusters1.xlsx'
df.to_excel(output_path, index=False)

print(df.head())

df['gx'] = df['gx'] * (180 / np.pi)
df['gy'] = df['gy'] * (180 / np.pi)

import numpy as np
import pandas as pd

def kalman_filter(state_estimate, estimate_covariance, process_variance, measurement_variance, measurement, control_input, dt):
    predicted_state = state_estimate + control_input * dt
    predicted_covariance = estimate_covariance + process_variance
    kalman_gain = predicted_covariance / (predicted_covariance + measurement_variance)
    updated_state = predicted_state + kalman_gain * (measurement - predicted_state)
    updated_covariance = (1 - kalman_gain) * predicted_covariance

    return updated_state, updated_covariance
df['dt'] = df['seconds_elapsed'].diff().fillna(0.01)

# Initialize Kalman filter parameters
pitch_state, pitch_cov = 0.0, 1.0
roll_state, roll_cov = 0.0, 1.0
process_variance = 0.01
measurement_variance = 0.1

filtered_pitch = []
filtered_roll = []

# Kalman filter for pitch and roll fusion
for i in range(len(df)):
    dt = df['dt'].iloc[i]
    pitch_measurement = df['pitch'].iloc[i]
    roll_measurement = df['roll'].iloc[i]
    gx_control = df['gx'].iloc[i]
    gy_control = df['gy'].iloc[i]

    # Update pitch state
    pitch_state, pitch_cov = kalman_filter(
        state_estimate=pitch_state,
        estimate_covariance=pitch_cov,
        process_variance=process_variance,
        measurement_variance=measurement_variance,
        measurement=pitch_measurement,
        control_input=gx_control,
        dt=dt
    )

    # Update roll state
    roll_state, roll_cov = kalman_filter(
        state_estimate=roll_state,
        estimate_covariance=roll_cov,
        process_variance=process_variance,
        measurement_variance=measurement_variance,
        measurement=roll_measurement,
        control_input=gy_control,
        dt=dt
    )

    filtered_pitch.append(pitch_state)
    filtered_roll.append(roll_state)

# Append filtered results to the dataframe
df['filtered_pitch'] = filtered_pitch
df['filtered_roll'] = filtered_roll

# Save the processed data to an Excel file
# output_path = '/content/pr_project.xlsx'
output_path = './labeled_data_with_clusters1.xlsx'
df.to_excel(output_path, index=False)

# Display filtered data for verification
print(df[['pitch', 'roll', 'filtered_pitch', 'filtered_roll']].head())

df.head()

import matplotlib.pyplot as plt

# Plot Filtered Pitch vs Measured Pitch
plt.figure(figsize=(12, 6))
plt.plot(df['pitch'], label='Accelerometer Pitch', linestyle='--', alpha=0.7)
plt.plot(df['filtered_pitch'], label='Filtered Pitch', alpha=0.9)
plt.title('Filtered Pitch vs Accelerometer Pitch')
plt.xlabel('Sample Index')
plt.ylabel('Pitch (degrees)')
plt.legend()
plt.grid()
plt.show()

# Plot Filtered Roll vs Measured Roll
plt.figure(figsize=(12, 6))
plt.plot(df['roll'], label='Accelerometer Roll', linestyle='--', alpha=0.7)
plt.plot(df['filtered_roll'], label='Filtered Roll', alpha=0.9)
plt.title('Filtered Roll vs Accelerometer Roll')
plt.xlabel('Sample Index')
plt.ylabel('Roll (degrees)')
plt.legend()
plt.grid()
plt.show()

import numpy as np

# Ensure pitch and roll are in radians
df['filtered_pitch_rad'] = np.deg2rad(df['filtered_pitch'])  # Convert from degrees to radians
df['filtered_roll_rad'] = np.deg2rad(df['filtered_roll'])    # Convert from degrees to radians

df['lean_angle_rad'] = np.arctan2(
    np.sqrt(df['filtered_pitch_rad']**2 + df['filtered_roll_rad']**2), 1
)
df['lean_angle_deg'] = np.rad2deg(df['lean_angle_rad'])

# Display results
print(df[['filtered_pitch', 'filtered_roll', 'lean_angle_deg']].head())

# Define a function to assign labels based on thresholds
def assign_labels(row):
    if row['lean_angle_deg'] < 20 and row['speed'] < 6:
        return 'Safe'
    elif 20 <= row['lean_angle_deg'] <= 40 and 6<= row['speed'] <= 7:
        return 'Moderate'
    elif row['lean_angle_deg'] > 40 or row['speed'] > 8:
        return 'Unsafe'
    else:
        return 'Moderate'

df['safety_label'] = df.apply(assign_labels, axis=1)

# Save the labeled data to an Excel file
# output_path = 'labeled_data_with_clusters.xlsx'
output_path = './labeled_data_with_clusters1.xlsx'
df.to_excel(output_path, index=False)

print(f"Labels generated and saved to {output_path}.")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Step 1: Prepare Features and Labels
X = df[['lean_angle_deg', 'speed']].values  # Features: Lean angle and speed
y = df['safety_label'].values  # Target: Safety label (Safe, Moderate, Unsafe)

# Step 2: Split Data into Train and Test Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 3: Initialize and Train the Random Forest Model
rf_classifier = RandomForestClassifier(random_state=42, n_estimators=100)
rf_classifier.fit(X_train, y_train)

# Step 4: Evaluate the Model
y_pred = rf_classifier.predict(X_test)

# Calculate Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Random Forest Accuracy: {accuracy:.4f}")

# Display Classification Report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Step 5: Save the Trained Model as a Pickle File
with open('random_forest_model.pkl', 'wb') as file:
    pickle.dump(rf_classifier, file)
print("Random Forest model saved as 'random_forest_model.pkl'.")

# Step 6: (Optional) Load the Model for Future Use
with open('random_forest_model.pkl', 'rb') as file:
    loaded_rf_classifier = pickle.load(file)

# Test the loaded model
loaded_predictions = loaded_rf_classifier.predict(X_test)
print(f"Loaded Model Accuracy: {accuracy_score(y_test, loaded_predictions):.4f}")

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
X = df[['lean_angle_deg', 'speed']].values
y = df['safety_label'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
bins_lean_angle = np.linspace(0, 90, 10)
bins_speed = np.linspace(0, 15, 10)
X_train_binned = np.column_stack([
    np.digitize(X_train[:, 0], bins_lean_angle),
    np.digitize(X_train[:, 1], bins_speed)
])

X_test_binned = np.column_stack([
    np.digitize(X_test[:, 0], bins_lean_angle),
    np.digitize(X_test[:, 1], bins_speed)
])
class_counts = {cls: (y_train == cls).sum() for cls in np.unique(y_train)}
total_count = len(y_train)

priors = {cls: count / total_count for cls, count in class_counts.items()}
likelihoods = {}

for cls in np.unique(y_train):
    cls_indices = (y_train == cls)
    feature_counts = {}

    for i in range(X_train_binned.shape[1]):
        feature_counts[i] = np.bincount(X_train_binned[cls_indices, i], minlength=10)
    likelihoods[cls] = {
        i: feature_counts[i] / class_counts[cls]  # Normalize by class count
        for i in range(X_train_binned.shape[1])
    }

def predict_probabilities(X_binned, priors, likelihoods):
    posteriors = []

    for cls in priors.keys():
        posterior = np.log(priors[cls])  # Start with log-prior
        for i, bin_index in enumerate(X_binned):
            likelihood = likelihoods[cls][i][bin_index] if bin_index < len(likelihoods[cls][i]) else 1e-6  # Smoothing
            posterior += np.log(likelihood)
        posteriors.append(posterior)
    posteriors = np.exp(posteriors)
    total_prob = np.sum(posteriors)
    return posteriors / total_prob
y_probabilities = []
y_pred = []

for x in X_test_binned:
    probabilities = predict_probabilities(x, priors, likelihoods)
    y_probabilities.append(probabilities)
    y_pred.append(np.argmax(probabilities))
y_probabilities = np.array(y_probabilities)
y_pred = np.array([list(priors.keys())[pred] for pred in y_pred])  # Map indices to class labels

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Posterior Probabilities for the first instance:")
for cls, prob in zip(priors.keys(), y_probabilities[0]):
    print(f"{cls}: {prob:.4f}")

