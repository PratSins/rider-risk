import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def initialize_firestore(service_account_key_path):
    cred = credentials.Certificate(service_account_key_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def send_data_to_firestore(db, collection_name, data):
    db.collection(collection_name).add(data)
    print("Data successfully sent to Firestore!")

def main():
    service_account_key_path = ""
    collection_name = "score_1"

    db = initialize_firestore(service_account_key_path)

    try:
        risk_score = float(input("Enter risk score: "))
        lean_angle = float(input("Enter lean angle: "))
        cummulative_speed = float(input("Enter cummulative speed: "))
    except ValueError:
        print("Invalid input. Please enter numerical values.")
        return

    data = {
        "risk_score": risk_score,
        "lean_angle": lean_angle,
        "cummulative_speed": cummulative_speed,
        "timestamp": datetime.now(),
    }

    send_data_to_firestore(db, collection_name, data)

if __name__ == "__main__":
    main()