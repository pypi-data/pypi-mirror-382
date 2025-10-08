"""
Gerencia a carga dos dados de um arquivo CSV.
"""

import pandas as pd

import blipy.erro as erro
from blipy.tabela_dataframe import TabelaDataFrame


class ArquivoCSV(TabelaDataFrame):
    """
    Arquivo CSV a ser carregado no banco de dados.
    """

    # tratamento de erro
    e = erro.console

    def carrega_dados(self, 
            arquivo, header=0, skipfooter=0, 
            names=None, index_col=None, usecols=None,
            skiprows=None, nrows=None, na_values=None, engine=None,
            sep=";", decimal=".", thousands=None, 
            dtype=None, encoding=None):
        """
        Lê um arquivo CSV e carrega seus dados em um Data Frame do Pandas.

        Referência: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Args:
        arquivo:    caminho (path) do arquivo. Formato esperado: 
                    C:/.../arquivo.csv
        header:     linhas de cabeçalho a serem ignoradas, 0-indexed
        skipfooter: linhas de rodapé  a serem ignoradas, 0-indexed.
        names:      lista de nomes de colunas. Se arquivo não contém header,
                    deve-se obrigatoriamente setar header=None
        index_col:  coluna a ser usada como label das linhas
        usecols:    seleção de colunas. Tipos de seleção: 'A,B,C', [0,1,2],
                    ['ID','Coluna_1','Coluna_4']
        skiprows:   linhas a serem ignoradas no início do arquivo, 0-indexed
        nrows:      número de linhas a serem carregadas
        na_values:  lista de strings a serem consideradas como dados não
                    disponívels (NaN)
        engine:     engine a ser usado pelo Pandas.
        sep:        caractere separador das células
        decimal:    separador de decimais
        thousands:  separador de milhar
        dtype:      dict com os tipos das colunas do CSV, conforme parâmetro
                    dtype do Pandas
        encoding:   string com o encoding do arquivo csv
        """

        # Carregamento da tabela para a memória
        try:
            self._dataframe = pd.read_csv(arquivo,
                    header=header, skipfooter=skipfooter,
                    names=names, index_col=index_col, usecols=usecols, 
                    skiprows=skiprows, nrows=nrows, na_values=na_values, 
                    engine=engine, 
                    sep=sep, decimal=decimal, thousands=thousands, 
                    dtype=dtype,
                    encoding=encoding)
        except FileNotFoundError:
            self.e._("Não foi possível abrir o arquivo " + arquivo + ".")
            raise

        self._nome = arquivo

