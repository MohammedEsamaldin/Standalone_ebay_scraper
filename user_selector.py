import keys2
import user_counter

filename = 'user_data.json'  # JSON file to store counters

def user_credentials_selector(user=1):
    max_count = 5000
    number_of_users = 3  # Total number of users

    for i in range(user, number_of_users + 1):
        current_count = user_counter.get_current_count(filename, i)
        if current_count < max_count:
            app_id = getattr(keys2, f'app_id_{i}', None)
            client_secre = getattr(keys2, f'client_secre_{i}', None)
            return app_id, client_secre, i
    
    # If all users have exceeded the limit
    print("All users have exceeded the limit for today.")
    return None, None, None

# Example usage
app_id, client_secre, user = user_credentials_selector()
print(app_id, client_secre, user)
