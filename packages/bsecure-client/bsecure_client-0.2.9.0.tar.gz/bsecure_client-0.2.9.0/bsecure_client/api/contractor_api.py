from ..utils import File
from .base import API
from .types import PushContractorInput

contractor_fields = """
  id
  uuid
  name
  businessNumber
  aboutUs
  address
  country
  email
  phone
  industries
  isActive
  servicesProvided
  serviceAreas
  website
  logo
"""

get_contractor_query = f"""
  query getContractor(
    $uuid: UUID!
  ) {{
    contractor(uuid: $uuid) {{
      {contractor_fields}
    }}
  }}
"""

my_contractor_query = f"""
  query myContractor {{
    myContractor {{
      {contractor_fields}
    }}
  }}
"""

push_contractor_query = """
  mutation pushContractor(
    $name: String!,
    $businessNumber: String!,
    $aboutUs: String,
    $address: String!,
    $country: Country!,
    $email: String!,
    $industries: [Industry!]!,
    $isActive: Boolean,
    $phone: String!,
    $serviceAreas: String,
    $servicesProvided: [ServiceProvided!]!,
    $website: String,
  ) {
    pushContractor(input: {
      name: $name,
      businessNumber: $businessNumber,
      aboutUs: $aboutUs,
      address: $address,
      country: $country,
      email: $email,
      industries: $industries,
      isActive: $isActive,
      phone: $phone,
      serviceAreas: $serviceAreas,
      servicesProvided: $servicesProvided,
      website: $website,
    }) {
      contractor {
        uuid
      }
    }
  }
"""

all_contractors_query = """
  query allContractors {
    allContractors(isActive: true) {
      edges {
        node {
          id
          uuid
          name
          businessNumber
          aboutUs
          address
          country
          email
          phone
          industries
          isActive
          servicesProvided
          serviceAreas
          website
        }
      }
    }
  }
"""

push_contractor_logo_query = """
  mutation pushContractorLogo(
    $logo: String!,
  ) {
    pushContractorLogo(
      logo: $logo,
    ) {
      contractor {
        uuid
      }
    }
  }

"""


class ContractorAPI(API):
    def get_contractor(self, uuid: str) -> dict:
        """Returns a contractor by uuid"""
        response_data = self.perform_query(get_contractor_query, {"uuid": uuid})
        return response_data["contractor"]

    def push_contractor(self, input: PushContractorInput) -> str:
        """Pushes a contractor into bsecure"""
        response_data = self.perform_query(
            push_contractor_query,
            self.make_variables(
                name=input.name,
                businessNumber=input.business_number,
                aboutUs=input.about_us,
                address=input.address,
                country=input.country,
                email=input.email,
                industries=input.industries,
                isActive=input.is_active,
                phone=input.phone,
                serviceAreas=input.service_areas,
                servicesProvided=input.services_provided,
                website=input.website,
            ),
        )

        return response_data["pushContractor"]["contractor"]["uuid"]

    def push_contractor_logo(self, logo: File):
        logo_file_id = self.upload_file(logo)
        self.perform_query(
            push_contractor_logo_query,
            self.make_variables(
                logo=logo_file_id,
            ),
        )

    def all_contractors(self) -> list[dict]:
        response_data = self.perform_query(all_contractors_query, {})
        return [edge["node"] for edge in response_data["allContractors"]["edges"]]

    def my_contractor(self) -> dict:
        response_data = self.perform_query(my_contractor_query, {})
        return response_data["myContractor"]
