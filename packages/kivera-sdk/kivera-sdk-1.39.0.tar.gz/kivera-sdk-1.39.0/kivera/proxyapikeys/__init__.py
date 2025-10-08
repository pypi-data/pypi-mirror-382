from .create import createMethods
from .get import getMethods
from .update import updateMethods

class ProxyApiKeysMethods(
	createMethods,
	getMethods,
	updateMethods
):
	pass
