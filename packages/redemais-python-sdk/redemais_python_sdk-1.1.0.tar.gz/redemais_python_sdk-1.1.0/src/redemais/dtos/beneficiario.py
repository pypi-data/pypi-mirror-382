from dataclasses import dataclass, asdict
from typing import Optional
from fmconsult.utils.object import CustomObject

@dataclass
class Beneficiario(CustomObject):
    nome: str
    codigo_externo: str
    cpf: str
    data_nascimento: str
    sexo: str
    celular: str
    email: str
    cep: str
    endereco: str
    numero_endereco: str
    complemento_endereco: str
    bairro: str
    cidade: str
    uf: str
    cpf_titular: Optional[str] = None

    def to_dict(self):
        data = asdict(self)
        return data