from .create import createMethods
from .get import getMethods
from .list import listMethods
from .update import updateMethods

class UserApiKeysMethods(
	createMethods,
	getMethods,
	listMethods,
	updateMethods
):
	pass
