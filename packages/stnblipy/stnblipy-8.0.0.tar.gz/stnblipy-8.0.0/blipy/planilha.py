"""
Gerencia a carga dos dados de uma planilha do Excel.
"""

import pandas as pd

import blipy.erro as erro
from blipy.tabela_dataframe import TabelaDataFrame


class Planilha(TabelaDataFrame):
    """
    Planilha a ser carregada no banco de dados.
    """

    # tratamento de erro
    e = erro.console

    def carrega_dados(self, 
            arquivo, sheet_name=0, header=0, skipfooter=0, 
            names=None, index_col=None, usecols=None,
            skiprows=None, nrows=None, na_values=None, engine='openpyxl',
            thousands=None, dtype=None):
        """
        Lê uma aba de uma planilha de Excel e carrega em um Data Frame do
        Pandas.

        Referência: https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

        Args:
        arquivo:    caminho (path) do arquivo, com nome do arquivo incluso ou
                    uma URL
        sheet_name: aba ou guia do Excel, pode ser o nome ou número 0-indexed
        header:     linhas de cabeçalho a serem ignoradas, 0-indexed
        skipfooter: linhas de rodapé (final arquivo) a serem ignoradas,
                    0-indexed.
        names:      lista de nomes de colunas. Se arquivo não contém header,
                    deve-se obrigatoriamente setar header=None
        index_col:  coluna a ser usada como label das linhas
        usecols:    seleção de colunas. Tipos de seleção: 'A,B,C', [0,1,2],
                    ['ID','Coluna_1','Coluna_4']
        skiprows:   linhas a serem ignoradas no início do arquivo, 0-indexed
        nrows:      número de linhas a serem carregadas
        na_values:  lista de strings a serem consideradas como dados não
                    disponívels (NaN)
        engine:     o padrão é openpyxl. Existem outras para outros formatos,
                    por ex .odf
        thousands:  separador de milhar
        dtype:      dict com os tipos das colunas da planilha, conforme 
                    parâmetro dtype do Pandas
        """

        # Verificações de possíveis erros
        if arquivo is None:
            self.e._("O argumento 'arquivo' é o mínimo para funcionamento da função. \n"
                     "Este é o caminho (path) para a planilha com o nome do arquivo incluso ao final e com a extensão .xlsx ou .xls. \n"
                     "Formato esperado: C:/.../planilha.xlsx")
            raise RuntimeError

        if arquivo.endswith('.xlsx') and engine != 'openpyxl':
            self.e._("Parâmetro 'engine' não adequado para o tipo de arquivo.\n"
                     "O argumento 'arquivo' caminho (path) para a planilha deve terminar com: .xlsx ou .xls.\n"
                     "Para cada formato de arquivo existe uma engine adequada.\n"
                     "Engine 'openpyxl' para .xlsx e 'xlrd' para .xls.\n"
                     "Exemplos de parâmetro 'arquivo' esperados:\n"
                     "\tC:/.../planilha.xlsx\n"
                     "\tC:/.../planilha.xls\n")
            raise RuntimeError

        if arquivo.endswith('.xls') and engine != 'xlrd':
            self.e._("Parâmetro 'engine' não adequado para o tipo de arquivo.\n"
                     "O argumento 'arquivo' caminho (path) para a planilha deve terminar com: .xlsx ou .xls.\n"
                     "Para cada formato de arquivo existe uma engine adequada.\n"
                     "Engine 'openpyxl' para .xlsx e 'xlrd' para .xls.\n"
                     "Exemplos de parâmetro 'arquivo' esperados:\n"
                     "\tC:/.../planilha.xlsx\n"
                     "\tC:/.../planilha.xls\n")
            raise RuntimeError

        if not arquivo.endswith(('.xlsx','.xls')):
            self.e._("O argumento 'arquivo' caminho (path) para a planilha deve terminar com: .xlsx ou .xls.\n"
                     "Para cada formato de arquivo existe uma engine adequada.\n"
                     "Engine 'openpyxl' para .xlsx e 'xlrd' para .xls.\n"
                     "Exemplos de parâmetro 'arquivo' esperados:\n"
                     "\tC:/.../planilha.xlsx\n"
                     "\tC:/.../planilha.xls\n")
            raise RuntimeError

        # Carregamento da tabela para a memória
        try:
            self._dataframe = pd.read_excel(io=arquivo,sheet_name=sheet_name, 
                    header=header, skipfooter=skipfooter,
                    names=names, index_col=index_col, usecols=usecols, 
                    skiprows=skiprows, nrows=nrows, na_values=na_values, 
                    engine=engine, thousands=thousands, dtype=dtype)
        except FileNotFoundError:
            self.e._("Não foi possível abrir a planilha " + arquivo)
            raise

        self._nome = arquivo

