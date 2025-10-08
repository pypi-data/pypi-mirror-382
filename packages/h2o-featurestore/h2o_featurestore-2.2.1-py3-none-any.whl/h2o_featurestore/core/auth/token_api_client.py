import uuid
from typing import Callable

from h2o_featurestore.gen.api_client import ApiClient
from h2o_featurestore.gen.api_client import Configuration


class TokenApiClient(ApiClient):
    """Overrides update_params_for_auth method of the generated ApiClient classes"""

    def __init__(self, configuration: Configuration, token_provider: Callable[[], str]):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(
        self,
        headers,
        queries,
        auth_settings,
        resource_path,
        method,
        body,
        request_auths=None,
    ):
        token = self._token_provider()
        headers["Authorization"] = f"Bearer {token}"
        headers["request-id"] = str(uuid.uuid4())
