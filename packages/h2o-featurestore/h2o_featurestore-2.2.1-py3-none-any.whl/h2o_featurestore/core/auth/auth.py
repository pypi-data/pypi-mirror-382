from h2o_featurestore.gen.api.core_service_api import CoreServiceApi

from ..collections.pats import PersonalAccessTokens


class AuthWrapper:

    def __init__(self, stub: CoreServiceApi):
        self._stub = stub
        self.pats = PersonalAccessTokens(self._stub)

    def get_active_user(self):
      """Obtain currently active user details.

      Returns:
          UserBasicInfo: Logged-in user details.

          For example:

          id: <user_id>
          name: <user_name>
          email: <user_email>
      """
      return self._stub.core_service_get_active_user().user
