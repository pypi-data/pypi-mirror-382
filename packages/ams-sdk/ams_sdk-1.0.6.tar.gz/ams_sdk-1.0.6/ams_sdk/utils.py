from ams_sdk.client import AMSClient

# Initialize AMSClient
SERVICE_URL = "<service_url>"   # Replace with actual service URL
API_KEY = "<your-api-key>"      # Replace with your API key

client = AMSClient(SERVICE_URL, API_KEY)

# Authenticate and get Bearer token
try:
    client.authenticate()
    print("Authentication successful!")
except Exception as e:
    print(f"Error during authentication: {e}")

# Query the `/nbstat` endpoint
try:
    params = {
        "location": "US",
        "start": "2025-01-01",
        "txt": "insurance NOT car"
    }
    data = client.query_endpoint("/nbstat", params=params)
    print("Query successful:", data)
except Exception as e:
    print(f"Error during query: {e}")