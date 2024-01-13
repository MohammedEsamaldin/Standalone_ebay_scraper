import json
from datetime import datetime

filename = '/home/qparts/ebay_scraper/user_counter.json'
def load_counters(filename= '/home/qparts/ebay_scraper/user_counter.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return {}
    except OSError as e:
        print(f"OS error occurred: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

def save_counters(data , filename ='/home/qparts/ebay_scraper/user_counter.json' ):
    print('saving')
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def update_counter(user , filename ='/home/qparts/ebay_scraper/user_counter.json' , max_count=5000):
    counters = load_counters(filename)
    today = datetime.now().strftime("%Y-%m-%d")
    user_str = str(user)
    
    if user_str not in counters or counters[user_str]["date"] != today:
        counters[user_str] = {"date": today, "count": 0}

    if counters[user_str]["count"] < max_count:
        counters[user_str]["count"] += 1
        save_counters(counters, filename)
        return counters[user_str]["count"]
    else:
        return None  # Counter limit reached for the day

def get_current_count(user,  filename ='/home/qparts/ebay_scraper/user_counter.json'):
    print('getting current count')
    counters = load_counters(filename)
    user_str = str(user)
    if user_str in counters:
        print('user found ')
        return counters[user_str]["count"]
    return 0
# current = update_counter(filename=filename,user= 4)
# print(current)