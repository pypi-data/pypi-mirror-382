from abc import ABC
from abc import abstractmethod


class AbstractInit(ABC):
	@abstractmethod
	def getCartellaScriptCorrente(self)->str:
		"""
		Come recuperare la cartella dello script corrente.
		"""
