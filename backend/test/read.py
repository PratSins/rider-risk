import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

def initialize_firestore(service_account_key_path):
    cred = credentials.Certificate(service_account_key_path)

    firebase_admin.initialize_app(cred)
    return firestore.client()

def fetch_top_readings(db, collection_name, order_by_field, limit=10):
    query = (
        db.collection(collection_name)
        .order_by(order_by_field, direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    results = query.stream()
    data = [doc.to_dict() for doc in results]
    return data


def main():
    service_account_key_path = ""
    collection_name = "readings3"
    order_by_field = "timestamp"

    db = initialize_firestore(service_account_key_path)
    data = fetch_top_readings(db, collection_name, order_by_field)

    df = pd.DataFrame(data)
    print(df)

if __name__ == "__main__":
    main()
