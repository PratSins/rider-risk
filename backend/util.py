import pickle
import numpy as np
import warnings
warnings.filterwarnings("ignore")

__model = None

def load_saved_artifacts():
    print("loading saved artifacts...start")
    global __model

    if __model is None:
        with open('./model/random_forest_model (1).pkl', 'rb') as f:
            __model = pickle.load(f)
    print("loading saved artifacts...done")


def getRiskScore(lean_angle_deg, speed, threshold=0.4):
    """
    Calculate the risk score for a given set of input features using the loaded Random Forest model.

    Args:
        lean_angle_deg (float): Lean angle in degrees.
        speed (float): Speed.
        threshold (float): Probability threshold to classify as risky (default: 0.4).

    Returns:
        dict: Risk analysis result containing:
            - 'unsafe_proba': Posterior probability of Unsafe.
            - 'is_risky': Boolean indicating if the instance is classified as risky.
    """
    global __model

    input_features = np.array([[lean_angle_deg, speed]])
    y_proba = __model.predict_proba(input_features)

    # Extract Unsafe probability
    classes = __model.classes_
    unsafe_index = list(classes).index('Unsafe')
    unsafe_proba = y_proba[0, unsafe_index]

    # Determine if the instance is risky based on the threshold
    is_risky = unsafe_proba > threshold

    return {
        "unsafe_proba": unsafe_proba,
        "is_risky": is_risky
    }


if __name__ == '__main__':
    load_saved_artifacts()

    X_test_example = np.array([
        [25, 15],  # Lean angle = 25°, Speed = 15
        [35, 20],  # Lean angle = 35°, Speed = 20
        [45, 5]    # Lean angle = 45°, Speed = 5
    ])
    y_test_example = np.array(['Safe', 'Moderate', 'Unsafe'])

    risk_score = getRiskScore(lean_angle_deg=30, speed=20, threshold=0.4)
    print(f"Risk Score for Single Instance: {risk_score}")

