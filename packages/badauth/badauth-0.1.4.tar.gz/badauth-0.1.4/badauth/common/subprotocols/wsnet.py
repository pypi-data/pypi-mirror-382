from badauth.common.constants import asyauthSubProtocol
from badauth.common.subprotocols import SubProtocol


class SubProtocolWSNet(SubProtocol):
	def __init__(self):
		SubProtocol.__init__(self, asyauthSubProtocol.WSNET)

	@staticmethod
	def from_url_params(query_params = None):
		return SubProtocolWSNet()
