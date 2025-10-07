import os
import re
import socket
from contextlib import closing
from uuid import getnode

from _socket import gaierror

from modulitiz_nano.ModuloListe import ModuloListe
from modulitiz_nano.ModuloStringhe import ModuloStringhe
from modulitiz_nano.eccezioni.EccezioneRuntime import EccezioneRuntime
from modulitiz_nano.sistema.ModuloSystem import ModuloSystem


class ModuloNetworking(object):
	@staticmethod
	def getMacAddress()->str:
		mac=("%012X" % getnode())
		return mac

	@staticmethod
	def getLocalIp()->str|None:
		"""
		Returns private local IP address.
		"""
		sockObj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockObj.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		try:
			# doesn't even have to be reachable
			sockObj.connect(('255.255.255.255', 1))
			indirizzoIp = sockObj.getsockname()[0]
		except gaierror:
			indirizzoIp = None
		finally:
			sockObj.close()
		return indirizzoIp

	@staticmethod
	def isHttpPortOpen(host:str|None,port:int)->bool:
		# controllo host
		if host is None:
			host="127.0.0.1"
		# controllo porta
		with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
			if sock.connect_ex((host, port)) == 0:
				return True
		return False

	@staticmethod
	def checkPing(ipAddress:str)->bool:
		# build command
		cmd="ping "
		regexPercPacketsLost=r"(\d{1,3})\% "
		if ModuloSystem.isWindows():
			cmd+="-n"
			regexPercPacketsLost=r"\("+regexPercPacketsLost
		elif os.name=='posix':
			cmd+="-W 5 -c"
			regexPercPacketsLost=r", "+regexPercPacketsLost
		else:
			raise EccezioneRuntime("Tipologia del sistema operativo non riconosciuta: "+os.name)
		cmd+=" 1 "+ipAddress
		# execute command
		outputComando=ModuloStringhe.normalizzaEol(ModuloSystem.systemCallReturnOutput(cmd,None))
		rows=outputComando.split("\n")
		rows=ModuloListe.eliminaElementiVuoti(rows)
		for row in rows:
			if ModuloStringhe.contains(row, "%"):
				regexOutput=re.search(regexPercPacketsLost,row)
				if regexOutput is not None:
					return int(regexOutput.group(1).strip())==0
		return False
