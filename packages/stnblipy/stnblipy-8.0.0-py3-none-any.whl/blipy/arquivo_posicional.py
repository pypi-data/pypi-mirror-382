"""
Gerencia a carga dos dados de um arquivo posicional.
"""

import pandas as pd

import blipy.erro as erro
from blipy.tabela_dataframe import TabelaDataFrame


class ArquivoPosicional(TabelaDataFrame):
    """
    Arquivo posicional a ser carregado no banco de dados.
    """

    # tratamento de erro
    e = erro.console

    def carrega_dados(self, 
            arquivo, 
            tam_colunas,
            header=None, 
            skipfooter=0,
            skiprows=None,
            nrows=None,
            usecols=None,
            encoding=None, 
            decimal=None,
            thousands=None,
            dtype=None):
        """
        Lê um arquivo posicional e carrega seus dados em um Data Frame do
        Pandas.

        Args:
        arquivo:        nome do arquivo, com seu path se for o caso
        tam_colunas:    lista de ints com o tamanho em caracteres de cada
                        coluna do arquivo
        header:         quantidade de linhas de cabeçalho no arquivo ou None se
                        não houver cabeçalho
        skipfooter:     linhas de rodapé a serem ignoradas, 0-indexed.
        skiprows:       linhas a serem ignoradas no início do arquivo, 0-indexed
        nrows:          número de linhas a serem carregadas
        usecols:        seleção de colunas. Tipos de seleção: 'A,B,C', [0,1,2],
                        ['ID','Coluna_1','Coluna_4']
        encoding:       string com o encoding do arquivo
        decimal:        separador de decimais
        thousands:      separador de milhar
        dtype:          dict com os tipos das colunas do CSV, conforme
                        parâmetro dtype do Pandas

        Referência: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_fwf.html
        """

        try:
            self._dataframe = pd.read_fwf(
                arquivo,
                widths=tam_colunas, 
                header=header,
                encoding=encoding, 
                decimal=decimal, 
                thousands=thousands,
                dtype=dtype,
                usecols=usecols,
                skipfooter=skipfooter,
                skiprows=skiprows,
                nrows=nrows)
        except FileNotFoundError:
            self.e._("Não foi possível abrir o arquivo " + arquivo + ".")
            raise

        self._nome = arquivo

