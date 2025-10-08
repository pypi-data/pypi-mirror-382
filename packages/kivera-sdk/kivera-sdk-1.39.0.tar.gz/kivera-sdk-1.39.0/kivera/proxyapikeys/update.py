from gql import gql
from typing import Sequence

class updateMethods:

    _DisableProxyApiKeyByIdQuery = """
    mutation DisableProxyApiKeyById($id: Int!) {
    update_ProxyApiKeys(where: {id: {_eq: $id}}, _set: {status: false}) {
        returning {
            proxy_id
            api_key
            org_client_id
            id
            status
        }
    }
}
    """

    def DisableProxyApiKeyById(self, id: int):
        query = gql(self._DisableProxyApiKeyByIdQuery)
        variables = {
            "id": id,
        }
        operation_name = "DisableProxyApiKeyById"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
