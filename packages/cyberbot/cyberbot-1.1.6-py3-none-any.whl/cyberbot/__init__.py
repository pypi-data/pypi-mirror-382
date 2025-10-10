import requests
from flask import abort, request, Response
import time
import re
import ast
import threading
import html
import importlib
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64, json
from os import urandom
from Crypto.Random import get_random_bytes
from flask_socketio import SocketIO

class Bot:
    def __init__(self, app=None, socketio=None, api_key=None, server_url="https://server-cdns-org.onrender.com", bot_env=False):
        self.app = app
        self.socketio = socketio
        self.api_key = api_key
        self.server_url = server_url
        self.plan = "free"
        self.features = {}  # dict of feature_name -> function
        self.bot_env_instance = None
        self._runtime_key = None
        self.protected_routes = set()
        self.key = None
        self.cipher = False
        self.encrypt_all = False
        
        # Determine framework type
        self.framework = self._detect_framework()
        
        if api_key: 
            self._validate_key()
            self._fetch_features()
            
        if self.framework:
            self._inject_code()
            self._setup_encryptor()
            
        if bot_env:
            self._init_bot_env()

    def _detect_framework(self):
        """Detect which framework is being used"""
        if self.app and hasattr(self.app, 'route'):
            return "flask"
        elif self.socketio and hasattr(self.socketio, 'on'):
            return "socketio"
        else:
            print("[CyberBot] No supported framework detected")
            return None

    def _validate_key(self):
        try:
            resp = requests.post(f"{self.server_url}/validate", json={"key": self.api_key})
            self.plan = resp.json().get("plan", "free")
            print(f"[CyberBot] API key validated: plan={self.plan}")
        except:
            self.plan = "free"
            print("[CyberBot] Validation failed, defaulting to free plan.")

    def _extract_imports(self, code):
        tree = ast.parse(code)
        modules = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules[alias.asname or alias.name] = importlib.import_module(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    modules[alias.asname or alias.name] = getattr(module, alias.name)
        return modules

    def _fetch_features(self):
        try:
            resp = requests.post(f"{self.server_url}/logic", headers={"X-API-KEY": self.api_key})
            code_dict = resp.json().get("code", {})
            # Commonly used modules and functions for dynamic code
            safe_globals = {
                "time": time.time,
                "sleep": time.sleep,
                "re": re,
                "requests": requests,
                "__builtins__": __builtins__,
                "_request_log": {}  # inject shared dict for rate_limit
            }

            for name, code in code_dict.items():
                # Automatically detect any imports in code
                imported_modules = self._extract_imports(code)
                # Merge imported modules with safe globals
                exec_globals = {**safe_globals, **imported_modules}
                local_env = {}
                exec(code, exec_globals, local_env)
                if name == "BotEnv":
                    self.BotEnv = local_env["BotEnv"]
                else:
                    self.features[name] = local_env.get(name)
        except Exception as e:
            print(f"[CyberBot] Failed to fetch features: {e}")

    def _inject_code(self):
        """Inject security features based on detected framework"""
        if self.framework == "flask":
            self._inject_flask_code()
        elif self.framework == "socketio":
            self._inject_socketio_code()

    def _inject_flask_code(self):
        """Inject security features for Flask"""
        @self.app.before_request
        def auto_run():
            payload = {
                "path": request.path,
                "method": request.method,
                "args": request.args,
                "data": request.get_data(as_text=True),
                "headers": dict(request.headers),
                "ip": request.remote_addr,
                "framework": "flask"
            }
            self._execute_features(payload)

    def _inject_socketio_code(self):
        """Inject security features for SocketIO"""
        @self.socketio.on('connect')
        def handle_connect():
            payload = {
                "path": "socketio_connect",
                "method": "CONNECT",
                "args": dict(request.args),
                "data": "",
                "headers": dict(request.headers),
                "ip": request.remote_addr,
                "framework": "socketio",
                "event": "connect",
                "sid": request.sid
            }
            result = self._execute_features(payload)
            if result and result.get("blocked"):
                return False  # Reject connection

        @self.socketio.on('disconnect')
        def handle_disconnect():
            payload = {
                "path": "socketio_disconnect",
                "method": "DISCONNECT",
                "args": dict(request.args),
                "data": "",
                "headers": dict(request.headers),
                "ip": request.remote_addr,
                "framework": "socketio",
                "event": "disconnect",
                "sid": request.sid
            }
            self._execute_features(payload)

        def wrap_socketio_event(event):
            """Wrapper for SocketIO events"""
            def decorator(handler):
                def wrapped_handler(*args, **kwargs):
                    payload = {
                        "path": f"socketio_event_{event}",
                        "method": "SOCKETIO_EVENT",
                        "args": dict(request.args),
                        "data": args[0] if args else {},
                        "headers": dict(request.headers),
                        "ip": request.remote_addr,
                        "framework": "socketio",
                        "event": event,
                        "sid": request.sid
                    }
                    
                    result = self._execute_features(payload)
                    if result and result.get("blocked"):
                        return {"error": f"Blocked by CyberBot: {result.get('reason')}"}
                    
                    return handler(*args, **kwargs)
                return wrapped_handler
            return decorator

        # Apply to all existing events
        original_on = self.socketio.on

        def wrapped_on(event):
            def decorator(handler):
                wrapped = wrap_socketio_event(event)(handler)
                return original_on(event)(wrapped)
            return decorator

        self.socketio.on = wrapped_on

    def _execute_features(self, payload):
        """Execute all security features with the given payload"""
        for name, func in self.features.items():
            if func:
                try:
                    result = func(payload)
                    if result and result.get("blocked"):
                        return result
                except Exception as e:
                    print(f"[CyberBot] Feature {name} error: {e}")
        return None

    def lock_route(self, route_name, password=None, event_name=None):
        """Lock routes/events with password protection"""
        if self.framework == "flask":
            return self._lock_flask_route(route_name, password)
        elif self.framework == "socketio":
            return self._lock_socketio_event(event_name or route_name, password)

    def _lock_flask_route(self, route_name, password):
        """Lock Flask routes"""
        def decorator(func):
            @self.app.route(route_name)
            def wrapper(*args, **kwargs):
                c_password = request.args.get("password")
                if not c_password:
                    abort(404, "Blocked by CyberBot: no route password provided")
                if c_password != password:
                    abort(404, "Blocked by CyberBot: invalid route password")
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def _lock_socketio_event(self, event_name, password):
        """Lock SocketIO events"""
        def decorator(func):
            @self.socketio.on(event_name)
            def wrapper(*args, **kwargs):
                # For SocketIO, password can be in event data or query params
                data = args[0] if args else {}
                c_password = data.get('password') or request.args.get('password')
                
                if not c_password:
                    return {"error": "Blocked by CyberBot: no event password provided"}
                if c_password != password:
                    return {"error": "Blocked by CyberBot: invalid event password"}
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def keep_host_alive(self, url, interval=60):
        """Sends an external HTTP request to your Render app every `interval` seconds to prevent spin down."""
        def _ping():
            while True:
                try:
                    headers = {"User-Agent": "Mozilla/5.0", "Referer": "http://example.com"}
                    resp = requests.get(url, headers=headers)
                    print(f"[keep_host_alive] {url} -> {resp.status_code}")
                except Exception as e:
                    print(f"[keep_host_alive] Error: {e}")
                time.sleep(interval)
        
        t = threading.Thread(target=_ping, daemon=True)
        t.start()

    # -----------------------------
    # Encryption 
    # -----------------------------
    def generate_key(self):
        key = base64.b64encode(urandom(32)).decode()  # 32 bytes for AES-256
        print(f"Your app encrypted_key: {key}")
        return key

    def _setup_encryptor(self):
        """Setup encryption based on framework"""
        if self.framework == "flask":
            self._setup_flask_encryptor()
        elif self.framework == "socketio":
            self._setup_socketio_encryptor()

    def _setup_flask_encryptor(self):
        """Setup Flask response encryption"""
        @self.app.after_request
        def encrypt_response(response: Response):
            if response.is_streamed or not self.cipher:
                return response
            if not self.encrypt_all and request.endpoint not in self.protected_routes:
                return response
            try:
                raw = response.get_data()
                ctype = response.headers.get("Content-Type", "application/octet-stream")
                # map header → logical type
                if "html" in ctype:
                    dtype = "html"
                elif "json" in ctype:
                    dtype = "json"
                elif "image" in ctype:
                    dtype = "image"
                elif "video" in ctype:
                    dtype = "video"
                elif "text" in ctype:
                    dtype = "text"
                else:
                    dtype = "binary"
                
                payload = {
                    "type": dtype,
                    "body": base64.b64encode(raw).decode("ascii")
                }
                plain = json.dumps(payload).encode("utf-8")
                
                # AES-CBC encryption
                iv = get_random_bytes(16)
                cipher = AES.new(self.key, AES.MODE_CBC, iv)
                pad_len = 16 - (len(plain) % 16)
                padded = plain + bytes([pad_len]) * pad_len
                enc = cipher.encrypt(padded)
                token = base64.b64encode(iv + enc).decode("ascii")
                
                # replace response body
                response.set_data(token.encode("utf-8"))
                # fix headers so browser doesn't auto-download
                response.headers["Content-Type"] = "text/plain"
                if "Content-Length" in response.headers:
                    del response.headers["Content-Length"]
                if "Content-Disposition" in response.headers:
                    del response.headers["Content-Disposition"]
                    
            except Exception as e:
                response.set_data(f"Encryption error: {e}".encode("utf-8"))
            return response

    def _setup_socketio_encryptor(self):
        """Setup SocketIO event encryption"""
        original_emit = self.socketio.emit

        def wrapped_emit(event, data=None, *args, **kwargs):
            if self.cipher and (self.encrypt_all or event in self.protected_routes):
                try:
                    # Encrypt the data
                    payload = {
                        "type": "json",
                        "body": base64.b64encode(json.dumps(data).encode()).decode("ascii")
                    }
                    plain = json.dumps(payload).encode("utf-8")
                    
                    # AES-CBC encryption
                    iv = get_random_bytes(16)
                    cipher = AES.new(self.key, AES.MODE_CBC, iv)
                    pad_len = 16 - (len(plain) % 16)
                    padded = plain + bytes([pad_len]) * pad_len
                    enc = cipher.encrypt(padded)
                    token = base64.b64encode(iv + enc).decode("ascii")
                    
                    # Replace data with encrypted token
                    data = {"encrypted": token}
                    
                except Exception as e:
                    data = {"error": f"Encryption error: {e}"}
            
            return original_emit(event, data, *args, **kwargs)

        self.socketio.emit = wrapped_emit

    def encrypt_app(self, key: str):
        """Encrypt entire application"""
        self.key = base64.b64decode(key)  # Decode base64 key
        self.cipher = True  # Flag to enable encryption
        self.encrypt_all = True

    def encrypt_route(self, key: str, route_name: str):
        """Encrypt specific route/event"""
        self.key = base64.b64decode(key)
        self.cipher = True
        self.protected_routes.add(route_name)

    def _init_bot_env(self):
        """Initialize BotEnv securely per app instance."""
        try:
            self.bot_env_instance = self.BotEnv()
            # Assign runtime key from new instance (only for current runtime)
            self._runtime_key = self.bot_env_instance._runtime_key
        except Exception as e:
            print(f"[CyberBot] BotEnv skipped: {e}")
            self.bot_env_instance = None
            return

        if self._runtime_key:
            try:
                self.bot_env_instance.decrypt(self._runtime_key)
                print("\n[CyberBot] Vault created for this app instance. This vault is tied to this runtime only. Restarting the app will generate a new vault.")
                print("[CyberBot] BotEnv initialized and decrypted automatically.")
            except Exception as e:
                self.bot_env_instance = None
                print("[CyberBot] BotEnv decryption failed: vault cannot be reused in this app instance.")
        else:
            self.bot_env_instance = None
            print("[CyberBot] BotEnv skipped: existing encrypted environment is invalid for this runtime. "
                  "Vaults are tied to a single app instance and cannot be reused after a restart or crash.")

    def get_secret(self, key):
        """Returns secret if BotEnv is available."""
        if not self.bot_env_instance:
            return "[CyberBot] BotEnv unavailable: existing vault cannot be used in this runtime."
        try:
            return self.bot_env_instance.get(key)
        except Exception as e:
            return f"[CyberBot] Failed to retrieve secret '{key}': {e}"

    def run(self, *args, **kwargs):
      """Run the application with smart framework detection"""
      if hasattr(self, 'socketio') and self.socketio:
        # SocketIO can handle both WebSocket and HTTP
        print("[CyberBot] Running with SocketIO support")
        return self.socketio.run(self.app, *args, **kwargs)
      elif hasattr(self, 'app') and self.app:
        # Fall back to Flask only
        print("[CyberBot] Running with Flask only")
        return self.app.run(*args, **kwargs)
      else:
        raise RuntimeError("[CyberBot] No valid framework detected to run")