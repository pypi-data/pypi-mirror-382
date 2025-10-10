class Bot:
    def __init__(self, api_key, server_url="http://127.0.0.1:8000"):
        self.api_key = api_key
        self.server_url = server_url

    def advanced_firewall(self, payload=None):
        # Fetch premium logic from server
        resp = requests.post(
            f"{self.server_url}/logic/advanced_firewall",
            headers={"X-API-KEY": self.api_key}
        )
        code = resp.json()["code"]
        
        # Dynamically execute logic
        local_env = {}
        exec(code, {}, local_env)
        if "run" in local_env:
            result = local_env["run"](payload)
            print("[Bot] Result:", result)
            return result
        else:
            print("[Bot] No logic available for your plan")
            return None