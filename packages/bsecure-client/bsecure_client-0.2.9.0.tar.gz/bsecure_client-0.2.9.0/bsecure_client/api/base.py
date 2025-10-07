import requests

from ..exceptions import QueryException
from ..utils import File, make_serializeable, remove_trailing_slash

upload_file_mutation = """
  mutation uploadFile($filename: String!) {
    uploadFile(filename: $filename) {
      guid,
      presignedUrl
    }
  }
"""


class API:
    SUCCESS_RESPONSE_CODES = (200, 201)

    def __init__(self, client):
        self.client = client

    def perform_query(self, query, variables=None, headers=None):
        response = self.send_query(query, variables, headers)
        response.raise_for_status()
        response_data = response.json()
        self.check_for_errors(response_data)
        return response_data["data"]

    def get_url(self) -> str:
        domain: str = remove_trailing_slash(self.client.domain)
        if domain.startswith("https://") or domain.startswith("http://"):
            return f"{domain}/graphql/"
        else:
            return f"{self.client.protocol}://{domain}/graphql/"

    def send_query(self, query, variables, headers):
        auth_headers = {}
        url = self.get_url()

        if self.client.jwt:
            auth_headers["Authorization"] = f"Bearer {self.client.jwt}"
        response = requests.post(
            url,
            json={"query": query, "variables": make_serializeable(variables)},
            headers={
                **({"Origin": self.client.origin} if self.client.origin else {}),
                **auth_headers,
                **(headers or {}),
            },
            timeout=30,
        )
        # This will only trigger for 400/500 django view exceptions.
        if response.status_code not in self.SUCCESS_RESPONSE_CODES:
            msg = response.content
            raise QueryException(f"BSECURE error: {str(msg)}")

        return response

    def upload_file(self, file: File | None) -> str | None:
        """Uploads a `File` in echange for a tmpfile_uuid

        This is used by other mutations to upload a file to a temporary s3 location
        before it is published with another mutation
        """
        if not file:
            return None
        response_data = self.perform_query(upload_file_mutation, {"filename": file.filename})
        if "uploadFile" not in response_data.keys() or not response_data["uploadFile"]:
            raise QueryException("Failed to upload file: You do not have permission")

        tmpfile_uuid = response_data["uploadFile"]["guid"]
        presigned_url = response_data["uploadFile"]["presignedUrl"]

        # Upload file to s3
        upload_response = requests.put(presigned_url, data=file.content.read(), timeout=200)

        if upload_response.status_code != 200:
            raise QueryException(f"Failed to upload file: {upload_response.text}")

        return tmpfile_uuid

    def check_for_errors(self, response_data):
        # GraphQL responses only throw 400s and 500s if something goes
        # very wrong, so we need to check the error fields in addition.
        if response_data.get("errors"):
            try:
                msg = response_data["errors"][0]["message"]
                error_type = response_data["errors"][0].get("type")
            except KeyError:
                msg = "unknown reason"
                error_type = "BSECURE error"

            raise QueryException(message=msg, type=error_type)

    def make_variables(self, **kwargs):
        return {key: value for key, value in kwargs.items() if value is not None}
