import datetime
from collections.abc import Iterator
from typing import Optional

from dateutil.tz import gettz

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_generate_token_request import V1GenerateTokenRequest

from .. import interactive_console
from ..entities.pat import PersonalAccessToken
from ..utils import Utils


class PersonalAccessTokens:
    def __init__(self, stub: CoreServiceApi):
        self._stub = stub

    def generate(self, name: str, description: str, expiry_date: Optional[str] = None, timezone: Optional[str] = None) -> str:
        """Generate a personal access token for the currently logged-in user.

        Args:
            name: (str) A token name.
            description: (str) A description about the token.
            expiry_date: (str) Object represents a date string with format dd/MM/yyyy. Default is None.
            timezone: (str) Object represents a time zone name (Eg: 'America/Chicago'). Default is None.

        Returns:
            str: A token string for authentication.

        Typical example:
            token_str = client.auth.pats.generate(name="background_jobs", description="some description",
              expiry_date="<dd/MM/yyyy>", timezone=None)

        Raises:
            Exception: Invalid timezone.
            ValueError: Expiry date must be in the format: dd/MM/yyyy.

        For more details:
            https://docs.h2o.ai/featurestore/api/authentication.html#authentication-via-personal-access-tokens-pats
        """
        request = V1GenerateTokenRequest()
        request.name = name
        request.description = description
        if expiry_date:
            try:
                if timezone:
                    desired_timezone = gettz(timezone)
                    if not desired_timezone:
                        raise Exception(f"Invalid timezone id: '{timezone}'")
                else:
                    desired_timezone = None
                expiration = datetime.datetime.strptime(expiry_date, "%d/%m/%Y").astimezone(desired_timezone)
                request.expiry_date = expiration
            except ValueError:
                raise Exception("Expiry date must be in the format: dd/MM/yyyy")
        response = self._stub.core_service_generate_token(request)

        if not expiry_date:
            expire_date_used = Utils.timestamp_to_string(response.token_expiry_date)
            interactive_console.log("As expiry_date wasn't explicitly specified,")
            interactive_console.log(f"it was set to {expire_date_used} according to feature store policies.")
            interactive_console.log("Call client.auth.pats.maximum_allowed_token_duration to find out a limit.")

        return response.token

    def list(self, query: Optional[str] = None) -> Iterator[PersonalAccessToken]:
        """Return a generator which obtains the personal access tokens owned by current user, lazily.

        Args:
            query: (str) the name or description by which to search for the personal access tokens

        Returns:
            Iterable[PersonalAccessToken]: A generator iterator object consists of personal access tokens.

        Typical example:
            client.auth.pats.list()
        """
        has_next_page = True
        page_size = 100
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_personal_access_tokens(page_size=page_size, page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for pat in response.personal_access_tokens:
                yield PersonalAccessToken(self._stub, pat)

    def get(self, token_id: str) -> PersonalAccessToken:
        """Obtain a particular personal access token.

        Args:
            token_id: (str) A unique id of a token object.

        Returns:
            PersonalAccessToken: A token object.

        Typical example:
            client.auth.pats.get("token_id")
        """
        response = self._stub.core_service_get_token(token_id=token_id)
        return PersonalAccessToken(self._stub, response.token)

    @property
    def maximum_allowed_token_duration(self) -> str:
        """Obtain a maximum token duration that can't be exceeded when generating a token.

        Returns:
            Duration.

        Typical example:
            client.auth.pats.maximum_allowed_token_duration
        """
        response = self._stub.core_service_get_tokens_config()
        return response.maximum_allowed_token_duration

    def __repr__(self):
        return "This class wraps together methods working with Personal Access Tokens (PATs)"
