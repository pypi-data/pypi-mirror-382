from modulitiz_nano.files.ModuloLogging import ModuloLogging
from modulitiz_nano.multithread.ModuloThreadWithCallbackError import ModuloThreadWithCallbackError


class ModuloThreadLogger(ModuloThreadWithCallbackError):
	
	def __init__(self,logger:ModuloLogging,**kwargs):
		super().__init__(lambda ex:logger.exception('Eccezione nel thread:'),**kwargs)
