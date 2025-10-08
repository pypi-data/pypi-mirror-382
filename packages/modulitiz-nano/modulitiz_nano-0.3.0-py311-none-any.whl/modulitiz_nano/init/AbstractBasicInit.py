from abc import ABC
from abc import abstractmethod

from modulitiz_nano.init.AbstractInit import AbstractInit


class AbstractBasicInit(AbstractInit,ABC):
	@abstractmethod
	def getCartellaBase(self)->str:
		"""
		Ricavo la cartella dell'archivio del progetto attuale.
		"""
	
	@abstractmethod
	def getProjectRoot(self,_nome: str) -> str:
		"""
		Restituisce il percorso assoluto di un progetto.
		"""
	
	@abstractmethod
	def getProjectsRoot(self) -> str:
		"""
		Restituisce il percorso assoluto dei progetti.
		"""
