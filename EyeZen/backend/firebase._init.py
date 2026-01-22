import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ✅ Step 1: Initialize Firebase with your JSON file
cred = credentials.Certificate("D:/project/purapro/backend/firebase_config.json")  # Make sure the file is in the same folder
firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ Step 2: Save user profile
def save_user_profile(user_id, name, age, spectacles):
    profile_data = {
        "name": name,
        "age": age,
        "spectacles": spectacles
    }
    db.collection('users').document(user_id).collection('profile').document('profile').set(profile_data)
    print(f"✅ Profile saved for {user_id}")

# ✅ Step 3: Save today's screen time and blink rate
def save_daily_data(user_id, screen_time, blink_rate):
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "screen_time": screen_time,
        "blink_rate": blink_rate
    }
    db.collection('users').document(user_id).collection('user_data').document(today).set(data)
    print(f"✅ Data saved for {user_id} on {today}")

# ✅ Test run
save_user_profile("user123", "John", 22, True)
save_daily_data("user123", 120, 14.3)
