import requests, json

USER_ID = "f8acfe8f-c2c3-4fe4-b1fd-6d7e7820e93f"
BASE = "http://127.0.0.1:8000"

print("=== 1. Identity fetch ===")
r = requests.get(f"{BASE}/api/identity/{USER_ID}")
print(f"Status: {r.status_code}")
d = r.json()
# Print without embedding
if isinstance(d, dict) and "embedding" in d:
    d.pop("embedding")
print(json.dumps(d, indent=2))

print("\n=== 2. Generate (linkedin) ===")
r2 = requests.post(f"{BASE}/api/generate/", json={
    "user_id": USER_ID,
    "platform": "linkedin",
    "content_type": "post",
    "topic": "Machine Learning"
})
print(f"Status: {r2.status_code}")
if r2.status_code == 200:
    data = r2.json()
    print(f"Got {len(data)} result(s)")
    print(f"Platform: {data[0]['platform']}")
    print(f"Content preview: {data[0]['content'][:200]}")
else:
    print(r2.json())
