import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from redemais.api import RedeMaisApi
from redemais.dtos.beneficiario import Beneficiario

class Beneficiarios(RedeMaisApi):
    
    def adesao(self, data:Beneficiario, id_tipo_plano: int):
        try:
            logging.info(f'add new person...')
            payload = {
                # informações do contrato
                "idCliente": int(self.id_cliente),
                "idClienteContrato": int(self.id_contrato_plano),
                "tipoPlano": id_tipo_plano,
                # dados pessoais
                "idBeneficiarioTipo": 1,
                "codigoExterno": data.codigo_externo,
                "cpf": data.cpf,
                "nome": data.nome,
                "dataNascimento": data.data_nascimento,
                "sexo": data.sexo,
                "email": data.email,
                "celular": data.celular,
                # endereço
                "cep": data.cep,
                "logradouro": data.endereco,
                "numero": data.numero_endereco,
                "complemento": data.complemento_endereco,
                "bairro": data.bairro,
                "cidade": data.cidade,
                "uf": data.uf
            }

            if not data.cpf_titular is None:
                payload['cpfTitular'] = data.cpf_titular
                
            endpoint_url = UrlUtil().make_url(self.base_url, ['adesao'])

            res = self.call_request(HTTPMethod.POST, endpoint_url, None, payload=payload)
            
            return jsonpickle.decode(res)
        except:
            raise

    def cancelamento(self, cpf):
        try:
            logging.info(f'remove person...')
            payload = {
                "idClienteContrato": int(self.id_contrato_plano),
                "idCliente": int(self.id_cliente),
                "cpf": cpf
            }

            endpoint_url = UrlUtil().make_url(self.base_url, ['cancelamento'])

            res = self.call_request(HTTPMethod.POST, endpoint_url, None, payload=payload)
            
            return jsonpickle.decode(res)
        except:
            raise
    
    def get_all(self, data_inicial, data_final, cpf, offset):
        logging.info('get beneficiaries...')
        endpoint_url = UrlUtil().make_url(self.base_url, ['beneficiarios'])

        params = {
            'idCliente': self.id_cliente,
            'idClienteContrato': self.id_contrato_plano,
            'dataInicial': data_inicial,
            'dataFinal': data_final,
            'cpf': cpf,
            'offset': offset
        }

        res = self.call_request(HTTPMethod.GET, endpoint_url, params=params)

        return jsonpickle.decode(res)