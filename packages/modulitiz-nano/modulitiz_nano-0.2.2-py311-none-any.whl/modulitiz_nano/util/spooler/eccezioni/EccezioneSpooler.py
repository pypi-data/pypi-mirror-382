from modulitiz_nano.eccezioni.EccezioneBase import EccezioneBase


class EccezioneSpooler(EccezioneBase):
	
	def __init__(self,msg:str):
		super().__init__(msg)
