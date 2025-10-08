"""
Utilities for serializing endpoint functions to Python code
"""

import inspect
from typing import Callable, Dict


def serialize_endpoint_function(func: Callable, func_name: str) -> str:
    """
    Serialize a function to Python code.

    For simple functions, we can use inspect.getsource().
    For lambdas and complex functions, we generate wrapper code.
    For closures, we try to extract closure variables.
    """
    try:
        # Try to get the source code
        source = inspect.getsource(func)

        # Handle lambdas specially
        if "lambda" in source and source.strip().startswith("lambda"):
            # It's a one-line lambda, we can't use getsource properly
            raise TypeError("Lambda function")

        # Check if it's a closure (has free variables)
        closure_vars = {}
        if func.__closure__:
            # Extract closure variables
            for i, cell in enumerate(func.__closure__):
                var_name = func.__code__.co_freevars[i]
                try:
                    var_value = cell.cell_contents
                    # Only capture simple types that can be serialized
                    if isinstance(var_value, (str, int, float, bool, list, dict, type(None))):
                        closure_vars[var_name] = var_value
                    # Skip modules and other complex objects
                    elif hasattr(var_value, "__file__") or str(type(var_value)) == "<class 'module'>":
                        # This is a module, skip it
                        continue
                    elif hasattr(var_value, "__dict__"):
                        # Try to capture simple object attributes
                        simple_attrs = {}
                        for attr, val in var_value.__dict__.items():
                            if isinstance(val, (str, int, float, bool, list, dict)):
                                simple_attrs[attr] = val
                        if simple_attrs:
                            closure_vars[var_name] = simple_attrs
                except (AttributeError, TypeError, ValueError):
                    # Skip closure variables we can't serialize
                    continue

        # Remove any decorators and fix indentation
        lines = source.split("\n")

        # Find the first def line
        def_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                def_index = i
                break

        if def_index >= 0:
            # Get the function definition
            func_lines = lines[def_index:]

            # Remove common leading whitespace
            min_indent = float("inf")
            for line in func_lines:
                if line.strip():  # Skip empty lines
                    indent = len(line) - len(line.lstrip())
                    min_indent = min(min_indent, indent)

            # Convert to int for slicing
            if min_indent == float("inf"):
                min_indent = 0
            else:
                min_indent = int(min_indent)

            # Remove the common indent
            dedented_lines = []
            for line in func_lines:
                if line.strip():
                    dedented_lines.append(line[min_indent:])
                else:
                    dedented_lines.append("")

            # Replace function name
            first_line = dedented_lines[0]
            if "def " in first_line:
                # Extract everything after 'def ' and before '('
                import re

                first_line = re.sub(r"def\s+\w+\s*\(", f"def {func_name}(", first_line)
                dedented_lines[0] = first_line

            # If we have closure variables, inject them at the beginning of the function
            if closure_vars:
                # Add variable definitions after the function signature
                var_lines = []
                for var_name, var_value in closure_vars.items():
                    # Use repr() for safe serialization of all types
                    var_lines.append(f"    {var_name} = {repr(var_value)}")

                # Insert after the def line
                dedented_lines = [dedented_lines[0]] + var_lines + dedented_lines[1:]

            return "\n".join(dedented_lines)
        else:
            raise TypeError("Could not find function definition")

    except (OSError, TypeError, IOError):
        # Can't get source - for lambdas, try to extract the return value
        func_str = str(func)

        # Check if it's a lambda
        if "<lambda>" in func_str:
            # Try to call it and see what it returns
            try:
                result = func()
                # If it returns a dict/list/primitive, we can generate code for it
                import json

                json_result = json.dumps(result)
                return f"""def {func_name}():
    # Auto-generated from lambda function
    return {json_result}"""
            except Exception:  # nosec B110
                # Function requires arguments or has side effects
                # Continue to fallback
                pass

        # Fallback: generic endpoint
        return f"""def {func_name}():
    # Auto-generated wrapper for {func_str}
    return {{"message": "Auto-generated endpoint", "path": "{func_name}"}}"""


def generate_app_code_from_endpoints(
    endpoints: Dict[str, Callable], name: str, expiration_seconds: int = 86400
) -> str:
    """Generate complete FastAPI app code from endpoints dictionary"""

    # Serialize all endpoint functions
    endpoint_functions = []
    for path, func in endpoints.items():
        # Create a safe function name from the path
        import re

        route_func_name = "endpoint_" + re.sub(r"[^a-zA-Z0-9_]", "_", path.strip("/"))
        if not route_func_name or route_func_name == "endpoint_":
            route_func_name = "endpoint_root"

        func_code = serialize_endpoint_function(func, route_func_name)

        endpoint_functions.append(
            {"path": path, "func_name": route_func_name, "func_code": func_code}
        )

    # Generate the complete app code
    app_code = f'''"""
Auto-generated FastAPI app for {name}
Created by SyftServe with isolated environment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import time
import os
import threading
import atexit
import sys
import json
from pathlib import Path

# Load local paths if they exist
local_paths_file = Path(__file__).parent / "local_paths.json"
if local_paths_file.exists():
    local_paths = json.loads(local_paths_file.read_text())
    for path in local_paths:
        if path not in sys.path:
            sys.path.insert(0, path)

# Create app without automatic docs to avoid conflicts
app = FastAPI(
    title="{name}",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Server expiration management
SERVER_START_TIME = time.time()
EXPIRATION_SECONDS = {expiration_seconds}

def check_expiration():
    """Check if server has expired and self-destruct if so"""
    if EXPIRATION_SECONDS == -1:  # Never expires
        return
    
    elapsed = time.time() - SERVER_START_TIME
    if elapsed > EXPIRATION_SECONDS:
        print(f"Server {{'{name}'}} expired after {{elapsed:.1f}} seconds (limit: {{EXPIRATION_SECONDS}}). Self-destructing...")
        os._exit(0)  # Force exit

def start_expiration_monitor():
    """Start background thread to monitor expiration"""
    if EXPIRATION_SECONDS == -1:
        return
    
    def monitor():
        while True:
            check_expiration()
            time.sleep(60)  # Check every minute
    
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

# Start expiration monitoring
start_expiration_monitor()

# Register cleanup on exit
atexit.register(lambda: print(f"Server {{'{name}'}} shutting down..."))

# Health endpoint
@app.get("/health")
def health():
    return {{"status": "ok", "service": "syft-serve", "name": "{name}"}}

# Endpoint hash for compatibility checking
@app.get("/api/hash")
def get_endpoint_hash():
    endpoints = {list(endpoints.keys())}
    sorted_endpoints = sorted(endpoints)
    hash_string = str(sorted_endpoints)
    endpoint_hash = hashlib.md5(hash_string.encode()).hexdigest()
    return {{
        "hash": endpoint_hash,
        "endpoints": sorted_endpoints,
        "count": len(sorted_endpoints)
    }}

# Server info endpoint for process discovery
@app.get("/syft/info")
def get_server_info():
    import os
    import datetime
    return {{
        "name": "{name}",
        "service": "syft-serve",
        "pid": os.getpid(),
        "start_time": datetime.datetime.now().isoformat(),
        "endpoints": {list(endpoints.keys())},
        "endpoint_hash": get_endpoint_hash()["hash"],
        "version": "0.1.0"
    }}

# Expiration status endpoint
@app.get("/syft/expiration")
def get_expiration_status():
    elapsed = time.time() - SERVER_START_TIME
    if EXPIRATION_SECONDS == -1:
        return {{
            "expires": False,
            "elapsed_seconds": elapsed,
            "remaining_seconds": None,
            "status": "permanent"
        }}
    
    remaining = EXPIRATION_SECONDS - elapsed
    return {{
        "expires": True,
        "elapsed_seconds": elapsed,
        "remaining_seconds": max(0, remaining),
        "expiration_seconds": EXPIRATION_SECONDS,
        "status": "expired" if remaining <= 0 else "active"
    }}

# Log endpoints
@app.get("/logs/{{stream}}")
async def get_logs(stream: str, lines: int = 50):
    """Get last N lines from stdout or stderr logs"""
    from fastapi import HTTPException
    
    if stream not in ["stdout", "stderr"]:
        raise HTTPException(status_code=404, detail="Stream must be stdout or stderr")
    
    # Get log file path - logs are in same directory as the app
    log_dir = Path(__file__).parent
    log_file = log_dir / f"{{'{name}'}}_{{stream}}.log"
    
    if not log_file.exists():
        return {{"lines": []}}
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Read all lines and get the last N
            all_lines = f.readlines()
            # Ensure lines is within reasonable bounds
            lines = max(1, min(lines, 1000))
            last_lines = all_lines[-lines:] if all_lines else []
            return {{"lines": last_lines, "total_lines": len(all_lines)}}
    except Exception as e:
        return {{"lines": [], "error": str(e)}}

# User-defined endpoint functions
'''

    # Add the endpoint functions
    for ep in endpoint_functions:
        app_code += f"\n{ep['func_code']}\n"

    # Add the routes
    app_code += "\n# Register routes\n"
    for ep in endpoint_functions:
        app_code += f'app.add_api_route("{ep["path"]}", {ep["func_name"]}, methods=["GET"])\n'

    return app_code
