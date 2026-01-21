import requests
import time
import logging

class Synapse:
    """
    Simulates the MCP Client (HTTP Bridge).
    Acts as the 'Effector' in the Scientific E2E loop.
    """
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.logger = logging.getLogger("Synapse")

    def execute(self, tool_name, args=None):
        """Execute a tool and measure latency."""
        return self.post("/mcp/tools/execute", {
            "tool_name": tool_name,
            "arguments": args or {}
        })

    def post(self, endpoint, payload):
        """Generic POST request."""
        url = f"{self.base_url}{endpoint}" if endpoint.startswith("/") else f"{self.base_url}/{endpoint}"
        start_t = time.perf_counter()
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            latency = (time.perf_counter() - start_t) * 1000
            
            try:
                data = resp.json()
            except ValueError:
                 return {"success": False, "error": f"Invalid JSON: {resp.text}", "latency": latency, "status_code": resp.status_code}

            # Handle FastAPI errors
            if resp.status_code >= 400:
                return {
                    "success": False, 
                    "error": data.get('detail', 'Unknown Error'), 
                    "latency": latency,
                    "status_code": resp.status_code,
                    "data": data
                }

            # Handle MCP Envelope vs Raw JSON
            if "success" in data:
                return {**data, "latency": latency, "status_code": resp.status_code}
            else:
                # Raw API response assumed successful if 2xx
                return {"success": True, "data": data, "latency": latency, "status_code": resp.status_code}

        except Exception as e:
            return {"success": False, "error": str(e), "latency": (time.perf_counter() - start_t) * 1000}

    def list_tools(self):
        url = f"{self.base_url}/mcp/tools/list"
        try:
            resp = requests.get(url, timeout=5)
            return resp.json()
        except Exception as e:
            return {"tools": [], "error": str(e)}

    def health(self):
        url = f"{self.base_url}/health"
        try:
            resp = requests.get(url, timeout=2)
            return resp.json()
        except Exception:
            return {"status": "offline"}
