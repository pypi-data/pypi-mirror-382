import platform
from badauth.common.constants import asyauthSubProtocol
from badauth.common.subprotocols import SubProtocol


class SubProtocolSSPI(SubProtocol):
	def __init__(self):
		SubProtocol.__init__(self, asyauthSubProtocol.SSPI)
		if platform.system() != 'Windows':
			raise Exception("SSPI subprotocol only works on Windows!")

	@staticmethod
	def from_url_params(query_params = None):
		return SubProtocolSSPI()