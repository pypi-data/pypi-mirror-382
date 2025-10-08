from packaging import version


class ComponentVersions:
    def __init__(self, client_version, server_version):
        self._client_version = client_version
        self._server_version = server_version

    @property
    def client_version(self) -> str:
        return self._client_version

    @property
    def server_version(self) -> str:
        return self._server_version

    def client_is_newer_than_server(self) -> bool:
        return version.parse(self._client_version) > version.parse(self._server_version)

    def server_is_newer_than_client(self) -> bool:
        return version.parse(self.server_version) > version.parse(self.client_version)

    def __repr__(self):
        return f"Client version : {self._client_version}\n" f"Server version : {self._server_version}"
