import keys2
import user_counter
from datetime import datetime
import os

filename = os.path.join(os.path.dirname(__file__), 'user_counter.json')

# filename = '/home/qparts/ebay_scraper/user_counter.json'  # JSON file to store counters
#
def user_credentials_selector(user=1):
    max_count = 5000
    number_of_users = 4  # Total number of users

    for i in range(user, number_of_users + 1):
        counters = user_counter.load_counters(filename)
        user_str = str(i)
        today = datetime.now().strftime("%Y-%m-%d")
        if counters[user_str]["date"] != today:
            counters[user_str] = {"date": today, "count": 0}
            user_counter.save_counters(counters, filename)
        current_count = user_counter.get_current_count( i,filename)


        if current_count < max_count:
            app_id = getattr(keys2, f'app_id_{i}', None)
            client_secre = getattr(keys2, f'client_secre_{i}', None)
            return app_id, client_secre, i, current_count
        # elif current_count == max_count:


    # If all users have exceeded the limit
    print("All users have exceeded the limit for today.")
    return None, None, None, None

# Example usage
# app_id, client_secre, user = user_credentials_selector()
# print(app_id, client_secre, user)
