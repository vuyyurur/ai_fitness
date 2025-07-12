""" from firebase_admin import firestore
from datetime import datetime

def save_workout_data(user_id, reps, calories, duration):
    db = firestore.client()
    date_str = datetime.today().strftime('%Y-%m-%d')
    doc_ref = db.collection("workout_data").document(f"{user_id}_{date_str}")
    
    data = {
        "reps": reps,
        "calories": calories,
        "duration": duration,
        "timestamp": datetime.now()
    }

    doc_ref.set(data)  # overwrites or creates the doc
 """




""" 
from firebase_admin import firestore
from datetime import datetime

def save_workout_data(user_id, reps_dict, calories, duration, plank_time=None):
    db = firestore.client()
    date_str = datetime.today().strftime('%Y-%m-%d')
    doc_ref = db.collection("workout_data").document(f"{user_id}_{date_str}")

    total_reps = sum(reps_dict.get(k, 0) for k in ['pushups', 'squats', 'curls', 'situps'])

    data = {
        "pushups": reps_dict.get("pushups", 0),
        "squats": reps_dict.get("squats", 0),
        "curls": reps_dict.get("curls", 0),
        "situps": reps_dict.get("situps", 0),
        "plank_time": plank_time or 0,
        "total_reps": total_reps,
        "calories": round(calories, 1),
        "duration": duration,
        "timestamp": datetime.now()
    }

    doc_ref.set(data)  # overwrites or creates the doc
 """


from firebase_admin import firestore
from datetime import datetime

def save_workout_data(user_id, reps_dict, calories, duration, plank_time=None):
    db = firestore.client()
    date_str = datetime.today().strftime('%Y-%m-%d')
    doc_ref = db.collection("workout_data").document(f"{user_id}_{date_str}")

    # Fetch existing data if present
    existing_data = doc_ref.get().to_dict()
    
    # Initialize or accumulate values
    def get_total(key, new):
        return (existing_data.get(key, 0) if existing_data else 0) + new

    updated_data = {
        "pushups": get_total("pushups", reps_dict.get("pushups", 0)),
        "squats": get_total("squats", reps_dict.get("squats", 0)),
        "curls": get_total("curls", reps_dict.get("curls", 0)),
        "situps": get_total("situps", reps_dict.get("situps", 0)),
        "plank_time": get_total("plank_time", plank_time or 0),
        "total_reps": get_total("total_reps", sum(reps_dict.get(k, 0) for k in ['pushups', 'squats', 'curls', 'situps'])),
        "calories": round(get_total("calories", calories), 1),
        "duration": get_total("duration", duration),
        "timestamp": datetime.now()
    }

    doc_ref.set(updated_data)
