"""
Métodos auxiliares para serem herdados por classes de entrada de dados que
utilizam um dataframe do pandas como forma de auxiliar a implementação.

Esse código não foi pensado para ser usado independentemente, mas apenas sendo
chamado por classes filhas.
"""

import pandas as pd

import blipy.erro as erro


# classe abstrata
# Todas as classes de entrada de dados que usem um dataframe pandas para
# facilitar suas implmentações herdarão desta classe aqui (por exemplo, as
# classes TabelaHTML e Planilha)
class TabelaDataFrame():
    """
    Classe auxiliar para classes de entrada de dados que utilizam um dataframe
    do pandas como forma de auxiliar a implementação.
    """

    # tratamento de erro
    e = erro.console

    def __init__(self):
        # atributos para ser herdado pelas classes filhas
        self._dataframe = None
        self._cursor = None

    def recarrega_dados(self):
        """
        Faz o reset do cursor para o ponto inicial do dataframe carregado.

        Uma exceção é disparada se o dataframe ainda não tiver sido carregado
        ao menos uma vez.
        """
        if self._dataframe is None:
            self.e._("O dataframe não pode ser recarregado pois ainda não "
                     "foi carregado pela primeira vez.\n"
                     "É necessário executar a função carrega_dados() primeiro.")
            raise RuntimeError

        # reset do cursor para o index 0
        self._cursor = None

    def le_prox_registro(self):
        """
        Lê a próximo registro do dataframe.

        Ret:
        Tupla com o registro lido ou None se não houver mais registros a serem
        lidos.
        """

        if self._cursor is None:
            self._cursor = self._dataframe.itertuples(index=False)

        try:
            registro = next(self._cursor)
            registro = tuple(registro)
        except StopIteration:
            registro = None

        return registro

    def formata_colunas(self, cols):
        """
        Altera a estrutura (colunas) do dataframe. Colunas podem ser suprimidas,
        duplicadas ou trocadas de ordem.

        Arg:
        cols:   lista com o índice (zero-based) das colunas finais do dataframe.
                Por exemplo, para duplicar a primeira coluna como última coluna
                num dataframe original de 3 colunas, esse parâmetro deve ser
                [0, 1, 2, 0]. 

                Pode haver uma lista dentro da lista, por exemplo
                [0, [1, 2], 0]. Neste caso, o data frame final terá 4 colunas:
                [0, 1, 2, 0]. Esta forma de lista dentro de lista não faz
                diferença aqui, mas é útil em outra parte do código do Blipy
                (na classe Job) quando mais de uma coluna de entrada é usada
                para calcular uma única coluna de saída.
        """

        df_original = self._dataframe.copy()
        df_original_cols = list(df_original.columns)
        self._dataframe = pd.DataFrame()

        i = 0
        for col in cols:
            if isinstance(col, list):
                for col1 in col:
                    self._dataframe.insert(
                            i, 
                            df_original_cols[col1], 
                            df_original[df_original_cols[col1]],
                            allow_duplicates=True)
                    i += 1
            else:
                self._dataframe.insert(
                        i, 
                        df_original_cols[col], 
                        df_original[df_original_cols[col]],
                        allow_duplicates=True)
                i += 1

    # self._nome deve ser preenchido pelas classes filhas
    @property
    def nome(self):
        return self._nome
    @nome.setter
    def nome(self, nome):
        raise NotImplementedError
