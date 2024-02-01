import requests

import requests

# List of proxies to test
proxies =  ["http://145.253.188.132:80","http://202.62.10.210:8080"]
# Test each proxy
for proxy in proxies:
    try:
        response = requests.get("http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=10)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working. IP: {response.json()['origin']}")
        else:
            print(f"Proxy {proxy} failed with status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"Proxy {proxy} failed with error: {e}")
