import base64

key = "123"
encoded_key = base64.b64encode(key.encode()).decode()
print(encoded_key)