import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from redemais.api import RedeMaisApi

class DescontosMedicamentosFarmacias(RedeMaisApi):

	def get_url(self, cpf):
		logging.info('get discounts medicines & pharmacies url...')
		endpoint_url = UrlUtil().make_url(self.base_url, ['farmacia-medicamentos','url'])

		params = {
			'idClienteContrato': int(self.id_contrato_plano),
			'cpf': cpf
		}

		res = self.call_request(HTTPMethod.GET, endpoint_url, params=params)

		return jsonpickle.decode(res)