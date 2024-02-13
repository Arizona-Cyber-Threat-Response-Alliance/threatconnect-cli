import requests
import hmac
import hashlib
import base64
import os
import time

# Retrieve Access ID and Secret Key from environment variables
tc_accessid = os.getenv('tc_accessid')
tc_secretkey = os.getenv('tc_secretkey')

print("Please provide an instance name. Example: company.threatconnect.com")
instance_name=input("Instance name: ")

# Ensure both the Access ID and Secret Key are available
if not tc_accessid or not tc_secretkey:
    raise ValueError("Missing environment variables for Access ID or Secret Key")

# Function to generate the Authorization header
def generate_auth_header(api_path, http_method, timestamp):
    # Create the message to sign
    message = f"{api_path}:{http_method}:{timestamp}"

    # Calculate HMAC SHA256 signature and encode it in base64
    signature = base64.b64encode(hmac.new(tc_secretkey.encode(), message.encode(), hashlib.sha256).digest()).decode()

    # Construct the Authorization header
    return f"TC {tc_accessid}:{signature}"

# Function to query the ThreatConnect Owners API
def query_owners_api():
    # API endpoint for the owners
    api_url = f'https://{instance_name}.threatconnect.com/api/v2/owners'

    # Generate timestamp
    timestamp = str(int(time.time()))

    # Generate Authorization header
    api_path = '/api/v2/owners'  # Update this path to match the new endpoint
    auth_header = generate_auth_header(api_path, 'GET', timestamp)

    # Headers
    headers = {
        'Timestamp': timestamp,
        'Authorization': auth_header,
        'Accept': 'application/json'
    }

    # Make the GET request
    response = requests.get(api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response JSON if the request was successful
        print(response.json())
    else:
        # Print the error if the request failed
        print(f"Error: {response.status_code} - {response.text}")

# Call the function to query the API
query_owners_api()
