"""
Simplified ServerHandle - Individual server control and monitoring
"""

import time
from typing import List, Optional
import psutil
import requests

from ._config import get_config
from ._exceptions import ServerNotFoundError, ServerShutdownError


class ServerHandle:
    """Handle for controlling and monitoring an individual server"""

    def __init__(
        self,
        port: int,
        pid: int,
        endpoints: List[str],
        name: Optional[str] = None,
        app_module: Optional[str] = None,
        expiration_seconds: int = 86400,
    ):
        self.port = port
        self.pid = pid
        self.endpoints = endpoints
        self.name = name or f"server_{port}"
        self.app_module = app_module
        self.expiration_seconds = expiration_seconds
        self.created_at = time.time()
        self._process: Optional[psutil.Process] = None
        self._config = get_config()
        self.host = "localhost"  # Add host property for health checker

    @property
    def status(self) -> str:
        """Get current server status"""
        try:
            # Check if server has expired
            if self.is_expired():
                return "expired"

            if self._get_process().is_running():
                if self.health_check():
                    return "running"
                else:
                    return "unhealthy"
            else:
                return "stopped"
        except (psutil.NoSuchProcess, ServerNotFoundError):
            return "stopped"
        except Exception:
            return "error"

    def _get_process(self) -> psutil.Process:
        """Get or refresh the process object"""
        if self._process is None or not self._process.is_running():
            try:
                self._process = psutil.Process(self.pid)
            except psutil.NoSuchProcess:
                raise ServerNotFoundError(f"Server process {self.pid} not found")
        return self._process

    def health_check(self, timeout: float = 2.0) -> bool:
        """Check if server is responding to HTTP requests"""
        try:
            response = requests.get(f"http://localhost:{self.port}/health", timeout=timeout)
            return bool(response.status_code == 200)
        except requests.RequestException:
            return False

    def is_expired(self) -> bool:
        """Check if server has expired based on creation time and expiration_seconds"""
        if self.expiration_seconds == -1:  # Never expires
            return False

        current_time = time.time()
        elapsed_seconds = current_time - self.created_at
        return elapsed_seconds > self.expiration_seconds

    def check_and_self_destruct(self) -> bool:
        """Check if expired and self-destruct if so. Returns True if destroyed."""
        if self.is_expired():
            try:
                self.terminate()
                return True
            except Exception:
                # If termination fails, still consider it destroyed
                return True
        return False

    def terminate(self, timeout: float = 5.0) -> None:
        """Terminate the server process and entire process group

        Args:
            timeout: Maximum time to wait for graceful shutdown (default: 5.0 seconds)
        """
        import signal
        import os

        try:
            process = self._get_process()

            # Since we use start_new_session=True, kill the entire process group
            # The process group ID is the same as the process ID for session leaders
            pgid = process.pid

            if hasattr(os, "killpg"):
                # Unix-like systems - use process groups
                try:
                    # Send SIGTERM to entire process group
                    os.killpg(pgid, signal.SIGTERM)

                    # Wait for graceful shutdown with timeout
                    start_time = time.time()
                    while process.is_running() and (time.time() - start_time) < timeout:
                        time.sleep(0.1)

                    # Check if main process is still alive
                    if process.is_running():
                        # Force kill the entire process group
                        if hasattr(signal, "SIGKILL"):
                            os.killpg(pgid, signal.SIGKILL)
                        else:
                            # Windows doesn't have SIGKILL
                            self._terminate_process_tree(process)

                        # Wait a bit more for SIGKILL to take effect
                        kill_timeout = 2.0
                        start_time = time.time()
                        while process.is_running() and (time.time() - start_time) < kill_timeout:
                            time.sleep(0.1)

                        # Final check - if still running, try fallback method
                        if process.is_running():
                            self._terminate_process_tree(process)

                            # One last check after fallback
                            time.sleep(0.5)
                            if process.is_running():
                                raise ServerShutdownError(
                                    f"Failed to kill server process group {pgid} after {timeout + kill_timeout}s"
                                )
                except ProcessLookupError:
                    # Process group already dead
                    pass
                except PermissionError:
                    # Fall back to killing individual processes
                    self._terminate_process_tree(process)
            else:
                # Windows - terminate process tree directly
                self._terminate_process_tree(process)

        except psutil.NoSuchProcess:
            # Process already dead
            pass

    def _terminate_process_tree(self, process: psutil.Process) -> None:
        """Fallback method to terminate process and all children"""
        try:
            # Get all child processes first
            children = process.children(recursive=True)

            # Kill all children
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass

            # Kill parent
            process.kill()

            # Wait briefly
            gone, alive = psutil.wait_procs([process] + children, timeout=1.0)

            if alive:
                # Log which processes couldn't be killed
                alive_pids = [p.pid for p in alive]
                raise ServerShutdownError(f"Failed to kill processes: {alive_pids}")
        except psutil.NoSuchProcess:
            pass

    def force_terminate(self) -> None:
        """Nuclear option - forcefully kill the process using OS commands

        This method uses platform-specific OS commands to ensure process termination.
        Use only when terminate() fails.
        """
        import subprocess  # nosec B404
        import platform
        import signal
        import os

        try:
            process = self._get_process()
            pid = process.pid

            if platform.system() == "Windows":
                # Windows: Use taskkill with force flag
                subprocess.run(  # nosec B603 B607
                    ["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, check=False
                )
            else:
                # Unix-like systems: Use kill -9 on process group
                if hasattr(os, "killpg") and hasattr(signal, "SIGKILL"):
                    try:
                        # First try to kill the entire process group
                        os.killpg(pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        # Fallback to killing just the process
                        subprocess.run(  # nosec B603 B607
                            ["kill", "-9", str(pid)], capture_output=True, check=False
                        )
                else:
                    # Fallback for systems without killpg
                    subprocess.run(  # nosec B603 B607
                        ["kill", "-9", str(pid)], capture_output=True, check=False
                    )

                # Also try to kill all children explicitly
                try:
                    children = process.children(recursive=True)
                    child_pids = [str(child.pid) for child in children]
                    if child_pids:
                        subprocess.run(  # nosec B603
                            ["kill", "-9"] + child_pids, capture_output=True, check=False
                        )
                except psutil.NoSuchProcess:
                    pass

            # Give it a moment to die
            time.sleep(0.5)

            # Final verification - if still running, it's likely a zombie or system issue
            try:
                if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                    raise ServerShutdownError(
                        f"Process {pid} survived force termination - may require manual intervention"
                    )
            except psutil.NoSuchProcess:
                # Good, it's dead
                pass

        except psutil.NoSuchProcess:
            # Already dead, that's fine
            pass
