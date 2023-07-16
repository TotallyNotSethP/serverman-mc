import typing
from pathlib import Path


class ServerPath:
    def __init__(self, server_path: typing.Annotated[str, "Path to an existing Minecraft Server JAR"] = "server.jar"):
        self.server_path = Path(server_path).resolve()
        if not self.server_path.is_file():
            raise FileNotFoundError(f"{server_path} does not exist or is not a file.")

    def __str__(self):
        return str(self.server_path)
