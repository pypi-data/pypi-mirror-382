"""
Simplified ServerManager - only what's needed for tutorial
"""

import json
import os
import platform
import shutil
import subprocess  # nosec B404
import time
import socket
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
import psutil

from ._handle import ServerHandle
from ._config import get_config
from ._exceptions import (
    ServerNotFoundError,
    PortInUseError,
    ServerStartupError,
    ServerAlreadyExistsError,
)
from ._endpoint_serializer import generate_app_code_from_endpoints
from ._health import HealthChecker, HealthCheckConfig
from ._process_manager import ProcessManager


class ServerManager:
    """Simple manager for FastAPI server processes"""

    def __init__(self) -> None:
        self._config = get_config()
        self._servers: Dict[str, ServerHandle] = {}  # name -> ServerHandle
        self._health_checker = HealthChecker()
        # Don't load persistent servers on init - discover on demand instead
        
        # Create base directory for isolated server environments
        self._envs_dir = self._config.log_dir / "server_envs"
        self._envs_dir.mkdir(parents=True, exist_ok=True)
        

    def list_servers(self) -> List[ServerHandle]:
        """List all managed servers - always discovers from scratch"""
        # First discover all running syft-serve processes
        from ._process_discovery import discover_syft_serve_processes
        import requests
        
        discovered_servers = []
        
        # Discover all running servers
        processes = discover_syft_serve_processes()
        
        for proc_info in processes:
            if proc_info.get("verified", False):
                # Additional health check
                try:
                    # Check if process is actually healthy
                    proc = psutil.Process(proc_info["pid"])
                    status = proc.status()
                    
                    # Skip zombie or dead processes
                    if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                        continue
                        
                    # Try to verify it's responsive
                    if proc_info.get("url"):
                        response = requests.get(f"{proc_info['url']}/health", timeout=0.5)
                        if response.status_code != 200:
                            continue
                except:
                    # Skip unhealthy processes
                    continue
                port = proc_info["port"]
                pid = proc_info["pid"]
                
                # Try to get more info from the server
                try:
                    # Get server info
                    info_resp = requests.get(f"http://localhost:{port}/syft/info", timeout=0.5)
                    if info_resp.status_code == 200:
                        info = info_resp.json()
                        name = info.get("name", f"unknown_{port}")
                        endpoints = info.get("endpoints", ["/"])
                    else:
                        # Fallback name from cmdline
                        cmdline = proc_info["cmdline"]
                        # Extract app name from uvicorn command
                        import re
                        match = re.search(r'(\w+)_app:app', cmdline)
                        name = match.group(1) if match else f"server_{port}"
                        endpoints = ["/"]
                    
                    # Create ServerHandle
                    server = ServerHandle(
                        port=port,
                        pid=pid,
                        endpoints=endpoints,
                        name=name,
                        app_module=None
                    )
                    discovered_servers.append(server)
                    
                    # Update our registry with discovered server
                    self._servers[name] = server
                    
                except Exception:
                    # If we can't get info, still create a basic handle
                    name = f"server_{port}"
                    server = ServerHandle(
                        port=port,
                        pid=pid,
                        endpoints=["/"],
                        name=name,
                        app_module=None
                    )
                    discovered_servers.append(server)
                    self._servers[name] = server
        
        # Also check our persistence file for any additional info
        self._load_persistent_servers()
        
        # Merge with any servers we already know about
        for name, server in self._servers.items():
            if not any(s.name == name for s in discovered_servers):
                # Check if this server is still alive
                if server.status == "running":
                    discovered_servers.append(server)
        
        return discovered_servers

    def create_server(
        self,
        name: str,
        endpoints: Dict[str, Callable],
        dependencies: Optional[List[str]] = None,
        force: bool = False,
        expiration_seconds: int = 86400,
        verify_startup: bool = True,
        startup_timeout: float = 10.0,
        verbose: bool = False,
    ) -> ServerHandle:
        """
        Create a new server with a unique name

        Args:
            name: Unique server name (required)
            endpoints: Dictionary of endpoint paths to handler functions
            dependencies: Optional list of Python packages to install
            force: If True, destroy existing server with same name
            expiration_seconds: Server auto-expires after this many seconds (default: 86400 = 24 hours, -1 = never)
            verify_startup: Whether to verify server health after starting (default: True)
            startup_timeout: Maximum time to wait for server to be healthy (default: 10.0 seconds)

        Returns:
            ServerHandle for the created server
        """
        # Validate name
        if not name:
            raise ValueError("Server name is required")

        if not self._is_valid_name(name):
            raise ValueError(
                f"Invalid server name '{name}'. Names must contain only letters, "
                "numbers, underscores, and hyphens. No spaces or special characters."
            )

        # Check if name already exists
        if name in self._servers:
            if force:
                # Destroy existing server
                self.terminate_server(name)
            else:
                raise ServerAlreadyExistsError(
                    f"Server '{name}' already exists. Use force=True to replace."
                )

        # Find available port
        port = self._find_free_port()

        # Extract endpoint paths
        endpoint_paths = list(endpoints.keys())

        # Start the server process
        pid = self._start_server_from_endpoints(
            port, endpoints, name, dependencies, expiration_seconds
        )

        # Create server handle
        server = ServerHandle(
            port=port,
            pid=pid,
            endpoints=endpoint_paths,
            name=name,
            expiration_seconds=expiration_seconds,
        )

        # Verify startup if requested
        if verify_startup:
            health_config = HealthCheckConfig(startup_timeout=startup_timeout)
            self._health_checker.config = health_config
            
            health_result = self._health_checker.verify_startup(server, verbose=verbose)
            if not health_result.healthy:
                # Cleanup failed server
                try:
                    ProcessManager.kill_process_tree(pid)
                except:
                    pass
                raise ServerStartupError(
                    f"Server {name} failed health check: {health_result.details.get('error', 'Unknown error')}"
                )
        else:
            # Use old wait method for backward compatibility
            self._wait_for_server_ready(server)

        # Register server
        self._servers[name] = server
        self._save_persistent_servers()

        return server

    def get_server(self, name: str) -> ServerHandle:
        """Get server by name"""
        if name not in self._servers:
            available = list(self._servers.keys())
            if available:
                raise ServerNotFoundError(
                    f"No server found with name '{name}'. "
                    f"Available servers: {', '.join(available)}"
                )
            else:
                raise ServerNotFoundError("No servers are currently registered")
        return self._servers[name]

    def terminate_server(self, name: str, force: bool = True) -> None:
        """Terminate specific server by name

        Args:
            name: Server name
            force: If True, use force_terminate if normal termination fails (default: True)
        """
        server = self.get_server(name)

        try:
            # Try normal termination first
            server.terminate(timeout=5.0)
            
            # Verify it's dead
            time.sleep(0.5)
            if server.status == "running":
                if force:
                    # Silently use force terminate - don't print unless verbose
                    server.force_terminate()
                else:
                    raise Exception(f"Failed to terminate server {name}")
        except Exception as e:
            if force:
                # Silently try force terminate - no error messages
                try:
                    server.force_terminate()
                except:
                    # Silently fail
                    pass
            else:
                raise

        # Clean up environment
        server_dir = self._envs_dir / name
        if server_dir.exists():
            try:
                shutil.rmtree(server_dir)
            except:
                # Silently fail cleanup
                pass

        # Remove from registry
        del self._servers[name]
        self._save_persistent_servers()

    def terminate_all(self, force: bool = True) -> Dict[str, Any]:
        """Terminate all servers - both tracked and orphaned

        Args:
            force: If True, use force_terminate for stubborn processes

        Returns:
            dict: Summary of termination results with keys:
                - tracked_total: number of tracked servers
                - tracked_terminated: number of tracked servers successfully terminated
                - tracked_failed: list of server names that failed to terminate
                - orphaned_discovered: number of orphaned processes found
                - orphaned_terminated: number of orphaned processes terminated
                - orphaned_failed: list of PIDs that failed to terminate
                - success: bool indicating if all servers were terminated
        """
        results: Dict[str, Any] = {
            "tracked_total": 0,
            "tracked_terminated": 0,
            "tracked_failed": [],
            "orphaned_discovered": 0,
            "orphaned_terminated": 0,
            "orphaned_failed": [],
            "success": True,
        }

        # First terminate tracked servers
        names = list(self._servers.keys())
        results["tracked_total"] = len(names)

        for name in names:
            try:
                self.terminate_server(name, force=force)
                results["tracked_terminated"] += 1
            except Exception as e:
                # Silently fail - only show in verbose mode
                results["tracked_failed"].append(name)
                results["success"] = False

        # Then find and terminate any orphaned processes
        # Method 1: Use existing process discovery
        from ._process_discovery import terminate_all_syft_serve_processes
        
        orphan_result = terminate_all_syft_serve_processes(force=force)
        results["orphaned_discovered"] = orphan_result["discovered"]
        results["orphaned_terminated"] = orphan_result["terminated"]
        results["orphaned_failed"] = orphan_result["failed"]

        # # Method 2: Use ProcessManager to find ANY remaining uvicorn processes
        # print("🔍 Searching for any remaining uvicorn processes...")
        # remaining_processes = ProcessManager.find_uvicorn_processes()
        
        # for proc_info in remaining_processes:
        #     try:
        #         if ProcessManager.kill_process_tree(proc_info.pid, timeout=5.0):
        #             results["orphaned_terminated"] += 1
        #         else:
        #             results["orphaned_failed"].append(proc_info.pid)
        #     except:
        #         results["orphaned_failed"].append(proc_info.pid)
                
        # results["orphaned_discovered"] += len(remaining_processes)

        # # Method 3: Check our common port range for any listeners
        # for port in range(8000, 9000):
        #     port_processes = ProcessManager.find_processes_by_port(port)
        #     for proc_info in port_processes:
        #         if proc_info.pid not in results["orphaned_failed"]:
        #             try:
        #                 ProcessManager.kill_process_tree(proc_info.pid)
        #                 results["orphaned_terminated"] += 1
        #             except:
        #                 results["orphaned_failed"].append(proc_info.pid)

        if results["orphaned_failed"]:
            results["success"] = False
            # Don't print failure messages - keep them internal

        # Don't print summaries - keep termination quiet

        return results

    # Helper methods
    def _is_valid_name(self, name: str) -> bool:
        """Check if server name is valid"""
        # Only allow letters, numbers, underscores, and hyphens
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))

    def _find_free_port(self) -> int:
        """Find a free port within the configured range"""
        start_port, end_port = self._config.port_range

        for port in range(start_port, end_port + 1):
            if self._is_port_free(port):
                return port

        raise PortInUseError(f"No free ports in range {start_port}-{end_port}")

    def _is_port_free(self, port: int) -> bool:
        """Check if port is free"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("localhost", port))
                return True
        except OSError:
            return False

    def _create_server_environment(
        self, name: str, dependencies: Optional[List[str]] = None
    ) -> Path:
        """Create an isolated uv environment for a server"""
        server_dir = self._envs_dir / name
        server_dir.mkdir(parents=True, exist_ok=True)

        # Default dependencies
        default_deps = [
            "fastapi",
            "uvicorn[standard]",
            "httpx",  # for health checks
        ]

        # Separate local paths from pip packages
        pip_deps = []
        local_paths = []
        
        for dep in (dependencies or []):
            # Check if it's a path (absolute or relative)
            if (dep.startswith('/') or dep.startswith('./') or dep.startswith('../') or 
                ':' in dep and len(dep) > 1 and dep[1] == ':' or  # Windows path like C:
                Path(dep).exists()):
                local_paths.append(dep)
            else:
                pip_deps.append(dep)
        
        # Only include pip packages in dependencies, not local paths
        all_deps = default_deps + pip_deps

        # Create pyproject.toml
        pyproject_path = server_dir / "pyproject.toml"
        deps_str = ",\n    ".join(f'"{dep}"' for dep in all_deps)

        pyproject_content = f"""[project]
name = "{name}"
version = "0.1.0"
dependencies = [
    {deps_str}
]

[tool.uv]
package = false
"""
        pyproject_path.write_text(pyproject_content)

        # Create virtual environment
        result = subprocess.run(  # nosec B603 B607
            ["uv", "venv", "--python", "3.12"], cwd=str(server_dir), capture_output=True, text=True
        )

        if result.returncode != 0:
            raise ServerStartupError(f"Failed to create venv for {name}: {result.stderr}")

        # Install dependencies
        result = subprocess.run(  # nosec B603 B607
            ["uv", "sync"], cwd=str(server_dir), capture_output=True, text=True
        )

        if result.returncode != 0:
            raise ServerStartupError(f"Failed to install dependencies for {name}: {result.stderr}")

        # Store local paths in a file so the app can read them
        if local_paths:
            local_paths_file = server_dir / "local_paths.json"
            local_paths_file.write_text(json.dumps(local_paths))
        
        return server_dir

    def _start_server_from_endpoints(
        self,
        port: int,
        endpoints: Dict[str, Callable],
        name: str,
        dependencies: Optional[List[str]] = None,
        expiration_seconds: int = 86400,
    ) -> int:
        """Start server from endpoint dictionary"""
        # Generate app code directly from endpoints
        if shutil.which("uv"):
            server_dir = self._create_server_environment(name, dependencies)
            app_file = server_dir / f"{name}_app.py"
            stdout_log = server_dir / f"{name}_stdout.log"
            stderr_log = server_dir / f"{name}_stderr.log"
        else:
            app_dir = self._config.log_dir / "apps"
            app_dir.mkdir(exist_ok=True)
            app_file = app_dir / f"{name}_app.py"
            stdout_log = self._config.log_dir / f"{name}_stdout.log"
            stderr_log = self._config.log_dir / f"{name}_stderr.log"
            server_dir = None

        # Generate the app code
        app_code = generate_app_code_from_endpoints(endpoints, name, expiration_seconds)
        app_file.write_text(app_code)

        # Use uv run if available for better dependency management
        if shutil.which("uv") and server_dir:
            cmd = [
                "uv",
                "run",
                "uvicorn",
                f"{app_file.stem}:app",
                "--host",
                "127.0.0.1",  # Only bind to localhost for security
                "--port",
                str(port),
                "--log-level",
                "info",
            ]
        else:
            cmd = [
                "uvicorn",
                f"{app_file.stem}:app",
                "--host",
                "127.0.0.1",  # Only bind to localhost for security
                "--port",
                str(port),
                "--log-level",
                "info",
            ]

        try:
            # Set working directory if we created an environment
            cwd = str(server_dir) if server_dir else None

            with open(stdout_log, "w") as out, open(stderr_log, "w") as err:
                # Enhanced process independence - completely detach from parent
                kwargs = {
                    "stdout": out,
                    "stderr": err,
                    "text": True,
                    "cwd": cwd,
                    "start_new_session": True,  # Creates new process group
                    "close_fds": True,  # Close all parent file descriptors
                }
                
                # Unix-specific: ensure session leader (only if not already using start_new_session)
                # Note: start_new_session=True already handles session creation, so we don't need preexec_fn
                    
                # Windows-specific: create new process group
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
                    
                process = subprocess.Popen(cmd, **kwargs)  # nosec B603
            return process.pid
        except Exception as e:
            raise ServerStartupError(f"Failed to start server {name}: {e}")

    def _wait_for_server_ready(self, server: ServerHandle) -> None:
        """Wait for server to be ready to accept requests"""
        start_time = time.time()
        timeout = self._config.startup_timeout

        while time.time() - start_time < timeout:
            if server.health_check():
                return
            time.sleep(self._config.health_check_interval)

        raise ServerStartupError(f"Server {server.name} did not become ready within {timeout}s")

    def _load_persistent_servers(self) -> None:
        """Load server registry from persistence file"""
        if not self._config.persistence_file.exists():
            return

        try:
            with open(self._config.persistence_file, "r") as f:
                data = json.load(f)

            for server_data in data.get("servers", []):
                # Verify process still exists
                try:
                    psutil.Process(server_data["pid"])
                    server = ServerHandle(
                        port=server_data["port"],
                        pid=server_data["pid"],
                        endpoints=server_data["endpoints"],
                        name=server_data["name"],
                        app_module=server_data.get("app_module"),
                    )
                    self._servers[server.name] = server
                except psutil.NoSuchProcess:
                    # Process is dead, skip
                    pass

        except Exception as e:
            # Silently fail loading persistent servers
            pass

    def _save_persistent_servers(self) -> None:
        """Save server registry to persistence file atomically"""
        import tempfile
        
        try:
            data = {
                "servers": [
                    {
                        "name": server.name,
                        "port": server.port,
                        "pid": server.pid,
                        "endpoints": server.endpoints,
                        "app_module": server.app_module,
                    }
                    for server in self._servers.values()
                    if server.status == "running"
                ]
            }

            # Write to temp file first
            temp_fd, temp_path = tempfile.mkstemp(dir=self._config.persistence_file.parent, text=True)
            try:
                with open(temp_fd, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # Atomic rename
                Path(temp_path).replace(self._config.persistence_file)
            except:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise

        except Exception as e:
            # Silently fail saving persistent servers
            pass

    def _cleanup_dead_environments(self) -> None:
        """Clean up environments for dead servers"""
        import os
        
        if not self._envs_dir.exists():
            return
            
        for env_path in self._envs_dir.iterdir():
            if env_path.is_dir():
                pid_file = env_path / "server.pid"
                if pid_file.exists():
                    try:
                        pid = int(pid_file.read_text())
                        # Check if process exists
                        os.kill(pid, 0)
                    except (OSError, ValueError):
                        # Process doesn't exist, clean up
                        try:
                            shutil.rmtree(env_path)
                        except:
                            pass
