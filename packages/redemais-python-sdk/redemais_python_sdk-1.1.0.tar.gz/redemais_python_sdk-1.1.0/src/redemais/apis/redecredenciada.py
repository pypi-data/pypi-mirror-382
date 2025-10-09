import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from redemais.api import RedeMaisApi

class RedeCredenciada(RedeMaisApi):
    
    def get_agendamentos(self, cpf):
        logging.info('get schedules...')
        endpoint_url = UrlUtil().make_url(self.base_url, ['rede-credenciada','agendamentos'])

        params = {
			'idContratoPlano': self.id_contrato_plano,
			'cpf': cpf
		}

        res = self.call_request(HTTPMethod.GET, endpoint_url, params=params)

        return jsonpickle.decode(res)

    def get_url_rede_credenciada(self, tipo_solicitacao, cpf):
        logging.info('get schedules...')
        endpoint_url = UrlUtil().make_url(self.base_url, ['rede-credenciada','url'])

        params = {
			'tipoSolicitacao': tipo_solicitacao,
			'idContratoPlano': self.id_contrato_plano,
			'cpf': cpf,
			'modoIframe': 1
		}

        res = self.call_request(HTTPMethod.GET, endpoint_url, params=params)

        return jsonpickle.decode(res)