
"""
Gerencia a carga dos dados de uma tabela do banco.
"""

# módulo usado para  implementar method overloading
# ATENÇÃO: este módulo *não é* thread safe
# (https://stackoverflow.com/questions/6434482/python-function-overloading)
# ATENÇÃO: métodos que usam o decorator dispatch e que contenham argumentos
# nomeados com valores default: se o valor default for alterado na chamada do
# método, precisa ser por meio de argumento nomeado, não pode se basear na
# posição do argumento
# (https://stackoverflow.com/questions/54132640/how-to-use-default-parameter-with-multipledispatch)
from multipledispatch import dispatch

import blipy.erro as erro


class TabelaEntrada():
    """
    Tabela a ser lida do banco de dados.
    """

    # tratamento de erro
    # este atributo é um atributo de classe, portanto pode ser alterado pora
    # todas as instâncias dessa classe, se se quiser um tipo de tratamento de
    # erro diferente de imprimir mensagem no console.
    # Para alterá-lo, usar sintaxe "TabelaEntrada.e = <novo valor>"
    e = erro.console

    def __init__(self, conexao_bd):
        """
        Args:
            conexao_bd  : conexão com o banco de dados
        """

        self.__sql          = ""
        self.__conexao_bd   = conexao_bd
        self.__cursor       = None
        self.__nome_tabela  = ""

    # getter; instancia.nome vai retornar __nome_tabela
    @property
    def nome(self):
        return self.__nome_tabela
    @nome.setter
    def nome(self, nome):
        raise NotImplementedError

    @dispatch(str)
    def carrega_dados(self, sql):
        """
        Carrega a tabela com os dados do banco.

        Args:
            sql : sql no banco cujo resultado será a tabela de entrada. Pode
                  ser apenas um filtro numa tabela ou mesmo joins entre tabelas
        Ret:
            um iterável com os registros da tabela do banco.
        """

        self.__sql = sql

        self.__cursor = None
        return self.__carrega_tabela()

    # como usa o decorator dispatch, o código que chama esse método tem que 
    # nomear o arqgumento 'esquema' se quiser alterá-lo
    # (https://stackoverflow.com/questions/54132640/how-to-use-default-parameter-with-multipledispatch)
    @dispatch(str, list, esquema=str)
    def carrega_dados(self, tabela, colunas, esquema="", filtro=""):
        """
        Carrega a tabela com os dados do banco.

        Args:
            tabela  : nome da tabela no banco
            colunas : lista com os nomes das colunas da tabela que ser quer
                      carregar
            esquema : nome do esquema
            filtro  : filtro opcional para ser aplicado na tabela, no formato
                      de uma cláusula WHERE de SQL, sem a palavra WHERE
        Ret:
            um iterável com os registros da tabela do banco.
        """

        self.__nome_tabela = tabela

        cols = ""
        for col in colunas:
            cols += col + ", "
        cols = cols[:len(cols)-2]

        if esquema != "":
            esquema += "."
        if filtro != "":
            filtro = " where " + filtro

        self.__sql = "select " + cols + " from " + esquema + tabela + filtro

        self.__cursor = None
        return self.__carrega_tabela()

    def recarrega_dados(self):
        """
        Rearrega a tabela com os dados do banco.

        Ret:
            um iterável com os registros da tabela do banco ou uma exceção
            se a tabela ainda não foi carregada.
        """

        if self.__sql == "":
            self.e._("A tabela não pode ser recarregada pois ainda não "
                     "foi carregada pela primeira vez.")
            raise RuntimeError

        self.__cursor = None
        return self.__carrega_tabela()

    def __carrega_tabela(self):
        """
        Carrega a tabela com os dados do banco.

        Ret:
            um iterável com os registros da tabela do banco.
        """

        if self.__cursor is None:
            self.__cursor = self.__conexao_bd.executa(self.__sql)

        for row in self.__cursor:
            # é necessário usar yield pois o cursor do sql não é exposto para
            # fora dessa classe, e le_prox_registro (que chama este método
            # aqui) deve ser chamado num loop no job de carga
            yield row

    def le_prox_registro(self):
        """
        Lê a próximo registro da tabela.

        Ret:
            tupla com o registro lido ou None se não houver mais registros a
            serem lidos.
        """

        registro = self.__carrega_tabela()
        try:
            ret = next(registro)
        except StopIteration:
            ret = None

        return ret

