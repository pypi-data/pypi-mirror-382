from modulitiz_nano.eccezioni.EccezioneBase import EccezioneBase


class ExceptionTooManyLogins(EccezioneBase):
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
