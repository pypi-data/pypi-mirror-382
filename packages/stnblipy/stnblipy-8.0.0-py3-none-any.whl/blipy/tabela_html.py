
"""
Gerencia a carga dos dados de uma tabela em HTML lida de uma URL.
"""

import pandas as pd
import blipy.erro as erro
from blipy.tabela_dataframe import TabelaDataFrame


class TabelaHTML(TabelaDataFrame):
    """
    Tabela a ser lida de uma página HTML.
    """

    # tratamento de erro
    e = erro.console

            # tipos_col,
        # tipos_col: array com os tipos das colunas da tabela
        #            lida
        # Ret:
        # Um iterável com os registros da tabela lida.
    def carrega_dados(self, 
            url,
            tabela=0,
            header=None,
            decimal=",", 
            thousands="."):
        """
        Carrega uma tabela em HTML a partir de uma URL.

        Args:
        url:        a URL de onde a tabela será lida
        tabela:     qual tabela será lida da URL, no caso de haver mais de uma
                    na mesma página. Zero-based
        header:     quantidade de cabeçalhos na tabela lida, ou None se não
                    houver cabeçalho
        decimal:    o indicador de separador decimal usado na tabela lida
        thousands:  o indicador de separador de milhar usado na tabela lida
        """

        self._dataframe = pd.read_html( 
                io=url, 
                decimal=decimal,
                thousands=thousands)

        self._dataframe = self._dataframe[tabela]
        if header is not None:
            for _ in range(header):
                self._dataframe.columns = self._dataframe.columns.droplevel()
 
        self._nome = url

