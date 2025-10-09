import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from redemais.api import RedeMaisApi

class TeleTriagem(RedeMaisApi):

	def gerar_sala_teleatendimento(self, cpf):
		if cpf is None:
			raise Exception('parameter [cpf] is required')

		logging.info('generating chat room...')
		endpoint_url = UrlUtil().make_url(self.base_url, ['teletriagem'])

		payload = {
			'idClienteContrato': self.id_contrato_plano,
			'idContratoPlano': self.id_contrato_plano,
			'cpf': str(cpf).zfill(11)
		}

		res = self.call_request(HTTPMethod.POST, endpoint_url, payload=payload)

		return jsonpickle.decode(res)

	def get_url_sala_teleatendimento(self, id_sala, url_callback):
		logging.info('get chat url by room id...')
		endpoint_url = UrlUtil().make_url(self.base_url, ['teletriagem'])

		params = {
			'idSala': id_sala
		}

		if not url_callback is None:
			params['callback'] = url_callback

		res = self.call_request(HTTPMethod.GET, endpoint_url, params=params)

		return jsonpickle.decode(res)