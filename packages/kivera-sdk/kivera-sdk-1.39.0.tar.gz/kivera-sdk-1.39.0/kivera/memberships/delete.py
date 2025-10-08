from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteMembershipQuery = """
    mutation DeleteMembership($membership_id: Int!){
    delete_MembershipRoles(where: {membership_id: {_eq: $membership_id}}) {
        affected_rows
    }
    delete_Memberships(where: {id: {_eq: $membership_id}}) {
        affected_rows
        returning {
            user_id
            org_id
        }
    }
}
    """

    def DeleteMembership(self, membership_id: int):
        query = gql(self._DeleteMembershipQuery)
        variables = {
            "membership_id": membership_id,
        }
        operation_name = "DeleteMembership"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteOrganizationMembershipQuery = """
    mutation DeleteOrganizationMembership($user_id: String!, $org_id: Int!) {
  update_Users(where: {_and: {id: {_eq: $user_id}, active_org_id: {_eq: $org_id}}}, _set: {active_org_id: null}) {
    affected_rows
  }
  delete_MembershipRoles(where: {Membership: {_and: {user_id: {_eq: $user_id}, org_id: {_eq: $org_id}}}}) {
    affected_rows
  }
  delete_Memberships(where: {_and: {user_id: {_eq: $user_id}, org_id: {_eq: $org_id}}}) {
    affected_rows
  }
}
    """

    def DeleteOrganizationMembership(self, user_id: str, org_id: int):
        query = gql(self._DeleteOrganizationMembershipQuery)
        variables = {
            "user_id": user_id,
            "org_id": org_id,
        }
        operation_name = "DeleteOrganizationMembership"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
