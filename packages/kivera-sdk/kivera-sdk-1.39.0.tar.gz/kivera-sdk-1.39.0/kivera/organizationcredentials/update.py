from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateOrganizationCredentialsQuery = """
    mutation UpdateOrganizationCredentials($client_id: String!, $object: OrganizationCredentials_set_input!) {
  update_OrganizationCredentials_by_pk(pk_columns: {client_id: $client_id}, _set: $object) {
    client_id
  }
}
    """

    def UpdateOrganizationCredentials(self, client_id: str, object: dict):
        query = gql(self._UpdateOrganizationCredentialsQuery)
        variables = {
            "client_id": client_id,
            "object": object,
        }
        operation_name = "UpdateOrganizationCredentials"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
