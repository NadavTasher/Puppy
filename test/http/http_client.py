from puppy.http.client import HTTPClient

client = HTTPClient()
response = client.get(b"https://github.com")
response = client.get(b"https://github.com")
print(response)