"""
Gerencia a carga dos dados de uma string com dados no formato JSON.
"""

import unicodedata
import pandas as pd
import json
from io import StringIO
from enum import Enum, auto

import blipy.erro as erro
from blipy.tabela_dataframe import TabelaDataFrame


# Tipos de formato do JSON
class TpJson(Enum):
    # dados no formato:
    #   [
    #     {
    #       "campo1": valor1,
    #       "campo2": valor2,
    #       ...
    #     },
    #     {
    #       "campo1": valor3,
    #       "campo2": valor4,
    #       ...
    #     }
    #   ]
    LIST = auto()

    # dados no formato:
    #   {
    #     "items": [
    #       {
    #         "campo1": valor1,
    #         "campo2": valor2,
    #         ...
    #       },
    #       {
    #         "campo1": valor3,
    #         "campo2": valor4,
    #         ...
    #       }
    #     ],
    #     <outros campos do json ... >
    #   }
    DICT = auto()

class JsonString(TabelaDataFrame):
    """
    String com dados no formato JSON a ser carregada no banco de dados.
    """

    # tratamento de erro
    e = erro.console

    def __init__(self, fonte_json):
        # nome da fonte de dados original do JSON, por exemplo a URL de onde o
        # JSON será baixado ou o nome do arquivo que contém o JSON que será
        # importado

        self._nome = fonte_json
        super().__init__()


    def carrega_dados(self, 
            json_str, tipo_json, campo_de_dados, dtype=None):
        """
        Lê uma string com dados no formato JSON e carrega em um Data Frame do
        Pandas.

        Referência: https://pandas.pydata.org/docs/reference/api/pandas.read_json.html

        Args:
        json_str:       uma string com dados no formato JSON
        tipo_json:      formato do JSON em str_json; um dos possíveis valores do
                        enum TpJson
        campo_de_dados: qual o campo do JSON que conterá a lista de valores a
                        serem lidos. Por exemplo, para um JSON no formato 
                            {
                              "items": [
                                {
                                  "campo1": valor1,
                                  "campo2": valor2,
                                  ...
                                },
                                {
                                  "campo1": valor3,
                                  "campo2": valor4,
                                  ...
                                }
                              ],
                              "hasMore": false
                            }
                        esse parâmetro deverá ser "items". Para
                        tipo_json=TpJson.LIST este parâmetro deve ser None
        dtype:          dict com os tipos das colunas do JSON, conforme 
                        parâmetro dtype do Pandas; Se None, os tipos serão
                        inferidos a partir dos dados lidos
        """

        if tipo_json == TpJson.LIST:
            if campo_de_dados is not None:
                self.e._("Para JSON do tipo LIST o parâmetro campo_de_dados "
                         "deve ser None.")
                raise RuntimeError
        elif tipo_json == TpJson.DICT:
            if campo_de_dados is None:
                self.e._("Para JSON do tipo DICT o parâmetro campo_de_dados "
                         "deve ser informado.")
                raise RuntimeError
        else:
            self.e._("Tipo de JSON inválido")
            raise RuntimeError

        # TODO: testar se num pandas > 1.1.5 isso ainda será necessário
        # usar orient='index' não funciona no read_json do pandas 1.1.5 quando 
        # os dados do json estão no formato de um dict, apesar da documentação
        # sugerir que sim (ver
        # https://stackoverflow.com/questions/76582964/pandas-from-dict-returns-typeerror).
        # Então a string com o json é convertida para um dict, a chave do dict
        # que contém os dados é extraída e os dados são convertidos de volta
        # para uma string para ser lida pelo pandas no read_json abaixo
        if tipo_json == TpJson.DICT:
            json_str = json.loads(json_str)
            json_str = json_str.get(campo_de_dados)
            json_str = json.dumps(json_str)

        try:
            self._dataframe = pd.read_json(
                StringIO(json_str),
                orient="records",
                dtype=dtype)
        except:
            self.e._("Erro ao carregar o JSON")
            raise

