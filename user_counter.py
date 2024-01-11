import json
from datetime import datetime

def load_counters(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_counters(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def update_counter(filename, user, max_count=5000):
    counters = load_counters(filename)
    today = datetime.now().strftime("%Y-%m-%d")
    user_str = str(user)
    
    if user_str not in counters or counters[user_str]["date"] != today:
        counters[user_str] = {"date": today, "count": 0}

    if counters[user_str]["count"] < max_count:
        counters[user_str]["count"] += 1
        save_counters(filename, counters)
        return counters[user_str]["count"]
    else:
        return None  # Counter limit reached for the day

def get_current_count(filename, user):
    counters = load_counters(filename)
    user_str = str(user)
    if user_str in counters:
        return counters[user_str]["count"]
    return 0
