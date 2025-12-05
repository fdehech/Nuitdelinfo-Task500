import requests
import sys

def get_token(password):
    url = "http://mayan-edms:8000/api/v4/auth/token/"
    data = {"username": "admin", "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Success! Token: {response.json()['token']}")
            return True
        else:
            print(f"Failed with password '{password}': {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    passwords = ["admin", "changeme", "password", "123456"]
    for pwd in passwords:
        if get_token(pwd):
            break
