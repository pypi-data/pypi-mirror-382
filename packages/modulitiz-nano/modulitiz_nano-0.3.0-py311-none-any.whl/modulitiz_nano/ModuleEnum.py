class ModuleEnum(object):
	@staticmethod
	def isValueIn(value, enumClass)->bool:
		try:
			enumClass(value)
		except ValueError:
			return False
		return True
