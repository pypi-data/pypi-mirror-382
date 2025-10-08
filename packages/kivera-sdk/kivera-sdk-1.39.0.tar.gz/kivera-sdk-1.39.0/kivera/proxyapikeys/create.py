from gql import gql
from typing import Sequence

class createMethods:

    _CreateProxyApiKeyQuery = """
    mutation CreateProxyApiKey($object: ProxyApiKeys_insert_input!) {
  insert_ProxyApiKeys_one(object: $object) {
    api_key
    id
    proxy_id
  }
}
    """

    def CreateProxyApiKey(self, object: dict):
        query = gql(self._CreateProxyApiKeyQuery)
        variables = {
            "object": object,
        }
        operation_name = "CreateProxyApiKey"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _RotateProxyApiKeyQuery = """
    mutation RotateProxyApiKey($org_id: Int!, $proxy_id: Int!, $org_client_id: String!, $entity_secret: String!, $expiry: timestamptz!) {
  update_ProxyApiKeys(
    where: {
        org_id: {_eq: $org_id},
        proxy_id: {_eq: $proxy_id},
        expiry: {_is_null: true}
    },
    _set: {expiry: $expiry}
  ) {
      affected_rows
  }
  insert_ProxyApiKeys_one(object: {
      org_id: $org_id,
      proxy_id: $proxy_id,
      org_client_id: $org_client_id,
      entity_secret: $entity_secret
  }) {
      id
  }
}
    """

    def RotateProxyApiKey(self, org_id: int, proxy_id: int, org_client_id: str, entity_secret: str, expiry: dict):
        query = gql(self._RotateProxyApiKeyQuery)
        variables = {
            "org_id": org_id,
            "proxy_id": proxy_id,
            "org_client_id": org_client_id,
            "entity_secret": entity_secret,
            "expiry": expiry,
        }
        operation_name = "RotateProxyApiKey"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
