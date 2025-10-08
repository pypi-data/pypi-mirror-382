from .create import createMethods
from .get import getMethods
from .update import updateMethods

class OrganizationCredentialsMethods(
	createMethods,
	getMethods,
	updateMethods
):
	pass
