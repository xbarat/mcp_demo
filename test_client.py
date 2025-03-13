from mcp.client import Client

# Create a client
client = Client("http://localhost:8000")

# Test the add tool
result = client.call("add", a=5, b=3)
print(f"5 + 3 = {result}")

# Test the greeting resource
greeting = client.get("greeting://Alice")
print(f"Greeting: {greeting}")