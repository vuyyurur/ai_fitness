from firebase_admin import firestore
from datetime import datetime

def save_workout_data(user_id, reps_dict, calories, duration, plank_time=None):
    db = firestore.client()
    date_str = datetime.today().strftime('%Y-%m-%d')
    doc_ref = db.collection("workout_data").document(f"{user_id}_{date_str}")

    existing_data = doc_ref.get().to_dict()

    def get_total(key, new):
        return (existing_data.get(key, 0) if existing_data else 0) + new

    updated_data = {
        "pushups": get_total("pushups", reps_dict.get("pushups", 0)),
        "squats": get_total("squats", reps_dict.get("squats", 0)),
        "curls": get_total("curls", reps_dict.get("curls", 0)),
        "situps": get_total("situps", reps_dict.get("situps", 0)),

        "pushups_good": get_total("pushups_good", reps_dict.get("pushups_good", 0)),
        "pushups_bad": get_total("pushups_bad", reps_dict.get("pushups_bad", 0)),
        "squats_good": get_total("squats_good", reps_dict.get("squats_good", 0)),
        "squats_bad": get_total("squats_bad", reps_dict.get("squats_bad", 0)),
        "situps_good": get_total("situps_good", reps_dict.get("situps_good", 0)),
        "situps_bad": get_total("situps_bad", reps_dict.get("situps_bad", 0)),
        "curls_good": get_total("curls_good", reps_dict.get("curls_good", 0)),
        "curls_bad": get_total("curls_bad", reps_dict.get("curls_bad", 0)),

        "plank_time": get_total("plank_time", plank_time or 0),
        "total_reps": get_total("total_reps", sum(reps_dict.get(k, 0) for k in ['pushups', 'squats', 'curls', 'situps'])),
        "calories": round(get_total("calories", calories), 1),
        "duration": get_total("duration", duration),
        "timestamp": datetime.now()
    }

    doc_ref.set(updated_data)

