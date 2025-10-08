import os.path

import vulture
from vulture.utils import ExitCode

from modulitiz_nano.files.ModuloFiles import ModuloFiles


class ModuleLint(object):
	MIN_CONFIDENCE=90
	
	@classmethod
	def findDeadCode(cls,pathDir:str)->bool:
		"""
		Returns true if there is at least 1 error or warning.
		"""
		highestExitCode=ExitCode.NoDeadCode
		for _percorsoRel,percorso,_dirs,filenames in ModuloFiles.walk(pathDir,(),(),None,None):
			for filename in filenames:
				if filename.endswith(".py"):
					exitCode=cls.__findDeadCode(os.path.join(percorso,filename))
					if exitCode > highestExitCode:
						highestExitCode = exitCode
		return highestExitCode!=ExitCode.NoDeadCode
	
	@classmethod
	def __findDeadCode(cls,pathFile: str)->ExitCode:
		v=vulture.Vulture(ignore_decorators=["@abstractmethod",])
		v.scavenge((pathFile,))
		return v.report(cls.MIN_CONFIDENCE)
