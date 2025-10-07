from .base import API

route_to_tenant_mutation = """
  mutation routeToTenant($tenantUuid: UUID!, $routeCode: String!) {
    routeToTenant(input: {tenantUuid: $tenantUuid, routeCode: $routeCode}) {
      route {
        id
        uuid
      }
    }
  }
"""

route_to_asset_mutation = """
  mutation routeToAsset($assetUuid: UUID!, $routeCode: String!) {
    routeToAsset(input: {assetUuid: $assetUuid, routeCode: $routeCode}) {
      route {
        id
        uuid
      }
    }
  }
"""


route_to_cabinet_mutation = """
  mutation routeToCabinet($cabinetUuid: UUID!, $routeCode: String!) {
    routeToCabinet(input: {cabinetUuid: $cabinetUuid, routeCode: $routeCode}) {
      route {
        id
        uuid
      }
    }
  }
"""


remove_cabinet_from_route_mutation = """
  mutation removeCabinetFromRoute($cabinetUuid: UUID!, $routeCode: String!) {
    removeCabinetFromRoute(input: {cabinetUuid: $cabinetUuid, routeCode: $routeCode}) {
      route {
        id
        uuid
      }
    }
  }
"""


class RoutingAPI(API):
    def route_to_tenant(self, route_code: str, tenant_uuid: str) -> str:
        result = self.perform_query(
            route_to_tenant_mutation,
            {"routeCode": route_code, "tenantUuid": tenant_uuid},
        )
        return result["routeToTenant"]["route"]["uuid"]

    def route_to_asset(self, route_code: str, asset_uuid: str) -> str:
        result = self.perform_query(
            route_to_asset_mutation, {"routeCode": route_code, "assetUuid": asset_uuid}
        )
        return result["routeToAsset"]["route"]["uuid"]

    def route_to_cabinet(self, route_code: str, cabinet_uuid: str) -> str:
        result = self.perform_query(
            route_to_cabinet_mutation,
            {"routeCode": route_code, "cabinetUuid": cabinet_uuid},
        )
        return result["routeToCabinet"]["route"]["uuid"]

    def remove_cabinet_from_route(self, route_code: str, cabinet_uuid: str) -> str:
        result = self.perform_query(
            remove_cabinet_from_route_mutation,
            {"routeCode": route_code, "cabinetUuid": cabinet_uuid},
        )
        return result["removeCabinetFromRoute"]["route"]["uuid"]
