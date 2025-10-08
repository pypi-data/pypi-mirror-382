
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.api.online_service_api import OnlineServiceApi
