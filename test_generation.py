import requests

res = requests.post("http://127.0.0.1:8000/api/generate/", json={
    "user_id": "f8acfe8f-c2c3-4fe4-b1fd-6d7e7820e93f",
    "platform": "linkedin",
    "content_type": "post",
    "topic": "AI in healthcare"
})
print("Status:", res.status_code)
try:
    print(res.json())
except:
    print(res.text)
