import requests
import re

url = "http://127.0.0.1:8000/api/users/register/"
payload = {
    "full_name": "Test User",
    "password": "password123",
    "email": "",
    "phone": "0987654321",
    "role": "customer"
}

try:
    response = requests.post(url, json=payload)
    print("Status:", response.status_code)
    
    # Try to find Django exception message using regex
    match = re.search(r'<div class="exception_value">([^<]+)</div>', response.text)
    if match:
        print("Exception:", match.group(1).strip())
    else:
        # Fallback to general exception search
        match = re.search(r'<h1>([^<]+)</h1>', response.text)
        if match:
            print("H1:", match.group(1).strip())
        print("Response saved to error.html")
        with open('error.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
except Exception as e:
    print("Error:", str(e))
