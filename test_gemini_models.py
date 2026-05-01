from llm_service import get_client

def test():
    client = get_client()
    for m in client.models.list_models():
        if "gemini" in m.name:
            print(m.name)

test()
