import requests

res = requests.post("http://127.0.0.1:8000/api/identity/save", json={
    "user_id": "test-uuid-1234",
    "name": "Test User",
    "domain": "AI",
    "role": "Engineer",
    "journey": "A short journey"
})
print(res.json())
