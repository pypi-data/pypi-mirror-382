from gql import gql
from typing import Sequence

class createMethods:

    _CreateUserApiKeyQuery = """
    mutation CreateUserApiKey($object: UserApiKeys_insert_input!) {
    insert_UserApiKeys_one(object: $object) {
        id
        org_id
        status
        user_id
        client_id
        org_client_id
        created
    	description
    }
}
    """

    def CreateUserApiKey(self, object: dict):
        query = gql(self._CreateUserApiKeyQuery)
        variables = {
            "object": object,
        }
        operation_name = "CreateUserApiKey"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _RotateUserApiKeyQuery = """
    mutation RotateUserApiKey($org_id: Int!, $user_id: String!, $org_client_id: String!, $entity_secret: String!, $expiry: timestamptz!) {
  update_UserApiKeys(
    where: {
        org_id: {_eq: $org_id},
        user_id: {_eq: $user_id},
        expiry: {_is_null: true}
    },
    _set: {expiry: $expiry}
  ) {
      affected_rows
  }
  insert_UserApiKeys_one(object: {
      org_id: $org_id,
      user_id: $user_id,
      org_client_id: $org_client_id,
      entity_secret: $entity_secret
  }) {
      id
  }
}
    """

    def RotateUserApiKey(self, org_id: int, user_id: str, org_client_id: str, entity_secret: str, expiry: dict):
        query = gql(self._RotateUserApiKeyQuery)
        variables = {
            "org_id": org_id,
            "user_id": user_id,
            "org_client_id": org_client_id,
            "entity_secret": entity_secret,
            "expiry": expiry,
        }
        operation_name = "RotateUserApiKey"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
