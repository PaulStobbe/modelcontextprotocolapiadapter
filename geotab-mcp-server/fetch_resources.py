import os
import requests
import zipfile
from io import BytesIO

# Create directories
os.makedirs('mcp_spec', exist_ok=True)
os.makedirs('python_sdk', exist_ok=True)

# Fetch MCP specification
mcp_spec_url = 'https://modelcontextprotocol.io/llms-full.txt'
response = requests.get(mcp_spec_url)
if response.status_code == 200:
    with open('mcp_spec/llms-full.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Downloaded MCP specification to mcp_spec/llms-full.txt")
else:
    print(f"Failed to download MCP specification: {response.status_code}")

# Fetch Python SDK from GitHub
sdk_url = 'https://github.com/modelcontextprotocol/python-sdk/archive/refs/heads/main.zip'
response = requests.get(sdk_url)
if response.status_code == 200:
    # Extract the ZIP file
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall('python_sdk')
    print("Downloaded and extracted Python SDK to python_sdk/")
else:
    print(f"Failed to download Python SDK: {response.status_code}")

print("Resource fetching complete.")
