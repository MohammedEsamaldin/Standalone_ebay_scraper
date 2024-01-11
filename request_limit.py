import json
from datetime import datetime, timedelta
# /opt/airflow/dags/data/request_counter.json

def counter_updater(counter= 0 , filename ='/home/qparts/ebay_scraper/request_counter.json'):
      with open(filename, 'w') as file:
        json.dump({
            'date_of_counter': datetime.now().isoformat(),
            'current_request_num': counter
        }, file)
      



def limit_updater(filename ='/home/qparts/ebay_scraper/request_counter.json'):
    now = datetime.now()
    with open(filename, 'r') as file:
            counter_data = json.load(file)
            c_date_str = counter_data["date_of_counter"]
            c_date = datetime.strptime(c_date_str,'%Y-%m-%dT%H:%M:%S.%f')
            counter = counter_data["current_request_num"]
    if (now.month == c_date.month) and (now.day == c_date.day):
          print('this is yes')
          return counter
    else:
          print('this is error')
          counter = 0
          counter_updater()
          return counter