import util
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import numpy as np
import math
from datetime import datetime
import keyboard
import const_path

def initialize_firestore(service_account_key_path):
    cred = credentials.Certificate(service_account_key_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def fetch_top_readings(db, collection_name_read, order_by_field, limit=5):
    query = (
        db.collection(collection_name_read)
        .order_by(order_by_field, direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    results = query.stream()
    data = [doc.to_dict() for doc in results]
    return data

def send_data_to_firestore(db, collection_name_write, data):
    db.collection(collection_name_write).add(data)
    print("\nData successfully sent to Firestore!\n")

# LEAN ANGLE
def kalman_filter(state_estimate, estimate_covariance, process_variance, measurement_variance, measurement, control_input, dt):
    predicted_state = state_estimate + control_input * dt
    predicted_covariance = estimate_covariance + process_variance
    kalman_gain = predicted_covariance / (predicted_covariance + measurement_variance)
    updated_state = predicted_state + kalman_gain * (measurement - predicted_state)
    updated_covariance = (1 - kalman_gain) * predicted_covariance

    return updated_state, updated_covariance

def calculate_lean_angle(df):
    df['pitch'] = np.arctan2(-df['ax'], np.sqrt(df['ay']**2 + df['az']**2)) * (180 / np.pi)
    df['roll'] = np.arctan2(df['ay'], np.sqrt(df['ax']**2 + df['az']**2)) * (180 / np.pi)
    df['gx'] = df['gx'] * (180 / np.pi)
    df['gy'] = df['gy'] * (180 / np.pi)

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
    
    df['filtered_pitch_rad'] = np.deg2rad(df['filtered_pitch'])
    df['filtered_roll_rad'] = np.deg2rad(df['filtered_roll'])

    df['lean_angle_rad'] = np.arctan2(
        np.sqrt(df['filtered_pitch_rad']**2 + df['filtered_roll_rad']**2), 1
    )
    df['lean_angle_deg'] = np.rad2deg(df['lean_angle_rad'])  


# CUMMULATIVE SPEED
def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def calculate_speed(row1, row2):
    distance = haversine(row1['Latitude'], row1['Longitude'], row2['Latitude'], row2['Longitude'])
    time_delta = (row2['timestamp'] - row1['timestamp']).total_seconds()
    if time_delta == 0:
        return 0, 0
    speed = distance / time_delta
    return distance, speed

def calc_speed(df):
    df['cumulative_distance'] = 0
    df['cumulative_time'] = 0
    df['cumulative_speed'] = 0

    cumulative_distance = 0
    cumulative_time = 0

    for i in range(1, len(df)):
        distance, speed = calculate_speed(df.iloc[i-1], df.iloc[i])
        df.at[i, 'speed_m_s'] = speed
        cumulative_distance += distance
        cumulative_time += (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds()
        df.at[i, 'cumulative_distance'] = cumulative_distance
        df.at[i, 'cumulative_time'] = cumulative_time
        if cumulative_time != 0:
            df.at[i, 'cumulative_speed'] = cumulative_distance / cumulative_time

    df["speed_m_s"] = df["speed_m_s"].fillna(0)


service_account_key_path = const_path.PATH
db = initialize_firestore(service_account_key_path)

collection_name_read = "readings3"
collection_name_write = "score_1"

util.load_saved_artifacts()

def execute():
    order_by_field = "timestamp"
    data = fetch_top_readings(db, collection_name_read, order_by_field)

    df = pd.DataFrame(data)
    desired_order = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "Latitude", "Longitude"]
    df = df[desired_order]

    df = df.iloc[::-1].reset_index(drop=True)
    # Ensure the timestamp column is in datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["dt"] = df["timestamp"].diff().dt.total_seconds()
    df["dt"] = df["dt"].fillna(0)
    
    
    calculate_lean_angle(df)
    calc_speed(df)
    desired_order = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "Latitude", "Longitude", "dt", "lean_angle_deg", "speed_m_s", "cumulative_speed"]
    df = df[desired_order]
    
    # print(df, end="\n\n\n\n")

    last_row = df.iloc[-1]
    
    lean_angle_degree = last_row["lean_angle_deg"]
    speed_ms = last_row["speed_m_s"]
    # cs = last_row["cumulative_speed"]
    
    risk_dict = util.getRiskScore(lean_angle_deg=lean_angle_degree, speed=speed_ms)
    
    print()
    print(risk_dict)
    
    risk_score = risk_dict["unsafe_proba"] * 100
    print(risk_score)
    
    data = {
        "risk_score": risk_score,
        "lean_angle": lean_angle_degree,
        "cummulative_speed": speed_ms,
        "timestamp": datetime.now(),
    }

    send_data_to_firestore(db, collection_name_write, data)


if __name__ == "__main__":
    while True:
        for i in range(1, 3000):
            pass
        execute()
        if keyboard.is_pressed('d'):
            print("You pressed 'd'. Exiting the loop.")
            break

