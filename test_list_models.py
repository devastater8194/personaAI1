from llm_service import get_client

client = get_client()
for m in client.models.list():
    print(m.name)
