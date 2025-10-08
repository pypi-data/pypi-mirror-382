import asyncio
import subprocess
import os
import sys
import tempfile
import tarfile
from pathlib import Path
from typing import TYPE_CHECKING

from .prime_intellect import PrimeIntellectService, PodResponse

if TYPE_CHECKING:
    from ..execution.executor import NextZmqExecutor

class PodKernelManager:
    """
    Manages remote GPU pod connections (currently PI as provider, hope to provide other providers in the future)
    and SSH tunnels for ZMQ execution
    """
    pi_service: PrimeIntellectService
    pod: PodResponse | None
    ssh_tunnel_proc: subprocess.Popen[bytes] | None
    local_cmd_port: int
    local_pub_port: int
    remote_cmd_port : int
    remote_pub_port: int
    executor: "NextZmqExecutor | None"
    _ssh_key_cache: str | None

    def __init__(
        self,
        pi_service: PrimeIntellectService,
        local_cmd_port: int = 15555,
        local_pub_port: int = 15556,
        remote_cmd_port: int = 5555,
        remote_pub_port: int = 5556
    ) -> None:
        """
        Initialize pod manager

        args:
            pi_service : Prime Intellect API service
            local_cmd_port: Local port for REQ/REP tunnel
            local_pub_port: Local port for PUB/SUB tunnel
            remote_cmd_port: Remote port for REQ/REP socket
            remote_pub_port: Remote port for PUB/SUB socket
        """
        self.pi_service = pi_service
        self.pod = None
        self.ssh_tunnel_proc = None
        self.local_cmd_port = local_cmd_port
        self.local_pub_port = local_pub_port
        self.remote_cmd_port = remote_cmd_port
        self.remote_pub_port = remote_pub_port
        self.executor = None
        self._ssh_key_cache = None

    def _get_ssh_key(self) -> str | None:
        """
        Get SSH key path, checking environment variable and common locations.
        Returns None if no key is found.
        """
        if self._ssh_key_cache is not None:
            return self._ssh_key_cache

        # Check environment variable first
        ssh_key = os.getenv("MORECOMPUTE_SSH_KEY")
        if ssh_key:
            expanded = os.path.expanduser(ssh_key)
            if os.path.exists(expanded):
                self._ssh_key_cache = expanded
                return expanded

        # Try common SSH key paths (including Prime Intellect's recommended name)
        common_keys = [
            "~/.ssh/primeintellect_ed25519",  # Prime Intellect's recommended name
            "~/.ssh/id_ed25519",
            "~/.ssh/id_rsa",
        ]
        for key_path in common_keys:
            expanded_path = os.path.expanduser(key_path)
            if os.path.exists(expanded_path):
                self._ssh_key_cache = expanded_path
                return expanded_path

        return None

    async def connect_to_pod(self, pod_id:str) -> dict[str, object]:
        """
        Connects to existing pod and set up ssh tunnel
        args:
            pod_id: the pod identifier

        Response:
            dict with connection status
        """
        import sys

        self.pod = await self.pi_service.get_pod(pod_id)

        print(f"[POD MANAGER] Pod status: {self.pod.status}", file=sys.stderr, flush=True)
        print(f"[POD MANAGER] SSH connection: {self.pod.sshConnection}", file=sys.stderr, flush=True)

        if not self.pod.sshConnection:
            return{
                "status":"error",
                "message": f"Pod is not ready yet. Status: {self.pod.status}. SSH connection info is not available. Please wait for pod to finish provisioning."
            }

        # Validate SSH connection string is not empty/whitespace
        if not self.pod.sshConnection.strip():
            return{
                "status":"error",
                "message": f"Pod SSH connection is empty. Status: {self.pod.status}"
            }

        # Parse SSH connection string
        # Format can be: "ssh root@ip -p port" OR "root@ip -p port"
        ssh_parts = self.pod.sshConnection.split()

        # Find the part containing @ (user@host)
        host_part = None
        for part in ssh_parts:
            if "@" in part:
                host_part = part
                break

        if not host_part:
            return{
                "status":"error",
                "message": f"Invalid SSH connection format (no user@host found): {self.pod.sshConnection}"
            }

        # Extract host from user@host
        ssh_host = host_part.split("@")[1]
        ssh_port = "22"

        # Extract port if specified with -p flag
        if "-p" in ssh_parts:
            port_idx = ssh_parts.index("-p")
            if port_idx + 1 < len(ssh_parts):
                ssh_port = ssh_parts[port_idx + 1]

        print(f"[POD MANAGER] Parsed SSH host: {ssh_host}, port: {ssh_port}", file=sys.stderr, flush=True)

        #deploy worker code to pod
        deploy_result = await self._deploy_worker(ssh_host, ssh_port)
        if deploy_result.get("status") ==  "error":
            return deploy_result

        #create ssh tunnel for ZMQ ports
        tunnel_result = await self._create_ssh_tunnel(ssh_host, ssh_port)
        if tunnel_result.get("status") ==  "error":
            return tunnel_result

        #start remote worker
        worker_result = await self._start_remote_worker(ssh_host, ssh_port)
        if worker_result.get("status") ==  "error":
            await self.disconnect()
            return worker_result

        return {
            "status": "ok",
            "message": f"Connected to pod {pod_id}",
            "ssh_host": ssh_host,
            "ssh_port": ssh_port,
            "tunnel_ports": {
                "cmd": f"localhost:{self.local_cmd_port}",
                "pub": f"localhost:{self.local_pub_port}"
            }
        }

    async def _deploy_worker(self, ssh_host: str, ssh_port: str) -> dict[str,object]:
        """
        Deploy worker code to remote pod via Secure Copy Protocol.

        args:
            ssh_host: SSH host address
            ssh_port: SSH port

        returns:
            dict with deployment status
        """
        try:
            # Create temporary tarball of morecompute package
            project_root = Path(__file__).parent.parent.parent
            morecompute_dir = project_root / "morecompute"

            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                tmp_path = tmp.name

            with tarfile.open(tmp_path, 'w:gz') as tar:
                tar.add(morecompute_dir, arcname='morecompute')

            # Build SSH command with optional key override
            scp_cmd = ["scp", "-P", ssh_port]

            ssh_key = self._get_ssh_key()
            if ssh_key:
                scp_cmd.extend(["-i", ssh_key])

            scp_cmd.extend([
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "BatchMode=yes",  # Prevent password prompts, fail fast if key auth doesn't work
                "-o", "ConnectTimeout=10",
                tmp_path,
                f"root@{ssh_host}:/tmp/morecompute.tar.gz"
            ])

            result = subprocess.run(
                scp_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                error_msg = result.stderr.lower()
                if "permission denied" in error_msg or "publickey" in error_msg:
                    return {
                        "status": "error",
                        "message": (
                            "SSH authentication failed. Please add your SSH public key to Prime Intellect:\n"
                            "1. Visit https://app.primeintellect.ai/dashboard/tokens\n"
                            "2. Upload your public key (~/.ssh/id_ed25519.pub or ~/.ssh/id_rsa.pub)\n"
                            "3. Try connecting again"
                        )
                    }
                elif "host key verification failed" in error_msg:
                    return {
                        "status": "error",
                        "message": f"SSH host verification failed. This is unusual. Error: {result.stderr}"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Failed to copy worker code to pod. SSH Error: {result.stderr}"
                    }

            # Extract on remote and install dependencies
            ssh_cmd = ["ssh", "-p", ssh_port]

            if ssh_key:
                ssh_cmd.extend(["-i", ssh_key])

            ssh_cmd.extend([
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=10",
                f"root@{ssh_host}",
                (
                    "cd /tmp && "
                    "tar -xzf morecompute.tar.gz && "
                    "pip install --quiet pyzmq && "
                    "echo 'Deployment complete'"
                )
            ])

            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Cleanup local tarball
            os.unlink(tmp_path)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Failed to extract/setup worker: {result.stderr}"
                }

            return {"status": "ok", "message": "Worker deployed successfully"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"Deployment error: {str(e)}"
            }

    async def _create_ssh_tunnel(self, ssh_host: str, ssh_port: str) -> dict[str, object]:
        """
        Create SSH tunnel for ZMQ ports.

        args:
            ssh_host: SSH host address
            ssh_port: SSH port

        returns:
            dict with tunnel status
        """
        try:
            # Create SSH tunnel: local ports -> remote ports
            ssh_key = self._get_ssh_key()
            tunnel_cmd = ["ssh", "-p", ssh_port]

            if ssh_key:
                tunnel_cmd.extend(["-i", ssh_key])

            tunnel_cmd.extend([
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "BatchMode=yes",
                "-o", "ServerAliveInterval=60",
                "-o", "ServerAliveCountMax=3",
                "-N",  # No command execution
                "-L", f"{self.local_cmd_port}:localhost:{self.remote_cmd_port}",
                "-L", f"{self.local_pub_port}:localhost:{self.remote_pub_port}",
                f"root@{ssh_host}"
            ])

            self.ssh_tunnel_proc = subprocess.Popen(
                tunnel_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait briefly for tunnel to establish
            await asyncio.sleep(2)

            if self.ssh_tunnel_proc.poll() is not None:
                return {
                    "status": "error",
                    "message": "SSH tunnel failed to establish"
                }

            return {
                "status": "ok",
                "message": "SSH tunnel created",
                "pid": self.ssh_tunnel_proc.pid
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Tunnel creation error: {str(e)}"
            }

    async def _start_remote_worker(self, ssh_host: str, ssh_port: str) -> dict[str, object]:
        """
        Start ZMQ worker on remote pod.

        args:
            ssh_host: SSH host address
            ssh_port: SSH port

        returns:
            dict with worker start status
        """
        try:
            # Start worker in background on remote pod
            ssh_key = self._get_ssh_key()
            worker_cmd = ["ssh", "-p", ssh_port]

            if ssh_key:
                worker_cmd.extend(["-i", ssh_key])

            worker_cmd.extend([
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=10",
                f"root@{ssh_host}",
                (
                    f"cd /tmp && "
                    f"export MC_ZMQ_CMD_ADDR=tcp://0.0.0.0:{self.remote_cmd_port} && "
                    f"export MC_ZMQ_PUB_ADDR=tcp://0.0.0.0:{self.remote_pub_port} && "
                    f"export PYTHONPATH=/tmp:$PYTHONPATH && "
                    f"nohup {sys.executable} -m morecompute.execution.worker "
                    f"> /tmp/worker.log 2>&1 & "
                    f"echo $!"
                )
            ])

            result = subprocess.run(
                worker_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Failed to start remote worker: {result.stderr}"
                }

            remote_pid = result.stdout.strip()

            # Wait for worker to be ready
            await asyncio.sleep(2)

            return {
                "status": "ok",
                "message": "Remote worker started",
                "remote_pid": remote_pid
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Worker start error: {str(e)}"
            }

    def get_executor_addresses(self) -> dict[str, str]:
        """
        Get ZMQ addresses for executor to connect to tunneled ports.

        returns:
            dict with cmd_addr and pub_addr
        """
        return {
            "cmd_addr": f"tcp://127.0.0.1:{self.local_cmd_port}",
            "pub_addr": f"tcp://127.0.0.1:{self.local_pub_port}"
        }

    def attach_executor(self, executor: "NextZmqExecutor") -> None:
        """
        Attach an executor instance to this pod manager.

        args:
            executor: The executor to attach
        """
        self.executor = executor

    async def disconnect(self) -> dict[str, object]:
        """
        Disconnect from pod and cleanup tunnels.

        returns:
            dict with disconnection status
        """
        messages = []
        if self.ssh_tunnel_proc:
            try:
                self.ssh_tunnel_proc.terminate()
                try:
                    self.ssh_tunnel_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.ssh_tunnel_proc.kill()
                messages.append("SSH tunnel closed")
            except Exception as e:
                messages.append(f"Error closing tunnel: {str(e)}")
            finally:
                self.ssh_tunnel_proc = None

        # Note: We don't kill remote worker as it may be used by other connections
        # The pod itself should clean up when terminated

        self.pod = None

        return {
            "status": "ok",
            "messages": messages
        }

    async def get_status(self) -> dict[str, object]:
        """
        Get current connection status.

        returns:
            dict with status information
        """
        if not self.pod:
            return {
                "connected": False,
                "pod": None
            }

        # Check tunnel status
        tunnel_alive = False
        if self.ssh_tunnel_proc:
            tunnel_alive = self.ssh_tunnel_proc.poll() is None

        # Get updated pod info
        try:
            updated_pod = await self.pi_service.get_pod(self.pod.id)
            pod_status = updated_pod.status
        except Exception:
            pod_status = "unknown"

        return {
            "connected": True,
            "pod": {
                "id": self.pod.id,
                "name": self.pod.name,
                "status": pod_status,
                "gpu_type": self.pod.gpuName,
                "gpu_count": self.pod.gpuCount,
                "price_hr": self.pod.priceHr,
                "ssh_connection": self.pod.sshConnection
            },
            "tunnel": {
                "alive": tunnel_alive,
                "local_cmd_port": self.local_cmd_port,
                "local_pub_port": self.local_pub_port
            },
            "executor_attached": self.executor is not None
        }
