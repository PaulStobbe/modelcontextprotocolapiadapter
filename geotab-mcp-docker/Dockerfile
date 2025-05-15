FROM python:3.9-slim

WORKDIR /app

# Installing dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server code
COPY . .

# Expose the port the MCP server will run on
EXPOSE 8000

# Run the MCP server
CMD ["python", "server.py"]
