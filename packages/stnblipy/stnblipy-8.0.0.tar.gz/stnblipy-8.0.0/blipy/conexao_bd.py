
"""
Gerencia a conexão com um banco de dados.
"""

# TODO: colocar métodos num try. o catch desses try's vai ser feito nas funções que chamarem isso aqui, aqui vai tratar o erro e dar re-raise

import os
import json
import jpype

from sqlalchemy import create_engine, text
from jaydebeapi import connect as connect_jdv

import blipy.erro as erro


class ConexaoBD():
    """
    Conexão com o banco de dados.

    Qualquer falha na criação dessa conexão dispara uma exceção.
    """

    # tratamento de erro
    # este atributo é um atributo de classe, portanto pode ser alterado pora
    # todas as instâncias dessa classe, se se quiser um tipo de tratamento de
    # erro diferente de imprimir mensagem no console.
    # Para alterá-lo, usar sintaxe "ConexaoBD.e = <novo valor>"
    e = erro.console

    # controle para iniciar a JVM apenas uma vez para todas as instâncias,
    # quando usar conexões do tipo JDV
    __jvm_iniciada = False

    def __init__(self, 
            tipo, user, pwd,
            ip=None, port=None, service_name=None,
            class_path=None, params_jvm=None, jdbc_driver=None, jdbc_url=None, jar_file=None):
        """
        Este construtor não deve ser chamado diretamente, os objetos desta
        classe deverão ser instanciados através do método de classe from_json.
        """

        self.__conexao = None
        self.__tipo_conexao = tipo
        self.__usuario = user

        try:
            if tipo == "oracle":
                cstr = "oracle+oracledb://" +   user + ":" +                \
                                                pwd + "@" +                 \
                                                ip + ":" +                  \
                                                port + "/?service_name=" +  \
                                                service_name

                engine = create_engine( cstr, 
                                        thick_mode=None)

                self.__conexao = engine.connect()
                self.__conexao_raw_oracle = engine.raw_connection()

            elif tipo == "jdv":
                if not ConexaoBD.__jvm_iniciada:
                    jvm_path = jpype.getDefaultJVMPath()
                    jpype.addClassPath(class_path)
                    jpype.startJVM(jvm_path, params_jvm)
                    ConexaoBD.__jvm_iniciada = True

                self.__conexao = connect_jdv(
                        jdbc_driver, jdbc_url, [user, pwd], jar_file)
                
                self.__cursor_jdv = None

            else:
                raise Exception("Tipo de conexão inválido.")

        except Exception as err:
            self.e._(   "Erro ao conectar com o banco de dados."
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

    def __del__(self):
        if self.__conexao != None and \
           self.__tipo_conexao != "jdv":

            try:
                # só fecha a conexão explicitamente se não for JDV, pois se
                # for JDV, no momento em que este destrutor é chamado a JVM
                # já não está mais rodando e portanto fechar a conexão JDV
                # aqui geraria uma exceção
                self.__conexao.close()
            except Exception as err:
                self.e._(   "Erro ao fechar conexão com o banco de dados."
                            "\nDetalhes do erro:\n" + str(err))
                raise RuntimeError

    @classmethod
    def from_json(cls, conexoes=[]):
        """
        Constrói objetos de conexão com o banco a partir de um JSON de
        configuração que esteja no diretório onde o script está sendo
        executado e de uma variável de ambiente que contenha a(s) senha(s)
        do(s) esquema(s).

        O JSON se chamará 'conexoes_bd.json' e terá o seguinte formato:
        {
            "conexoes": [
                {
                    "ordem": <ordem>, 
                    "tipo": "oracle"
                    "user": "<usuário>", 
                    "pwd": "<nome da variável de ambiente com a senha>"
                    "ip": "<ip>", 
                    "port": "<número da porta>", 
                    "service_name": "<service_name>",
                },
                {
                    "ordem": <ordem>, 
                    "tipo": "jdv"
                    "user": "<usuário>", 
                    "pwd": "<nome da variável de ambiente com a senha>"
                    "class_path": <class path para instanciação da JVM>,
                    "params_jvm": <parâmetros adicionais da JVM>,
                    "jdbc_driver": <caminho e nome do arquivo do driver JDBC>,
                    "jdbc_url": <url do JDBC>,
                    "jar_file": <caminho e nome do arquivo jar do JDBC>
                },
                {
                 ....  outras conexões .....
                }
            ]
        }

        O campo ordem do JSON começa com 1. Não há limite no número de conexões
        possíveis.

        Os tipos de conexão podem ser "oracle" ou "jdv", cada qual com seus
        parâmetros de conexão específficos. Se não informado, considera-se o
        tipo "oracle".

        A senha de cada conexão será obtida da variável de ambiente cujo nome
        está indicado no parâmetro "pwd".

        Args:
        conexoes:   array de int com as conexões que serão consideradas
                    (campo 'ordem' do JSON); se não informado, todas as
                    conexões do JSON serão consideradas

        Ret:
        Uma tupla com um ou mais objetos de conexão com o banco de dados, na
        ordem especificada no parâmetro "conexoes" ou, se este não for
        informado, na ordem do campo "ordem" do JSON.
        """

        param_conexoes = [] 
        try:
            with open("conexoes_bd.json") as f:
                conexoes_json = json.load(f)

                if conexoes == []:
                    # simula um parâmetro "conexoes" de 1 a n, onde n é a
                    # quantidade de conexões do json de entrada
                    conexoes = [
                        x + 1 for x in range(len(conexoes_json["conexoes"]))]

                for conexao in conexoes:
                    achou = False

                    # varre o json para cada item do parâmetro conexoes
                    for conexao_json in conexoes_json["conexoes"]:
                        if conexao == conexao_json["ordem"]:
                            param_conexoes.append(conexao_json)
                            achou = True
                            break

                    if not achou:
                        cls.e._("Não foi possível achar a conexão " + 
                                str(conexao) + 
                                " no arquivo de conexões de banco de dados 'conexoes_bd.json'.")
                        raise RuntimeError

        except RuntimeError as err:
            raise err
        except Exception as err:
            cls.e._("Não foi possível ler o arquivo de conexões de banco de dados 'conexoes_bd.json'."
                    "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

        conexoes_ret = []
        for conexao in param_conexoes:
            falhou = False
            senha = None
            try:
                senha = os.getenv(conexao["pwd"])
            except KeyError:
                falhou = True

            if (senha is None) or falhou:
                cls.e._( "Não foi possível obter a senha do banco "
                                "de dados de uma variável de ambiente "
                                "para o usuário " + conexao["user"] + ".")
                raise RuntimeError

            try:
                tipo_conexao = conexao["tipo"]
            except KeyError:
                tipo_conexao = "oracle"

            try:
                if tipo_conexao == "oracle":
                    conexoes_ret.append(cls(tipo=tipo_conexao,
                                        user=conexao["user"], 
                                        pwd=senha,
                                        ip=conexao["ip"], 
                                        port=conexao["port"], 
                                        service_name=conexao["service_name"]))
                elif tipo_conexao == "jdv":
                    conexoes_ret.append(cls(tipo=tipo_conexao,
                                        user=conexao["user"], 
                                        pwd=senha,
                                        class_path=conexao["class_path"],
                                        params_jvm=conexao["params_jvm"],
                                        jdbc_driver=conexao["jdbc_driver"],
                                        jdbc_url=conexao["jdbc_url"],
                                        jar_file=conexao["jar_file"]))
                else:
                    cls.e._("Erro ao conectar com o banco de dados: " 
                            "\nParâmetro de conexao 'tipo' é inválido.")
                    raise RuntimeError

            except KeyError as err:
                cls.e._(    "Erro ao conectar com o banco de dados: " 
                            "\nParâmetro de conexao " + str(err) + 
                            " não encontrado.")
                raise RuntimeError
            except Exception as err:
                # tem que ter esse teste aqui pois o construtor já exibirá a
                # mensagem de erro caso haja algum problema com os parâmetros
                if str(err) != "":
                    cls.e._(    "Erro ao conectar com o banco de dados. " 
                                "\nDetalhes do erro:\n" + str(err))
                raise RuntimeError

        return tuple(conexoes_ret)

    @property
    def conexao(self):
        return self.__conexao

    @property
    def usuario(self):
        return self.__usuario

    def executa(self, sql, commit=False):
        """
        Executa um comando sql no banco. Apenas consultas são suportadas em uma
        conexão do tipo JDV.

        Args:
            sql     : sql a ser executado no banco
            commit  : flag indicativa se haverá um commit após a execução do
                      sql ou não 
        Ret:
            Cursor com o resultado do comando sql.
        """

        try:
            if self.__tipo_conexao == "jdv":
                if self.__cursor_jdv is not None:
                    # cursor já tinha sido usado antes (provavelmente é um 
                    # recarregamento dos dados)
                    self.__cursor_jdv.close()

                # apenas consultas são suportadas para o tipo de conexão JDV,
                # pois a conexão em si não executa um comando, mas apenas um
                # cursor dentro dela
                self.__cursor_jdv = self.__conexao.cursor() 
                self.__cursor_jdv.execute(sql)
                registros = self.__cursor_jdv.fetchall()

                # transforma o array de tuplas retornado pelo fetchall num
                # generator, para ter a mesma interface de uma retorno de uma
                # consulta quando feita pelo SQLAlchemy
                ret = (i for i in registros)
            else:
                if not commit:
                    ret = self.__conexao.execute(text(sql))
                else:
                    ret = self.__conexao.execute(text(sql))
                    self.__conexao.commit()
        except Exception as err:
            self.e._(   "Erro ao executar o seguinte comando no banco de "
                        "dados:\n" + sql + 
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

        return ret

    def commit(self):
        """
        Executa um commit no banco.
        """

        self.__conexao.commit()

    def insere_varios_registros(self, insert_stmt, registros):
        """
        Insere vários registros de uma só vez num banco de dados Oracle.
        Qualquer erro dispara uma exceção.

        Args:
        insert_stmt: comando sql de insert, no formato 
                     "insert into tabela (coluna1, coluna2, ...) values (:1, :2)"
        registros:   array de tuplas com os valores de cada registro a ser
                     inserido
        """

        try:
            cursor = self.__conexao_raw_oracle.cursor()
            cursor.executemany(insert_stmt, registros)
            self.__conexao_raw_oracle.commit()
        except Exception as err:
            self.e._(   "Erro ao executar o seguinte comando no banco de "
                        "dados:\n" + insert_stmt + 
                        "\nDetalhes do erro:\n" + str(err) + 
                        "\n\nRegistros que tentaram ser inseridos:\n" + 
                        str(registros))
            raise RuntimeError

    def data_hora_banco(self):
        """
        Retorna o dia e hora atuais do banco.
        """
        return self.executa("select sysdate from dual").first()[0]

    def tabela_existe(self, tabela):
        """
        Verifica se uma tabela existe no banco.

        Arg:
            tabela  : nome da tabela no banco
        Ret:
            True se tabela existe, False se não existe.
        """
        return self.__conexao.dialect.has_table(self.__conexao, tabela)

    def apaga_registros(self, tabela, condicao=None, commit=True):
        """
        Apaga registros de uma tabela no banco, de acordo com a condição
        informada.

        Args:
            tabela      : nome da tabela
            condicao    : condição WHERE da deleção; se não informado, apaga
                          todas as linhas da tabela
            commit      : flag indicativa se haverá um commit após a execução 
                          da deleção ou não 
        """
        if condicao is not None:
            condicao = " where " + condicao
        else:
            condicao = ""

        sql = "delete from " + tabela + condicao
        try:
            self.executa(sql, commit)
        except Exception as err:
            self.e._(   "Erro ao apagar registros do banco de dados." 
                        "O seguinte comando falhou:\n" + sql + 
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

    def trunca_tabela(self, tabela, commit=True):
        """
        Trunca uma tabela no banco.

        Args:
        tabela  : nome da tabela
        commit  : flag indicativa se haverá um commit após a execução 
                  da operação ou não 
        """
        sql = "truncate table " + tabela
        try:
            self.executa(sql, commit)
        except Exception as err:
            self.e._(   "Erro ao truncar uma tabela do banco de dados." 
                        "O seguinte comando falhou:\n" + sql + 
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

