import datetime as dt

from ..utils import File, make_timestamp
from .base import API
from .types import PatchAssetInput, PatchRemarkInput, PatchServiceInput

remark_fields = """
    uuid
    createdTimestamp
    resolvedTimestamp
    description
    severity
    resolution
    created
    updated
"""

service_fields = """
    uuid
    name
    description
    createdTimestamp
    dueDate
    performedTimestamp
    result
    created
    updated
"""

asset_fields = """
    uuid
    code
    category
    make
    model
    size
    location
    status
    condition
    photo
    installationTimestamp
    expectedLifeYears
"""


push_asset_query = """
  mutation pushAsset(
    $tenantUuid: UUID!,
    $category: String!,
    $code: String!,
    $make: String,
    $model: String,
    $installationTimestamp: DateTime,
    $expectedLifeYears: Float,
    $photo: String
  ) {
    pushAsset(input: {
      tenantUuid: $tenantUuid,
      category: $category,
      code: $code,
      model: $model,
      make: $make,
      installationTimestamp: $installationTimestamp,
      expectedLifeYears: $expectedLifeYears,
      photo: $photo
    }) {
      asset {
        uuid
      }
    }
  }
"""

push_remark_query = """
  mutation pushRemark(
    $assetUuid: UUID!,
    $createdTimestamp: DateTime!,
    $resolvedTimestamp: DateTime,
    $description: String,
    $resolution: String
  ) {
    pushRemark(input: {
      assetUuid: $assetUuid,
      createdTimestamp: $createdTimestamp,
      resolvedTimestamp: $resolvedTimestamp,
      description: $description,
      resolution: $resolution
    }) {
      remark {
        uuid
      }
    }
  }
"""

push_service_query = """
  mutation pushService(
    $assetUuid: UUID!,
    $name: String!,
    $createdTimestamp: DateTime!,
    $description: String,
    $dueDate: Date,
    $performedTimestamp: DateTime,
    $result: String
  ) {
    pushService(input: {
      assetUuid: $assetUuid,
      name: $name,
      createdTimestamp: $createdTimestamp,
      description: $description,
      dueDate: $dueDate,
      performedTimestamp: $performedTimestamp,
      result: $result
    }) {
      service {
        uuid
      }
    }
  }
"""


patch_asset_mutation = f"""
  mutation patchAsset(
    $uuid: UUID!,
    $patch: PatchAssetInput!
  ) {{
    patchAsset(uuid: $uuid, patch: $patch) {{
      asset {{
        {asset_fields}
      }}
    }}
  }}
"""

patch_service_mutation = f"""
  mutation patchService(
    $uuid: UUID!,
    $patch: PatchServiceInput!
  ) {{
    patchService(uuid: $uuid, patch: $patch) {{
      service {{
          {service_fields}
      }}
    }}
  }}
"""

patch_remark_mutation = f"""
  mutation patchRemark(
    $uuid: UUID!,
    $patch: PatchRemarkInput!
  ) {{
    patchRemark(uuid: $uuid, patch: $patch) {{
      remark {{
          {remark_fields}
      }}
    }}
  }}
"""


class AssetAPI(API):
    def push_asset(
        self,
        tenant_uuid: str,
        category: str,
        code: str | None = None,
        make: str | None = None,
        model: str | None = None,
        installation_timestamp: dt.datetime | None = None,
        expected_life_years: float | None = None,
        photo: File | None = None,
    ) -> str:
        photo_file_id = self.upload_file(photo)
        response_data = self.perform_query(
            push_asset_query,
            self.make_variables(
                tenantUuid=tenant_uuid,
                category=category,
                code=code,
                make=make,
                model=model,
                installationTimestamp=make_timestamp(installation_timestamp),
                expectedLifeYears=expected_life_years,
                photo=photo_file_id,
            ),
        )
        return response_data["pushAsset"]["asset"]["uuid"]

    def push_asset_remark(
        self,
        asset_uuid: str,
        created_timestamp: dt.datetime,
        resolved_timestamp: dt.datetime | None = None,
        description: str | None = None,
        resolution: str | None = None,
    ) -> str:
        response_data = self.perform_query(
            push_remark_query,
            self.make_variables(
                assetUuid=asset_uuid,
                createdTimestamp=make_timestamp(created_timestamp),
                resolvedTimestamp=make_timestamp(resolved_timestamp),
                description=description,
            ),
        )
        return response_data["pushRemark"]["remark"]["uuid"]

    def push_asset_service(
        self,
        asset_uuid: str,
        name: str,
        created_timestamp: dt.datetime,
        description: str | None = None,
        due_date: dt.date | None = None,
        performed_timestamp: dt.datetime | None = None,
        result: str | None = None,
    ) -> str:
        response_data = self.perform_query(
            push_service_query,
            self.make_variables(
                assetUuid=asset_uuid,
                name=name,
                description=description,
                createdTimestamp=make_timestamp(created_timestamp),
                dueDate=make_timestamp(due_date),
                performedTimestamp=make_timestamp(performed_timestamp),
                result=result,
            ),
        )
        return response_data["pushService"]["service"]["uuid"]

    def patch_asset(
        self,
        asset_uuid: str,
        patch: PatchAssetInput,
    ) -> dict:
        photo = patch.photo
        if isinstance(photo, File):
            patch.photo = self.upload_file(photo)
        response_data = self.perform_query(
            patch_asset_mutation,
            variables={"uuid": asset_uuid, "patch": patch.model_dump()},
        )
        return response_data["patchAsset"]["asset"]

    def patch_service(self, service_uuid: str, patch: PatchServiceInput) -> dict:
        response_data = self.perform_query(
            patch_service_mutation,
            variables={"uuid": service_uuid, "patch": patch.model_dump()},
        )
        return response_data["patchService"]["service"]

    def patch_remark(self, remark_uuid: str, patch: PatchRemarkInput) -> dict:
        response_data = self.perform_query(
            patch_remark_mutation,
            variables={"uuid": remark_uuid, "patch": patch.model_dump()},
        )
        return response_data["patchRemark"]["remark"]
