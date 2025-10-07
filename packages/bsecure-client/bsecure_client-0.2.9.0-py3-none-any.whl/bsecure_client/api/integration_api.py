import logging

from .base import API

logger = logging.getLogger(__name__)


initiate_integration_mutation = """
  mutation initiateIntegration($host: String!, $organisation_name: String!, $bsecure_integration_secret: String!) {
      initiateIntegration(input: {
          host: $host, organisationName: $organisation_name, bsecureIntegrationSecret: $bsecure_integration_secret
          }) {
          jwt
      }
  }
"""


class IntegrationAPI(API):
    def initiate_integration(
        self, host: str, organisation_name: str, bsecure_integration_secret: str
    ) -> str:
        """Integrate this host with BSecure. Returns a JWT token if successful."""
        response_data = self.perform_query(
            initiate_integration_mutation,
            {
                "organisation_name": organisation_name,
                "host": host,
                "bsecure_integration_secret": bsecure_integration_secret,
            },
        )
        jwt = response_data["initiateIntegration"]["jwt"]
        return jwt
