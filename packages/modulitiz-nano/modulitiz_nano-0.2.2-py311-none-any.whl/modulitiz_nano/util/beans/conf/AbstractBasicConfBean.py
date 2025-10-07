from modulitiz_nano.files.ModuloFiles import ModuloFiles

from modulitiz_nano.util.beans.conf.AbstractConfBean import AbstractConfBean


class AbstractBasicConfBean(AbstractConfBean):
	
	def __init__(self,clazz,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.INPUT_FILE_CONF=ModuloFiles.pathJoin(self.CARTELLA_BASE_PROGETTO,"conf.json")
		self.fileConf=clazz(self.INPUT_FILE_CONF)
