import subprocess
import typing
import logging

import coloredlogs

from serverpath import ServerPath


class MCServer:
    class ServerStateError(Exception):
        pass

    class ServerNotStartedError(ServerStateError):
        pass

    class ServerAlreadyStartedError(ServerStateError):
        pass

    def __init__(self, server_path: ServerPath = ServerPath(),
                 max_ram_alloc: typing.Annotated[int, "In MB"] = 2048,
                 log_level: str = 'WARNING'):
        self.server_path: ServerPath = server_path
        self.server_process: typing.Optional[subprocess.Popen] = None
        self.max_ram_alloc: int = max_ram_alloc

        self.logger: logging.Logger = logging.getLogger("MCServerWrapper")
        coloredlogs.install(level=log_level, logger=self.logger)
        self.logger.debug(f"MCServerWrapper instantiated")

    @property
    def stopped(self):
        self.logger.debug("Checking server status")
        if self.server_process is not None and self.server_process.poll() is not None:
            self.logger.info("Recent server stop detected")
            self.server_process = None
        self.logger.debug("Server status: " + ("stopped" if self.server_process is None else "running"))
        return self.server_process is None

    def start(self):
        self.logger.info(f"Starting server at '{self.server_path}'")
        if not self.stopped:
            raise MCServer.ServerAlreadyStartedError()

        self.server_process = subprocess.Popen(
            ["java", f"-Xmx{self.max_ram_alloc}M", f"-Xms{self.max_ram_alloc // 4}M",
             "-jar", str(self.server_path), "--nogui"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.logger.info(f"Server at '{self.server_path}' started")

    def send_command(self, command: typing.Annotated[str, "A Minecraft command, without the slash"]):
        self.logger.debug(f"Sending command '/{command}'")
        self.server_process.stdin.write((command + "\n").encode("utf-8"))
        self.server_process.stdin.flush()
        self.logger.debug(f"Command '/{command}' sent")

    def retrieve_logs(self):
        self.logger.debug("Retrieving server logs")
        return self.server_process.stdout.read1().decode('utf-8')

    def stop(self):
        self.logger.info("Stopping server")
        if self.stopped:
            raise MCServer.ServerNotStartedError()

        self.server_process.terminate()
        self.logger.info("Server stopped")


if __name__ == "__main__":
    server = MCServer(log_level='DEBUG')
    server.start()
    while not server.stopped:
        print(server.retrieve_logs())
    print("Server stopped")
