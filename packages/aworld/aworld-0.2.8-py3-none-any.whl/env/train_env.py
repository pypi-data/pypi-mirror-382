import argparse
import asyncio
import json
import logging
from pathlib import Path
import socket
import traceback
import httpx

logger = logging.getLogger(__name__)


class TranEnv:

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.env_dir = self.base_dir / "env"
        self.mcp_config = None
        self.mcp_variables = None

    def get_env_config(self):
        if self.mcp_variables:
            url = f"http://{self.mcp_variables['ip']}:{self.mcp_variables['port']}/mcp"
            self.mcp_config = {
                "mcpServers": {
                    "virtualpc-mcp": {
                        "type": "streamable-http",
                        "url": url,
                        "headers": {
                            "Authorization": f"Bearer {self.mcp_variables['token']}",
                        },
                        "timeout": 600,
                        "sse_read_timeout": 600,
                        "client_session_timeout_seconds": 600,
                    }
                }
            }
            return self.mcp_config
        return None

    async def create_env(self, docker_dir: str = None) -> bool:
        if not docker_dir:
            logger.error(
                "You must provide --docker_dir to specify the Docker directory to build (relative to env)."
            )
            return False

        self.docker_dir = docker_dir

        image_ready = await self._build_image(docker_dir)
        assert image_ready, "Image is not ready!"

        service_ready = await self._start_service()
        assert service_ready, "Service config is not ready!"

        service_ready = await self._check_service_ready()
        assert service_ready, "Service is not ready!"

        self.mcp_variables = {
            "ip": self.get_local_ip(),
            "port": 8000,
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOiJsb2NhbF9kZWJ1ZyIsInZlcnNpb24iOjEsInRpbWUiOjE3NTYzOTUzNzIuMTg0MDc0NH0.SALKn1dxEzsdX82-e3jAJANAo_kE4NO4192Epw5rYmQ",
        }

        logger.info("✅ Service is ready!")
        return True

    async def _build_image(self, docker_dir: str):
        try:
            # Use asyncio.create_subprocess_exec for async subprocess execution
            logger.info(f"Building {docker_dir} image...")
            process1 = await asyncio.create_subprocess_exec(
                "sh",
                "build-image.sh",
                cwd=self.env_dir / "mcp-server-base",
            )
            await process1.wait()

            if process1.returncode != 0:
                logger.error("Failed to build mcp-server-base image")
                return False

            target_dir = self.env_dir / docker_dir
            if not target_dir.exists():
                logger.error(f"Specified Docker directory does not exist: {target_dir}")
                return False

            process2 = await asyncio.create_subprocess_exec(
                "sh",
                "build-image.sh",
                cwd=target_dir,
            )
            await process2.wait()

            if process2.returncode != 0:
                logger.error(f"Failed to build {docker_dir} image")
                return False

            logger.info("All images built successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to build image: {traceback.format_exc()}")
            return False

    async def _start_service(self):
        try:
            logger.info("Starting virtualpc-mcp service...")
            process = await asyncio.create_subprocess_exec(
                "sh",
                "run.sh",
                cwd=self.env_dir / self.docker_dir,
            )

            # Wait a bit for the service to start
            await asyncio.sleep(2)

            return True
        except Exception as e:
            logger.error(f"Failed to start service: {traceback.format_exc()}")
            return None

    async def _check_service_ready(self) -> bool:
        url = "http://localhost:8000/health"

        max_retries = 180
        for i in range(max_retries):
            try:
                # Try to establish MCP connection to check if service is ready
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return True
            except Exception as e:
                logger.error(
                    f"Waiting for service ready: {(i+1)}/{max_retries} attempts"
                )
                await asyncio.sleep(10)
        else:
            logger.error(
                f"Service at {url} is not reachable after {max_retries} attempts."
            )
            return False

    def get_local_ip(self):
        try:
            # build UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # connect to an external address (no need to connect)
            s.connect(("223.5.5.5", 80))
            # get local IP
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Env construction")
    parser.add_argument(
        "--docker_dir",
        default="gaia-mcp-server",
        help="Docker directory to build (relative to env, e.g., gaia-mcp-server)",
    )

    async def main():
        try:
            args = parser.parse_args()
            if not args.docker_dir:
                parser.error(
                    "You must use --docker_dir to specify the Docker directory to build (e.g., gaia-mcp-server)"
                )
            train_env = TranEnv()
            env_started = await train_env.create_env(docker_dir=args.docker_dir)
            if env_started:
                mcp_variables = json.dumps(
                    train_env.mcp_variables, ensure_ascii=False, indent=4
                )
                print(mcp_variables)
        except Exception as e:
            logger.error(f"Failed to start env: {traceback.format_exc()}")

    asyncio.run(main())
