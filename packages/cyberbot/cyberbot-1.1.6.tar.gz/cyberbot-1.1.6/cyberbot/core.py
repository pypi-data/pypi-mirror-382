import threading
import time
from flask import url_for, request, abort, Flask
import threading, time, requests

class Bot:
    def __init__(self, app: Flask):
        self.app = app
        self._inject_security()

    def _inject_security(self):
        @self.app.before_request
        def firewall():
            # Example simple checks
            if "DROP TABLE" in request.query_string.decode().upper():
                abort(403, "CyberBot: SQLi attempt blocked 🚫")

            if "<script>" in request.data.decode().lower():
                abort(403, "CyberBot: XSS attempt blocked 🚫")

    def run(self, *args, **kwargs):
        # delegate to Flask’s run
        self.app.run(*args, **kwargs)
        
def keep_host_alive(url, interval=60):
    """
    Sends an external HTTP request to your Render app every `interval` seconds
    to prevent spin down.
    """
    def _ping():
        while True:
            try:
                resp = requests.get(url)
                print(f"[keep_render_alive] {url} -> {resp.status_code}")
            except Exception as e:
                print(f"[keep_render_alive] Error: {e}")
            time.sleep(interval)

    t = threading.Thread(target=_ping, daemon=True)
    t.start()
    
def keep_app_alive(app, endpoint: str, interval: int = 60, **kwargs):
    """
    Internally calls a Flask endpoint every `interval` seconds.
    """
    def _ping():
        with app.test_client() as client:
            while True:
                try:
                    # Look up the rule for this endpoint
                    rule = None
                    for r in app.url_map.iter_rules():
                        if r.endpoint == endpoint:
                            rule = r.rule
                            break
                    if not rule:
                        print(f"[keep_alive] Endpoint '{endpoint}' not found")
                        return
                    
                    resp = client.get(rule)
                    print(f"[keep_alive] {endpoint} ({rule}) -> {resp.status_code}")
                except Exception as e:
                    print(f"[keep_alive] Error on {endpoint}: {e}")
                time.sleep(interval)

    t = threading.Thread(target=_ping, daemon=True)
    t.start()


def show_my_routes(app):
    """
    Prints all registered routes in the Flask app.
    """
    print("\n[show_my_routes] Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:20s} -> {rule.rule}")