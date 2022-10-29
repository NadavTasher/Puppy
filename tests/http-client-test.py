from puppy.http.client.client import HTTPClient

client = HTTPClient()

print(client.get("http://example.com/"))