from .api.asset_api import AssetAPI
from .api.contractor_api import ContractorAPI
from .api.integration_api import IntegrationAPI
from .api.place_api import PlaceAPI
from .api.routing_api import RoutingAPI


class BSecureClient(ContractorAPI, PlaceAPI, AssetAPI, IntegrationAPI, RoutingAPI):
    DEFAULT_DOMAIN = "bsec.me"

    def __init__(self, domain=None, origin=None, encrypt=True, jwt=None):
        self.protocol = "https" if encrypt else "http"
        self.domain = domain or self.DEFAULT_DOMAIN
        self.origin = origin
        self.jwt = jwt

        # TBH this isn't ideal but at least we have proper typing for all
        # the apis now....
        # Ideally we just have PlaceAPI as an instansiated attribute on the client...
        # like BsecureClient().place.get_tenant_by_uid
        # This is still better than monkey patching this base class with methods dynamically
        for superclass in [
            ContractorAPI,
            PlaceAPI,
            AssetAPI,
            IntegrationAPI,
            RoutingAPI,
        ]:
            super(superclass, self).__init__(self)  # type: ignore
