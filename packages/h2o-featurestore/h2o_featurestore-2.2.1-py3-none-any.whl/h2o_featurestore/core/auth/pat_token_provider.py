import re

from h2o_authn import TokenProvider


class PatTokenProvider(TokenProvider):
    """Returns the pat token when called."""
    def __init__(self, pat_token: str):
        if not self._is_personal_access_token(pat_token):
            raise ValueError("Invalid PAT token format. Expected format: 'xxx_...' where 'xxx' is a 3-character prefix.")
        self.pat_token = pat_token

    def __call__(self) -> str:
        return str(self.pat_token)

    @staticmethod
    def _is_personal_access_token(token: str) -> bool:
        return bool(re.match(r"^[a-z0-9]{3}_.*", token))
