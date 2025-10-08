from gql import gql
from typing import Sequence

class getMethods:

    _GetActiveOrganizationCredentialsQuery = """
    query GetActiveOrganizationCredentials($org_id: Int!) {
  OrganizationCredentials(where: {org_id: {_eq: $org_id}, deleted: {_eq: false}, expiry: {_is_null: true}}) {
    client_id
  }
}
    """

    def GetActiveOrganizationCredentials(self, org_id: int):
        query = gql(self._GetActiveOrganizationCredentialsQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "GetActiveOrganizationCredentials"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetExpiredCredentialsQuery = """
    query GetExpiredCredentials($time: timestamptz!) {
  OrganizationCredentials(where: {deleted: {_eq: false}, expiry: {_lt: $time}}) {
    client_id
    expiry
  }
  ProxyApiKeys(where: {status: {_eq: true}, expiry: {_lt: $time}}) {
    id
    api_key
    expiry
  }
  UserApiKeys(where: {status: {_eq: true}, expiry: {_lt: $time}}) {
    id
    client_id
    expiry
  }
}
    """

    def GetExpiredCredentials(self, time: dict):
        query = gql(self._GetExpiredCredentialsQuery)
        variables = {
            "time": time,
        }
        operation_name = "GetExpiredCredentials"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetOrganizationCredentialsQuery = """
    query GetOrganizationCredentials($org_id: Int!) {
  OrganizationCredentials(where: {org_id: {_eq: $org_id}, deleted: {_eq: false}}) {
    client_id
    expiry
  }
}
    """

    def GetOrganizationCredentials(self, org_id: int):
        query = gql(self._GetOrganizationCredentialsQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "GetOrganizationCredentials"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
