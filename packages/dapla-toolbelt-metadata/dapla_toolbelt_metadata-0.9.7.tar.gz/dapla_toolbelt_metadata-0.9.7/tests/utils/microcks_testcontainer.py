import urllib.parse
from pathlib import Path

import ruamel.yaml
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.generic import ServerContainer


class MicrocksContainer(ServerContainer):
    """Microcks Container.

    [Microcks](https://microcks.io/) allows mocking arbitrary API services based on an OpenAPI definition.

    This implementation supports a subset of Microcks functionality, supporting mocking a single service
    by uploading a single local definition file.
    """

    def __init__(
        self,
        port: int = 8080,
        image: str | DockerImage = "quay.io/microcks/microcks-uber:1.10.1-native",
    ) -> None:
        """Instantiate a Microcks container.

        Args:
            port (int, optional): The internal application port to use. Defaults to 8080.
            image (str | DockerImage, optional): The image name. Must be compatible with quay.io/microcks/microcks-uber. Defaults to "quay.io/microcks/microcks-uber:1.10.1-native".
        """
        super().__init__(port, image)
        self.primary_artifact: str | None = None

    def start(self) -> "ServerContainer":
        """Start the container and wait for it to be ready."""
        started = super().start()
        wait_for_logs(
            container=started,
            predicate=".*Started MicrocksApplication.*",
            timeout=10,
        )
        return started

    def get_api_url(self) -> str:
        """Get the base URL for the container."""
        return self._create_connection_url()

    def get_mock_url(self) -> str | None:
        """Get the base URL for the mocked service.

        Only relevant if an artifact has been uploaded.

        Returns:
            str | None: The base URL for the primary artifact, or None.
        """
        if not self.primary_artifact:
            return None

        version: str | None = None
        api_name: str | None = None

        with Path(self.primary_artifact).open() as openapi:
            openapi_yaml: dict = ruamel.yaml.YAML().load(openapi)

        info: dict | None = openapi_yaml.get("info")
        if info is None:
            return None
        version = info.get("version")
        api_name = info.get("title")

        if not version or not api_name:
            return None

        return (
            f"{self.get_api_url()}/rest/{urllib.parse.quote_plus(api_name)}/{version}"
        )

    def upload_primary_artifact(self, openapi_definition_path: str) -> str:
        """Upload a local OpenAPI definition file as the primary artifact.

        Args:
            openapi_definition_path (str): Path to the OpenAPI definition file

        Returns:
            _type_: _description_
        """
        with Path(openapi_definition_path).open("rb") as openapi:
            upload_response = self.get_client().post(
                "/api/artifact/upload",
                files={"file": openapi},
                timeout=30,
            )
            upload_response.raise_for_status()
        self.primary_artifact = openapi_definition_path
        return self.primary_artifact
