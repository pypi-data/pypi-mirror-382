from ..utils import File
from .base import API
from .types import PatchTenantDocumentInput

get_tenant_query = """
  query getTenant(
    $uuid: UUID!
  ) {
    tenant(uuid: $uuid) {
      id
      uuid
      name
      clientName
      source
      place {
        id
        uuid
        name
        shortName
        description
        formattedAddress
        gcsCoord
        gnafId
      }
    }
  }
"""

push_tenant_query = """
  mutation pushTenant(
    $name: String!,
    $formattedAddress: String!,
    $latitude: Float!,
    $longitude: Float!,
    $source: String!,
    $gnafId: String,
    $clientName: String,
    $frontPhoto: String
  ) {
    pushTenant(input: {
      name: $name,
      formattedAddress: $formattedAddress,
      latitude: $latitude,
      longitude: $longitude,
      source: $source,
      gnafId: $gnafId,
      clientName: $clientName,
      frontPhoto: $frontPhoto
    }) {
      tenant {
        uuid
      }
    }
  }
"""

all_tenant_documents_query = """
  query tenantDocuments($uuid: UUID!) {
    tenant(uuid: $uuid) {
      id
      uuid
      name
      tenantdocumentSet {
        edges {
          node {
            id
            uuid
            title
            uploadedTimestamp
            filename
          }
        }
      }
    }
  }
"""

push_tenant_photo_mutation = """
  mutation pushTenantPhoto(
    $tenant_uuid: UUID!,
    $tmpfile_uuid: UUID!,
  ) {
    pushTenantPhoto(
      tenantUuid: $tenant_uuid,
      tmpfileUuid: $tmpfile_uuid,
    ) {
      tenantPhoto {
        uuid
      }
    }
  }
"""

push_tenant_document_mutation = """
  mutation pushTenantDocument(
    $tenant_uuid: UUID!,
    $title: String!,
    $tmpfile_uuid: UUID!,
  ) {
    pushTenantDocument(
      tenantUuid: $tenant_uuid,
      title: $title,
      tmpfileUuid: $tmpfile_uuid,
    ) {
      tenantDocument {
        uuid
      }
    }
  }
"""

delete_tenant_document_mutation = """
  mutation deleteTenantDocument(
    $tenant_document_uuid: UUID!
  ) {
    deleteTenantDocument(
      tenantDocumentUuid: $tenant_document_uuid,
    ) {
      tenantDocumentUuid
    }
  }
"""

patch_tenant_document_mutation = """
  mutation patchTenantDocument(
    $tenant_document_uuid: UUID!,
    $patch: PatchTenantDocumentInput!
  ) {
    patchTenantDocument(
      tenantDocumentUuid: $tenant_document_uuid,
      patch: $patch
    ) {
      tenantDocument {
        uuid
        title
      }
    }
  }
"""


class PlaceAPI(API):
    # TODO: Would be nice to be able to share these with the server
    # implementation.
    PUBLIC = "Public"
    AUDIT = "Audit"
    SERVICE = "Service"

    def push_tenant(
        self,
        name: str,
        formatted_address: str,
        gcs_coord: tuple[float, float],
        source: str,
        gnaf_id: str | None = None,
        client_name: str | None = None,
        front_photo: File | None = None,
    ) -> str:
        """Pushes a tenant into bsecure

        Creates a tenant for a place (and a plce if it does not exist).

        An existing place is chosen if:
            the gnaf_id matches
        OR
            the formatted_address and coordinates are close

        The source should also be provided eg: workforce or logbooks
        """
        response_data = self.perform_query(
            push_tenant_query,
            self.make_variables(
                name=name,
                formattedAddress=formatted_address,
                longitude=gcs_coord[0],
                latitude=gcs_coord[1],
                gnafId=gnaf_id,
                clientName=client_name,
                source=source.lower(),
            ),
        )
        tenant_uuid = response_data["pushTenant"]["tenant"]["uuid"]
        if front_photo:
            self.push_tenant_photo(tenant_uuid, front_photo)
        return tenant_uuid

    def all_tenant_documents(self, tenant_uuid: str) -> list[dict]:
        response_data = self.perform_query(all_tenant_documents_query, {"uuid": tenant_uuid})
        return [edge["node"] for edge in response_data["tenant"]["tenantdocumentSet"]["edges"]]

    def get_tenant(self, uuid: str) -> dict:
        """Returns a tenant (and parent place) by uuid"""
        response_data = self.perform_query(get_tenant_query, {"uuid": uuid})
        return response_data["tenant"]

    def push_tenant_photo(self, tenant_uuid: str, photo: File) -> str:
        assert photo
        tmpfile_uuid = self.upload_file(photo)
        response_data = self.perform_query(
            push_tenant_photo_mutation,
            {
                "tenant_uuid": tenant_uuid,
                "tmpfile_uuid": tmpfile_uuid,
            },
        )
        return response_data["pushTenantPhoto"]["tenantPhoto"]["uuid"]

    def push_tenant_document(self, tenant_uuid: str, title: str, document: File) -> str:
        assert document
        tmpfile_uuid = self.upload_file(document)
        response_data = self.perform_query(
            push_tenant_document_mutation,
            {
                "tenant_uuid": tenant_uuid,
                "title": title,
                "tmpfile_uuid": tmpfile_uuid,
            },
        )
        return response_data["pushTenantDocument"]["tenantDocument"]["uuid"]

    def delete_tenant_document(self, tenant_document_uuid: str) -> str:
        response_data = self.perform_query(
            delete_tenant_document_mutation,
            {
                "tenant_document_uuid": tenant_document_uuid,
            },
        )
        return response_data["deleteTenantDocument"]["tenantDocumentUuid"]

    def patch_tenant_document(
        self, tenant_document_uuid: str, patch: PatchTenantDocumentInput
    ) -> dict:
        response_data = self.perform_query(
            patch_tenant_document_mutation,
            {"tenant_document_uuid": tenant_document_uuid, "patch": patch.model_dump()},
        )
        return response_data["patchTenantDocument"]["tenantDocument"]
