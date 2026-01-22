from flask import Flask, request, jsonify, send_from_directory
from blink_detector import BlinkDetector
from screen_tracker import ScreenTimeTracker
from alert_anager import AlertManager  # Fixed typo in the import statement
import json
import webbrowser
import os
import threading
import time
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate("C:/Users/vanaj/purapro/backend/firebase_config.json")  # Path to your Firebase credentials file
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

detector = BlinkDetector()
tracker = ScreenTimeTracker()
alert_mgr = AlertManager()

@app.route('/api/report/<user_id>')
def get_report(user_id):
    # Fetch data for the last 1 day, 7 days, and 30 days
    daily = fetch_reports(user_id, 1)
    weekly = fetch_reports(user_id, 7)
    monthly = fetch_reports(user_id, 30)

    return jsonify({
        "daily": analyze(daily),
        "weekly": analyze(weekly),
        "monthly": analyze(monthly)
    })

def fetch_reports(user_id, days):
    today = datetime.today()
    start_date = today - timedelta(days=days)
    reports_ref = db.collection("users").document(user_id).collection("user_data")
    query = reports_ref.where("__name__", ">=", start_date.strftime("%Y-%m-%d"))
    results = query.stream()

    report_data = []
    for doc in results:
        data = doc.to_dict()
        data["date"] = doc.id
        report_data.append(data)

    return report_data

def analyze(reports):
    total_blink = sum(r.get("blink_rate", 0) for r in reports)
    total_screen = sum(r.get("screen_time", 0) for r in reports)
    count = len(reports)

    return {
        "average_blink_rate": round(total_blink / count, 2) if count else 0,
        "average_screen_time": round(total_screen / count, 2) if count else 0,
        "days": count
    }

@app.route('/')
def serve_ui():
    return send_from_directory("../frontend", "index.html")

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory("../frontend", path)

@app.route('/api/user', methods=['POST'])
def save_user():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    age = data.get('age')
    spectacles = data.get('spectacles')

    # Save user profile in Firestore
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'name': name,
        'age': age,
        'spectacles': spectacles
    })

    tracker.reset()
    detector.blink_count = 0
    print("✅ User profile saved and screen time/blink count reset")

    return jsonify({"status": "saved"})

@app.route('/api/reset_timer', methods=['POST'])
def reset_timer():
    tracker.reset()
    return jsonify({"status": "reset"})

@app.route("/api/data")
def get_data():
    user_id = "user123"  # Example user ID, change this as needed (e.g., from logged-in user session)
    today = datetime.now().strftime("%Y-%m-%d")

    # Use the current date as the document ID for persistence during the day
    document_id = today  # Document ID stays the same throughout the day/session

    blink_count = detector.detect_blink_once()
    bpm = detector.get_blinks_per_minute()
    screen_time = tracker.get_screen_time()

    # Reference to the document for the user on the specific day (document ID = current date)
    user_data_ref = db.collection('users').document(user_id).collection('user_data').document(document_id)

    # Update the document with new data each time
    user_data_ref.set({
        'screen_time': screen_time,
        'blink_rate': bpm,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Store timestamp for the record
    }, merge=True)  # Merge ensures we don't overwrite other data, just update it

    return jsonify({
        "blinks": blink_count,
        "bpm": bpm,
        "screen_time": screen_time
    })

@app.route('/shutdown', methods=['POST'])
def shutdown():
    detector.release()
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return 'Server shutting down...'

def blink_detection_loop():
    while True:
        detector.detect_blink_once()
        time.sleep(0.1)

if __name__ == '__main__':
    # Start blink detection loop in a separate thread
    blink_thread = threading.Thread(target=blink_detection_loop, daemon=True)
    blink_thread.start()
    
    # Open the web UI in the default browser
    webbrowser.open('http://127.0.0.1:5000')
    
    # Start Flask application
    app.run(debug=False)
