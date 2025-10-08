import colorama
import webcolors


class ModuloColorText(object):
	"""
	Utility per gestire i colori e stampare a schermo testo colorato.
	"""
	
	DEFAULT=	'\033[0m'
	GRASSETTO=	DEFAULT+'\033[1m'
	NERO=		'\033[90m'
	ROSSO=		'\033[91m'
	VERDE=		'\033[92m'
	GIALLO=		'\033[93m'
	BLU=		'\033[94m'
	FUCSIA=		'\033[95m'
	AZZURRO=	'\033[96m'
	
	def __init__(self):
		colorama.init()
	
	@staticmethod
	def wordToRGB(word:str)->str|None:
		"""
		Translates color in RGB format.
		"""
		word=word.replace(" ","").replace("ish","")
		return webcolors.name_to_hex(word)
