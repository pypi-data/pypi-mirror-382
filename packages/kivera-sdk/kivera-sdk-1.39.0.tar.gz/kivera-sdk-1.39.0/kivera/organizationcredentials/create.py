from gql import gql
from typing import Sequence

class createMethods:

    _InsertOrganizationCredentialsQuery = """
    mutation InsertOrganizationCredentials($object: OrganizationCredentials_insert_input!) {
  insert_OrganizationCredentials_one(object: $object) {
    client_id
  }
}
    """

    def InsertOrganizationCredentials(self, object: dict):
        query = gql(self._InsertOrganizationCredentialsQuery)
        variables = {
            "object": object,
        }
        operation_name = "InsertOrganizationCredentials"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
