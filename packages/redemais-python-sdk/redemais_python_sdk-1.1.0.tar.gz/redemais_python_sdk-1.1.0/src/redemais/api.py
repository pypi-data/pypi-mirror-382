import os, base64, logging
from fmconsult.http.api import ApiBase

class RedeMaisApi(ApiBase):

    def __init__(self):
        try:
            self.api_token          = os.environ['redemais.api.token']
            self.api_environment    = os.environ['redemais.api.environment']
            self.id_cliente         = os.environ['redemais.api.id_cliente']
            self.id_contrato_plano  = os.environ['redemais.api.id_contrato_plano']

            self.headers = {
                'x-api-key': self.api_token
            }

            url_endpoint = (lambda env: 'prd-v1' if env == 'live' else 'hml-v1' if env == 'sandbox' else None)(self.api_environment)

            self.base_url = f'https://ddt8urmaeb.execute-api.us-east-1.amazonaws.com/{url_endpoint}/rms1'
        except:
            raise