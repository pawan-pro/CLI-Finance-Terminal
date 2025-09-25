import requests

url = 'https://cloud.olakrutrim.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <your secret key here>'
}

payload = {
    "model": "Phi-4-reasoning-plus",
    "messages": [
        {
            "role": "user",
            "content": "Best way to get to mars?"
        }
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print('Response:', response.json())
except requests.exceptions.RequestException as e:
    print(f'Error: {e}')