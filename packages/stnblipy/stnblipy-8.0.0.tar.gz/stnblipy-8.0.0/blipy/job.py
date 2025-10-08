
"""
Funções para facilitar a implementação de um ETL, subindo o nível de abstração
para um job de carga de dados.

Se parâmetro '-v' (de verbose) for passado na linha de comando ao executar o
script de carga, a quantidade de registros lidos e gravados será impressa no
console.
"""

import sys
import json
from datetime import datetime
from urllib.request import urlopen

import blipy.tabela_entrada as te
import blipy.tabela_saida as ts
import blipy.func_transformacao as ft

from enum import Enum, auto
from blipy.enum_tipo_col_bd import TpColBD as tp
from blipy.planilha import Planilha
from blipy.arquivo_csv import ArquivoCSV
from blipy.tabela_html import TabelaHTML
from blipy.jsonstring import JsonString
from blipy.arquivo_posicional import ArquivoPosicional


# Tipos de estratégias de gravação no banco
class TpEstrategia(Enum):
    # deleta todas as linhas da tabela antes de inserir as novas linhas
    DELETE = auto()    

    # simplesmente insere as novas linhas
    INSERT = auto()    

    # trunca a tabela antes de inserir as novas linhas
    TRUNCATE = auto()    


    # Quando a estratégia UPDATE_INSERT ou INSERT_UPDATE é utilizada, a técnica
    # de realizar várias gravações simultaneamente no banco (atributo
    # __qtd_insercoes_simultaneas de Job) é ignorada quando o registro é
    # atualizado (ou seja, sempre vai ser atualizado um registro de cada vez),
    # mas ainda é válida no caso das inserções

    # Primeiro tenta atualizar o registro, e se não conseguir, o insere.
    UPDATE_INSERT = auto()

    # Primeiro tenta inserir o registro, e se ele já existir, o atualiza.
    INSERT_UPDATE = auto()

    # Quando a estratégia UPDATE é utilizada, a técnica de realizar várias
    # gravações simultaneamente no banco (atributo __qtd_insercoes_simultaneas
    # de Job) não é utilizada, ou seja, a atualização é sempre feita um
    # registro por vez
    UPDATE = auto()

class Job():
    def __init__(self, nome_job):
        self.__verbose = True
        if len(sys.argv) > 1:
            if sys.argv[1] == "-s":
                self.__verbose = False
 
        self.__nome = nome_job
 
        print()
        print("====== Job " + self.__nome + " iniciado " + "=======")
        print("-----> Horário de início:  " +  \
                str(datetime.now().replace(microsecond=0)))

        # por padrão, vai usar o valor default de TabelaSaida
        self.__qtd_insercoes_simultaneas = None

        self.__reset_func_pre_pos_processamento()

    def __del__(self):
        print("====== Job " + self.__nome + " finalizado " + "=====")
        print("-----> Horário de término: " +  \
                str(datetime.now().replace(microsecond=0)))

    @property
    def qtd_insercoes_simultaneas(self):
        return self.__qtd_insercoes_simultaneas
    @qtd_insercoes_simultaneas.setter
    def qtd_insercoes_simultaneas(self, qtd_insercoes_simultaneas):
        self.__qtd_insercoes_simultaneas = qtd_insercoes_simultaneas

    def __reset_func_pre_pos_processamento(self):
        """
        Configura as funções de pré e pós processamento de cada registro para
        seus valores default, ou seja, retornam sempre True
        """
        self.__funcao_pre_processamento = lambda _: True
        self.__funcao_pos_processamento = lambda _, __: True

    def set_func_pre_processamento(self, funcao):
        """
        Seta a função que será chamada antes do processamento de cada linha dos
        dados de entrada. A função deverá ter como parâmetro uma tupla, que
        receberá o registro lido dos dados de entrada. Esta função deverá
        retornar True se o processamento do registro deve continuar ou False
        para pular esse registro e ir para o próximo registro de entrada.

        Ao final do processamento de carga de uma tabela, esta função é
        resetada para seu valor default, ou seja, retorna sempre True.
        """
        self.__funcao_pre_processamento = funcao

    def set_func_pos_processamento(self, funcao):
        """
        Seta a função que será chamada após o processamento de cada linha dos
        dados de entrada. A função deverá ter como parâmetros duas tuplas, uma 
        que receberá o registro original dos dados de entrada e outra que
        conterá o registro que foi efeitvamente gravado no banco, ou seja, após
        qualquer transformação porventura feita no dado de entrada. O retorno
        desta função atualmente é ignorado.

        Ao final do processamento de carga de uma tabela, esta função é
        resetada para seu valor default, ou seja, retorna sempre True.
        """
        self.__funcao_pos_processamento = funcao

    def grava_log_atualizacao(self, 
            conexao,
            tabela_log="LOG_ATUALIZACAO"):
        """
        Grava na tabela de log a data da última atualização dos dados. O nome
        da tabela de log é LOG_ATUALIZACAO por padrão, mas pode ser alterado. O
        nome do campo com a data da última atualização é sempre
        DT_ULT_ATUALIZACAO.

        Args:
        conexao:    conexão do esquema no banco onde está a tabela de log
        tabela_log: nome da tabela de log
        """

        ret = conexao.executa(
            "update " + tabela_log + 
            " set dt_ult_atualizacao = sysdate",
            commit=True)

        if ret.rowcount == 0:
            # é a primeira vez que o log é gravado, tanta então um insert
            conexao.executa(
                "insert into " + tabela_log + " (dt_ult_atualizacao)"
                "  values (sysdate)",
                commit=True)

    def importa_sql(self, 
            conn_entrada, 
            conn_saida, 
            sql_entrada,
            nome_tab_saida, 
            cols_saida, 
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação do resultado de uma consulta sql para o banco de dados. A
        tabela de destino por default é limpa e carregada de novo (considera-se
        que são poucas linhas), mas isso pode ser alterado pelo parâmetro
        "estrategia". Qualquer erro dispara uma exceção.

        Args:
        conn_entrada:       conexão com o esquema de entrada de dados
                            (geralmente o staging)
        conn_saida:         conexão com o esqumea de saída (geralmente a
                            produção)
        sql_entrada:        consulta sql que irá gerar os dados de entrada
        nome_tab_saida:     nome da tabela de saida
        cols_saida:         lista das colunas que serão gravadas na tabela de
                            saida, com o nome da coluna, seu tipo e a função de
                            transformanção a ser aplicada (função de
                            transformação é opcional; se não informado, faz só
                            uma cópia do dado)
        estrategia:         estratégia de gravação que será utilizada (enum
                            TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela. Esse parâmetro só faz
                            sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida
        """

        tab_entrada = te.TabelaEntrada(conn_entrada)
        tab_entrada.carrega_dados(sql_entrada)

        self.__grava_tabela(    tab_entrada, 
                                conn_saida, 
                                nome_tab_saida, 
                                cols_saida, 
                                estrategia, 
                                cols_chave_update)

    def importa_tabela_banco(self, 
            conn_entrada, 
            conn_saida, 
            nome_tab_entrada, 
            nome_tab_saida, 
            cols_entrada, 
            cols_saida,
            filtro_entrada="", 
            estrategia=TpEstrategia.DELETE, 
            cols_chave_update=None):
        """
        Importação de uma tabela de um banco de dados. A tabela de destino por
        default é limpa e carregada de novo (considera-se que são poucas
        linhas), mas isso pode ser alterado pelo parâmetro "estrategia".
        Qualquer erro dispara uma exceção.

        Args:
        conn_entrada:       conexão com o esquema de entrada de dados
                            (geralmente o staging)
        conn_saida:         conexão com o esqumea de saída (geralmente a
                            produção)
        nome_tab_entrada:   nome da tabela de entrada
        nome_tab_saida:     nome da tabela de saida
        cols_entrada:       lista dos nomes das colunas que serão buscadas na
                            tabela de entrada
        cols_saida:         lista das colunas que serão gravadas na tabela de
                            saida, com o nome da coluna, seu tipo e a função de
                            transformanção a ser aplicada (função de
                            transformação é opcional; se não informado, faz só
                            uma cópia do dado)
        filtro_entrada:     filtro opcional dos registros da tabela de entrada,
                            no formato de uma cláusula WHERE de SQL, sem a
                            palavra WHERE
        estrategia:         estratégia de gravação que será utilizada (enum
                            TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela. Esse parâmetro só faz
                            sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida

        Obs.:
        Para calcular o valor de saída baseado em mais de uma coluna de um
        mesmo registro da tabela de entrada, colocar as colunas numa lista
        dentro da lista cols_entrada. Por exemplo:

        cols_entrada = ["ID_CHAVE",
                        "QT_VALOR1",
                        "QT_VALOR2",
                        ["QT_VALOR1", "QT_VALOR2"]]
        cols_saida = [ ["ID_CHAVE", tp.NUMBER],
                       ["QT_VALOR1", tp.NUMBER],
                       ["QT_VALOR2", tp.NUMBER],
                       ["QT_SOMATORIO", tp.NUMBER, ft.Somatorio()]]

        QT_SOMATORIO na tabela de saída vai ser o resultado da aplicação de
        ft.Somatorio() nos valores das colunas QT_VALOR1 e QT_VALOR2 da tabela
        de entrada, registro a registro.
        """

        # salva no parâmetro que vai ser passsdo pra __grava_tabela quantas
        # colunas de entrada serão usadas no cálculo do valor de cada coluna de
        # saída, se for o caso de se usar a sintaxe "col1, col2, col_n" em
        # algum item de cols_entrada
        cols = []
        for i, col in enumerate(cols_entrada):
            if isinstance(col, list):
                for c in col:
                    cols.append(c)
                qtd_colunas = len(col)
                cols_saida[i].append(qtd_colunas)
            else:
                cols.append(col)
                qtd_colunas = 1

            if qtd_colunas > 1:
                cols_saida[i].append(qtd_colunas)

        tab_entrada = te.TabelaEntrada(conn_entrada)
        tab_entrada.carrega_dados(
                nome_tab_entrada, 
                cols, 
                filtro=filtro_entrada)

        self.__grava_tabela(    tab_entrada, 
                                conn_saida, 
                                nome_tab_saida, 
                                cols_saida, 
                                estrategia,
                                cols_chave_update)

    def importa_planilha(self, 
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            arquivo, 
            sheet=0, header=None, skipfooter=None, skiprows=None,
            qtd_linhas=None, cols=None, 
            na_values=None, 
            engine="openpyxl",
            uso_cols=None, 
            tp_cols_entrada=None,
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação de uma planilha para o banco de dados. Por default, a tabela
        de destino é limpa e carregada de novo (considera-se que são poucas
        linhas), mas isso pode ser alterado pelo parâmetro "estrategia".
        Qualquer erro dispara uma exceção.

        Args:
        conn_saida:     conexão com o esqumea de saída (geralmente a produção)
        nome_tab_saida: nome da tabela de saida
        cols_saida:     lista das colunas que serão gravadas na tabela de
                        saida, com o nome da coluna, seu tipo e a função de
                        transformanção a ser aplicada (funão de transformação é
                        opcional; se não informado, faz só uma cópia do dado)
        arquivo:        caminho (path) da planilha, com o nome da planilha
                        incluso ou uma URL
        sheet:          nome ou índice (0-based) da aba ou guia da planilha
        header:         quantidade de linhas de cabeçalho a serem ignoradas, ou
                        None se não houver cabeçalho
        skipfooter:     quantidade de linhas de rodapé a serem ignoradas ou
                        None para não ignorar nada. Se qtd_linhas for
                        informado, este parâmetro deve ser None
        skiprows:       quantidade de linhas a serem ignoradas no início do
                        arquivo ou None para não ignorar nada
        qtd_linhas:     número de linhas da planilha a serem carregadas ou None
                        para carregar todas as linhas
        cols:           seleção de colunas a serem carregadas a partir dos
                        dados de entrada ou None para carregar todas as
                        colunas. Tipos de seleção: 'A,B,C', [0,1,2],
                        ['ID','Coluna_1','Coluna_4']
        na_values:      lista de strings a serem consideradas como dados
                        não disponívels (NaN ou None)
        engine:         engine para o tipo de planilha que está sendo lida, por
                        padrão xlsx. Existem engines para outros formatos, por
                        exemplo para ODF (ver observação abaixo)
        uso_cols:       lista que indica como as colunas carregadas serão
                        utilizadas para calcular os dados de saida. Se None,
                        utiliza as colunas carregadas na ordem lida, uma a uma.
                        Esse parâmetro é importante quando se quer que:
                        1) uma única coluna carregada  
                        seja fonte de dados para mais de uma coluna de saída
                        (por exemplo, se a primeira
                        coluna carregada for fonte de dados para a primeira e
                        terceira colunas da tabela de saída, esse parâmetro
                        deve ser [0, 1, 0]) 
                        ou 
                        2) se quer que mais de uma coluna carregada seja
                        transformada em uma única coluna de saída. Neste caso,
                        esse parâmetro teria a forma de uma lista dentro da
                        lista, por exemplo [0, [1, 2], 3] indica que os dados
                        das colunas carregadas 1 e 2 vão ser transformados na
                        segunda coluna de saída e os dados carregados nas
                        colunas 0 e 3 serão fonte para a primeira e a terceira
                        colunas de saída, respectivamente
        tp_cols_entrada tipos das colunas de entrada, no formato de um array de
                        objetos TpColBD, na ordem das colunas lidas. Se None,
                        os tipos serão obtidos de cols_saida
        estrategia:     estratégia de gravação que será utilizada (enum
                        TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela de saída. Esse
                            parâmetro só faz sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida

        Obs.: o parâmetro engine é o mesmo do método read_excel do Pandas, ver
        https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        """

        # determina o tipo de cada coluna para a leitura do arquivo pelo pandas
        dtype = self.__monta_dtype(cols_saida, tp_cols_entrada)

        if header is not None:
            # no pandas, esse parâmetro é zero-based, não é a quantidade em si
            header -= 1

        if skipfooter is None:
            skipfooter = 0

        planilha = Planilha()
        planilha.carrega_dados(
            arquivo, 
            sheet_name=sheet, 
            header=header, 
            skipfooter=skipfooter, 
            skiprows=skiprows, 
            nrows=qtd_linhas, 
            usecols=cols,
            na_values=na_values,
            engine=engine, 
            dtype=dtype)

        self.__formata_dataframe(planilha, uso_cols, cols_saida)

        self.__grava_tabela(planilha, 
                            conn_saida, 
                            nome_tab_saida, 
                            cols_saida, 
                            estrategia,
                            cols_chave_update)

    def importa_arquivo_csv(self, 
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            arquivo, 
            header=None, skipfooter=None, skiprows=None, 
            qtd_linhas=None, cols=None,
            na_values=None,
            engine=None,
            sep=";", decimal=",", thousands=None,
            encoding="utf-8", 
            uso_cols=None, 
            tp_cols_entrada=None,
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação de um arquivo CSV para o banco de dados. Por default, a
        tabela de destino é limpa e carregada de novo (considera-se que são
        poucas linhas), mas isso pode ser alterado pelo parâmetro "estrategia".
        Qualquer erro dispara uma exceção.

        Args:
        conn_saida:     conexão com o esqumea de saída (geralmente a produção)
        nome_tab_saida: nome da tabela de saida
        cols_saida:     lista das colunas que serão gravadas na tabela de
                        saida, com o nome da coluna, seu tipo e a função de
                        transformanção a ser aplicada (funão de transformação é
                        opcional; se não informado, faz só uma cópia do dado)
        arquivo:        caminho (path) do arquivo csv
        header:         quantidade de linhas de cabeçalho a serem ignoradas, ou
                        None se não houver cabeçalho
        skipfooter:     quantidade de linhas de rodapé a serem ignoradas ou
                        None para não ignorar nada. Se qtd_linhas for
                        informado, este parâmetro deve ser None
        skiprows:       quantidade de linhas a serem ignoradas no início do
                        arquivo ou None para não ignorar nada
        qtd_linhas:     número de linhas do arquivo a serem carregadas ou None
                        para carregar todas as linhas
        cols:           seleção de colunas a serem carregadas a partir dos
                        dados de entrada ou None para carregar todas as
                        colunas. Tipos de seleção: 'A,B,C', [0,1,2],
                        ['ID','Coluna_1','Coluna_4']
        na_values:      lista de strings a serem consideradas como dados
                        não disponívels (NaN ou None)
        engine:         engine utilizada para ler o CSV. Se None, usa o padrão
                        do Pandas (ver observação abaixo sobre as engines do
                        Pandas)
        sep:            caractere separador dos campos
        decimal:        caractere separador de decimal
        thousands:      caractere separador de milhar
        encoding:       encoding do arquivo CSV
        uso_cols:       lista que indica como as colunas carregadas serão
                        utilizadas para calcular os dados de saida. Se None,
                        utiliza as colunas carregadas na ordem lida, uma a uma.
                        Esse parâmetro é importante quando se quer que:
                        1) uma única coluna carregada  
                        seja fonte de dados para mais de uma coluna de saída
                        (por exemplo, se a primeira
                        coluna carregada for fonte de dados para a primeira e
                        terceira colunas da tabela de saída, esse parâmetro
                        deve ser [0, 1, 0]) 
                        ou 
                        2) se quer que mais de uma coluna carregada seja
                        transformada em uma única coluna de saída. Neste caso,
                        esse parâmetro teria a forma de uma lista dentro da
                        lista, por exemplo [0, [1, 2], 3] indica que os dados
                        das colunas carregadas 1 e 2 vão ser transformados na
                        segunda coluna de saída e os dados carregados nas
                        colunas 0 e 3 serão fonte para a primeira e a terceira
                        colunas de saída, respectivamente
        tp_cols_entrada tipos das colunas de entrada, no formato de um array de
                        objetos TpColBD, na ordem das colunas lidas. Se None,
                        os tipos serão obtidos de cols_saida
        estrategia:     estratégia de gravação que será utilizada (enum
                        TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela de saída. Esse
                            parâmetro só faz sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida

        Obs.: o parâmetro engine é o mesmo do método read_csv do Pandas, ver
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        """

        # determina o tipo de cada coluna para a leitura do arquivo pelo pandas
        dtype = self.__monta_dtype(cols_saida, tp_cols_entrada)

        if header is not None:
            # no pandas, esse parâmetro é zero-based, não é a quantidade em si
            header -= 1

        if skipfooter is None:
            skipfooter = 0

        arq_csv = ArquivoCSV()
        arq_csv.carrega_dados(
            arquivo, 
            header=header, 
            skipfooter=skipfooter, 
            usecols=cols, 
            skiprows=skiprows,
            nrows=qtd_linhas, 
            na_values=na_values, 
            engine=engine,
            sep=sep, 
            decimal=decimal, 
            thousands=thousands, 
            dtype=dtype, 
            encoding=encoding)

        self.__formata_dataframe(arq_csv, uso_cols, cols_saida)

        self.__grava_tabela(arq_csv, 
                            conn_saida, 
                            nome_tab_saida, 
                            cols_saida, 
                            estrategia,
                            cols_chave_update)

    def importa_tabela_html(self, 
            conn_saida, 
            nome_tab_saida, 
            cols_saida,
            url,
            tabela=0,
            header=None,
            decimal=",", 
            thousands=".",
            uso_cols=None, 
            estrategia=TpEstrategia.DELETE):

        """
        Importação para o banco de dados de uma tabela em HTML disponível em
        uma URL. A tabela de destino por default é limpa e carregada de novo 
        (considera-se que são poucas linhas), mas isso pode ser alterado pelo
        parâmetro "estrategia". Qualquer erro dispara uma exceção.

        Args:
        conn_saida:     conexão com o esqumea de saída (geralmente a produção)
        nome_tab_saida: nome da tabela de saida
        cols_saida:     lista das colunas que serão gravadas na tabela de
                        saida, com o nome da coluna, seu tipo e a função de
                        transformanção a ser aplicada (funão de transformação é
                        opcional; se não informado, faz só uma cópia do dado)
        url:            a URL de onde a tabela html será lida
        tabela:         qual tabela será lida da URL, no caso de haver mais de
                        uma na mesma página. Zero-based
        header:         quantidade de cabeçalhos na tabela lida, ou None se não
                        houver cabeçalho
        decimal:        caractere separador de decimal
        thousands:      caractere separador de milhar
        uso_cols:       lista que indica como as colunas lidas serão utilizadas
                        para calcular os dados de saida. Se None, utiliza as
                        colunas na ordem lida. Esse parâmetro é importante
                        quando se quer que uma única coluna de entrada lida 
                        seja fonte de dados para mais de uma coluna de saída,
                        já que a relação entre cols_saida e as colunas lidas
                        tem que ser de 1 para 1. Por exemplo, se a primeira
                        coluna lida lida for fonte de dados para a primeira e
                        terceira colunas da tabela de saída, esse parâmetro
                        deve ser [0, 1, 0]
        estrategia:     estratégia de gravação que será utilizada (enum
                        TpEstrategia)
        """

        tabela_entrada = TabelaHTML()
        tabela_entrada.carrega_dados(url, 
            tabela=tabela, header=header, decimal=decimal, thousands=thousands)

        self.__formata_dataframe(tabela_entrada, uso_cols, cols_saida)

        self.__grava_tabela(tabela_entrada, 
                            conn_saida, 
                            nome_tab_saida, 
                            cols_saida, 
                            estrategia)

    def importa_json_url(self,
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            url_json, 
            tipo_json, 
            campo_de_dados=None,
            uso_cols=None, 
            tp_cols_entrada=None,
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação de um JSON que, para uma determinada chave, contenha um
        conjunto de itens de igual formato. O JSON será lido de uma URL. A
        tabela de destino por default é limpa e carregada novamente, mas isso
        pode ser alterado pelo parâmetro "estrategia". Qualquer erro dispara
        uma exceção.

        Args:
        conn_saida:         conexão com o esqumea de saída (geralmente a
                            produção)
        nome_tab_saida:     nome da tabela de saida
        cols_saida:         lista das colunas que serão gravadas na tabela de
                            saida, com o nome da coluna, seu tipo e a função de
                            transformanção a ser aplicada (funão de
                            transformação é opcional; se não informado, faz só
                            uma cópia do dado)
        url_json:           string com a url de onde buscar o JSON a ser
                            importado
        tipo_json:          formato do JSON de entrada (enum TpJson)
        campo_de_dados:     qual o campo do JSON que conterá a lista de valores
                            a serem lidos. Por exemplo, para um JSON no formato 
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
        uso_cols:           lista que indica como as colunas carregadas serão
                            utilizadas para calcular os dados de saida. Se None,
                            utiliza as colunas carregadas na ordem lida, uma a
                            uma. Esse parâmetro é importante quando se quer
                            que:
                            1) uma única coluna carregada seja fonte de dados
                            para mais de uma coluna de saída (por exemplo, se a
                            primeira coluna carregada for fonte de dados para a
                            primeira e terceira colunas da tabela de saída,
                            esse parâmetro deve ser [0, 1, 0]) 
                            ou 
                            2) se quer que mais de uma coluna carregada seja
                            transformada em uma única coluna de saída. Neste
                            caso, esse parâmetro teria a forma de uma lista
                            dentro da lista, por exemplo [0, [1, 2], 3] indica
                            que os dados das colunas carregadas 1 e 2 vão ser
                            transformados na segunda coluna de saída e os dados
                            carregados nas colunas 0 e 3 serão fonte para a
                            primeira e a terceira colunas de saída,
                            respectivamente
        tp_cols_entrada     tipos das colunas de entrada, no formato de um
                            array de objetos TpColBD, na ordem das colunas
                            lidas. Se None, os tipos serão obtidos de
                            cols_saida
        estrategia:         estratégia de gravação que será utilizada (enum
                            TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela de saída. Esse
                            parâmetro só faz sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida
        """

        response = urlopen(url_json)

        # converte json lido para uma string.
        # ensure_ascii=False garante que os caracteres acentuados serão
        # lidos corretamente
        str_json = json.dumps(json.loads(response.read()), ensure_ascii=False)

        self.__importa_json(
            url_json,
            conn_saida,
            nome_tab_saida,
            cols_saida,
            str_json,
            tipo_json,
            campo_de_dados,
            uso_cols,
            tp_cols_entrada,
            estrategia,
            cols_chave_update)

    def importa_json_str(self,
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            str_json, 
            tipo_json, 
            campo_de_dados=None,
            uso_cols=None, 
            tp_cols_entrada=None,
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação de uma string contendo um JSON que, para uma determinada
        chave, contenha um conjunto de itens de igual formato. A tabela de
        destino por default é limpa e carregada novamente, mas isso pode ser
        alterado pelo parâmetro "estrategia". Qualquer erro dispara uma
        exceção.

        Args:
        conn_saida:         conexão com o esqumea de saída (geralmente a
                            produção)
        nome_tab_saida:     nome da tabela de saida
        cols_saida:         lista das colunas que serão gravadas na tabela de
                            saida, com o nome da coluna, seu tipo e a função de
                            transformanção a ser aplicada (funão de
                            transformação é opcional; se não informado, faz só
                            uma cópia do dado)
        str_json:           string com o JSON a ser importado
        tipo_json:          formato do JSON de entrada (enum TpJson)
        campo_de_dados:     qual o campo do JSON que conterá a lista de valores
                            a serem lidos. Por exemplo, para um JSON no formato 
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
        uso_cols:           lista que indica como as colunas carregadas serão
                            utilizadas para calcular os dados de saida. Se None,
                            utiliza as colunas carregadas na ordem lida, uma a
                            uma. Esse parâmetro é importante quando se quer
                            que:
                            1) uma única coluna carregada seja fonte de dados
                            para mais de uma coluna de saída (por exemplo, se a
                            primeira coluna carregada for fonte de dados para a
                            primeira e terceira colunas da tabela de saída,
                            esse parâmetro deve ser [0, 1, 0]) 
                            ou 
                            2) se quer que mais de uma coluna carregada seja
                            transformada em uma única coluna de saída. Neste
                            caso, esse parâmetro teria a forma de uma lista
                            dentro da lista, por exemplo [0, [1, 2], 3] indica
                            que os dados das colunas carregadas 1 e 2 vão ser
                            transformados na segunda coluna de saída e os dados
                            carregados nas colunas 0 e 3 serão fonte para a
                            primeira e a terceira colunas de saída,
                            respectivamente
        tp_cols_entrada:    tipos das colunas de entrada, no formato de um
                            array de objetos TpColBD, na ordem das colunas
                            lidas. Se None, os tipos serão obtidos de
                            cols_saida
        estrategia:         estratégia de gravação que será utilizada (enum
                            TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela de saída. Esse
                            parâmetro só faz sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida
        """

        self.__importa_json(
            "String JSON",
            conn_saida,
            nome_tab_saida,
            cols_saida,
            str_json,
            tipo_json,
            campo_de_dados,
            uso_cols,
            tp_cols_entrada,
            estrategia,
            cols_chave_update)

    def importa_json_arquivo(self,
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            arquivo_json, 
            tipo_json, 
            campo_de_dados=None,
            encoding="utf-8",
            uso_cols=None, 
            tp_cols_entrada=None,
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação de um JSON que, para uma determinada chave, contenha um
        conjunto de itens de igual formato. O JSON será lido de um arquivo. A
        tabela de destino por default é limpa e carregada novamente, mas isso
        pode ser alterado pelo parâmetro "estrategia". Qualquer erro dispara
        uma exceção.

        Args:
        conn_saida:         conexão com o esqumea de saída (geralmente a
                            produção)
        nome_tab_saida:     nome da tabela de saida
        cols_saida:         lista das colunas que serão gravadas na tabela de
                            saida, com o nome da coluna, seu tipo e a função de
                            transformanção a ser aplicada (funão de
                            transformação é opcional; se não informado, faz só
                            uma cópia do dado)
        arquivo_json:       string com o nome do arquivo que contém o JSON a
                            ser importado
        tipo_json:          formato do JSON de entrada (enum TpJson)
        campo_de_dados:     qual o campo do JSON que conterá a lista de valores
                            a serem lidos. Por exemplo, para um JSON no formato 
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
        encoding:           o encoding do arquivo. Se não informado,
                            considera-se utf-8
        uso_cols:           lista que indica como as colunas carregadas serão
                            utilizadas para calcular os dados de saida. Se None,
                            utiliza as colunas carregadas na ordem lida, uma a
                            uma. Esse parâmetro é importante quando se quer
                            que:
                            1) uma única coluna carregada seja fonte de dados
                            para mais de uma coluna de saída (por exemplo, se a
                            primeira coluna carregada for fonte de dados para a
                            primeira e terceira colunas da tabela de saída,
                            esse parâmetro deve ser [0, 1, 0]) 
                            ou 
                            2) se quer que mais de uma coluna carregada seja
                            transformada em uma única coluna de saída. Neste
                            caso, esse parâmetro teria a forma de uma lista
                            dentro da lista, por exemplo [0, [1, 2], 3] indica
                            que os dados das colunas carregadas 1 e 2 vão ser
                            transformados na segunda coluna de saída e os dados
                            carregados nas colunas 0 e 3 serão fonte para a
                            primeira e a terceira colunas de saída,
                            respectivamente
        tp_cols_entrada     tipos das colunas de entrada, no formato de um
                            array de objetos TpColBD, na ordem das colunas
                            lidas. Se None, os tipos serão obtidos de
                            cols_saida
        estrategia:         estratégia de gravação que será utilizada (enum
                            TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela de saída. Esse
                            parâmetro só faz sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida
        """

        with open(arquivo_json, encoding=encoding) as f:
            # converte json lido para uma string.
            # ensure_ascii=False garante que os caracteres acentuados serão
            # lidos corretamente
            str_json = json.dumps(json.load(f), ensure_ascii=False)

        self.__importa_json(
            arquivo_json,
            conn_saida,
            nome_tab_saida,
            cols_saida,
            str_json,
            tipo_json,
            campo_de_dados,
            uso_cols,
            tp_cols_entrada,
            estrategia,
            cols_chave_update)

    def __importa_json( self,
            fonte_json,
            conn_saida,
            nome_tab_saida,
            cols_saida,
            str_json,
            tipo_json,
            campo_de_dados,
            uso_cols,
            tp_cols_entrada,
            estrategia,
            cols_chave_update):

        # determina o tipo de cada coluna para a leitura do json pelo pandas
        dtype = self.__monta_dtype(cols_saida, tp_cols_entrada)

        dados_json = JsonString(fonte_json)
        dados_json.carrega_dados(str_json, tipo_json, campo_de_dados, dtype)

        self.__formata_dataframe(dados_json, uso_cols, cols_saida)

        self.__grava_tabela(dados_json, 
                            conn_saida, 
                            nome_tab_saida, 
                            cols_saida, 
                            estrategia,
                            cols_chave_update)

    def importa_valores(self, 
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            dados_entrada,
            estrategia=TpEstrategia.DELETE):
    
        """
        Salva um conjunto de valores numa tabela do banco. Esses valores estão
        na forma de uma lista de tuplas, cada tupla sendo um registro a ser
        gravado.

        Args:
        conn_saida:     conexão com o esqumea de saída (geralmente a produção)
        nome_tab_saida: nome da tabela de saida
        cols_saida:     lista com o nome das colunas na tabela de saída e seus
                        tipos, conforme os tipos definidos em TpColBD, por
                        exemplo:
                        cols_saida = [["ID_GRUPO_FONTE", tp.NUMBER],
                                      ["NO_GRUPO_FONTE", tp.STRING]]
        dados_entrada:  lista de tuplas com os valores a serem gravados no
                        banco, por exemplo:
                        dados_entrada = [
                            (1, "Recursos do Tesouro-Exercício Corrente"), 
                            (2, "Recursos de Outras Fontes-Exercício Corrente")]
        estrategia:     estratégia de gravação que será utilizada (enum
                        TpEstrategia)
        """

        # monta as colunas de saída
        col = {}
        for i, _ in enumerate(cols_saida):
            col[cols_saida[i][0]] =    \
                ts.Coluna(cols_saida[i][0], cols_saida[i][1], ft.f_copia)

        # configura a tabela de saída
        tabela_saida = ts.TabelaSaida(nome_tab_saida, col, conn_saida)

        if estrategia == TpEstrategia.DELETE:
            conn_saida.apaga_registros(nome_tab_saida)
        elif estrategia == TpEstrategia.TRUNCATE:
            conn_saida.trunca_tabela(nome_tab_saida)
        elif estrategia == TpEstrategia.INSERT:
            pass

        # estrategias UPDATE_INSERT, INSERT_UPDATE ou UPDATE não fazem muito
        # sentido aqui, pois a ideia desse método é inserir poucas linhas
        # em tabelas de domínio, então quando se quiser atualizar algum
        # valor é mais prático limpar tudo e carregar novamente (estratégias
        # DELETE ou TRUNCATE)
        elif estrategia == TpEstrategia.UPDATE_INSERT:
            raise NotImplementedError
        elif estrategia == TpEstrategia.INSERT_UPDATE:
            raise NotImplementedError
        elif estrategia == TpEstrategia.UPDATE:
            raise NotImplementedError

        else:
            raise NotImplementedError

        # loop de leitura e gravação dos dados
        qtd_registros = 0
        for r in dados_entrada:
            for i, c in enumerate(cols_saida):
                tabela_saida.col[c[0]].calcula_valor( (r[i],) )

            tabela_saida.insere_registro()
            qtd_registros += 1

        if self.__verbose:
            print(  str(qtd_registros) +  \
                    " \tregistros salvos na tabela " +  \
                    nome_tab_saida)

    def importa_arquivo_posicional(self, 
            conn_saida, 
            nome_tab_saida, 
            cols_saida, 
            arquivo, 
            tam_colunas,
            header=None, skipfooter=None, skiprows=None, 
            qtd_linhas=None, cols=None,
            decimal=",", thousands=None,
            encoding="utf-8",
            uso_cols=None, 
            tp_cols_entrada=None,
            estrategia=TpEstrategia.DELETE,
            cols_chave_update=None):
        """
        Importação de um arquivo posicional para o banco de dados. A tabela
        de destino por default é limpa e carregada de novo (considera-se
        que são poucas linhas), mas isso pode ser alterado pelo parâmetro
        "estrategia". Qualquer erro dispara uma exceção.

        Obs.: não pode haver um <enter> no meio de um dos campos de dados (por
        exemplo, um campo "descrição" com um texto quebrado em várias linhas),
        pois o <enter> é considerado como o finalizador de uma linha de dados.

        Args:
        conn_saida:     conexão com o esqumea de saída
        nome_tab_saida: nome da tabela de saida
        cols_saida:     lista das colunas que serão gravadas na tabela de
                        saida, com o nome da coluna, seu tipo e a função de
                        transformanção a ser aplicada (funão de transformação é
                        opcional; se não informado, faz só uma cópia do dado)
        arquivo:        nome do arquivo, com seu path se for o caso
        tam_colunas:    lista de ints com o tamanho em caracteres de cada
                        coluna do arquivo. 
                        Obs.: o tamanho informado é em caracteres mesmo e não
                        bytes, então por exemplo um caracter acentuado numa
                        coluna ocupará dois bytes num arquivo com encoding
                        utf-8, mas contará apenas um caracter para fins desse
                        parâmetro
        header:         quantidade de linhas de cabeçalho a serem ignoradas, ou
                        None se não houver cabeçalho
        skipfooter:     quantidade de linhas de rodapé a serem ignoradas ou
                        None para não ignorar nada. Se qtd_linhas for
                        informado, este parâmetro deve ser None
        skiprows:       quantidade de linhas a serem ignoradas no início do
                        arquivo ou None para não ignorar nada
        qtd_linhas:     número de linhas do arquivo a serem carregadas ou None
                        para carregar todas as linhas
        cols:           seleção de colunas a serem carregadas a partir dos
                        dados de entrada ou None para carregar todas as
                        colunas. Tipos de seleção: 'A,B,C', [0,1,2],
                        ['ID','Coluna_1','Coluna_4']
        decimal:        caractere separador de decimal
        thousands:      caractere separador de milhar
        encoding:       encoding do arquivo CSV
        uso_cols:       lista que indica como as colunas carregadas serão
                        utilizadas para calcular os dados de saida. Se None,
                        utiliza as colunas carregadas na ordem lida, uma a uma.
                        Esse parâmetro é importante quando se quer que:
                        1) uma única coluna carregada  
                        seja fonte de dados para mais de uma coluna de saída
                        (por exemplo, se a primeira
                        coluna carregada for fonte de dados para a primeira e
                        terceira colunas da tabela de saída, esse parâmetro
                        deve ser [0, 1, 0]) 
                        ou 
                        2) se quer que mais de uma coluna carregada seja
                        transformada em uma única coluna de saída. Neste caso,
                        esse parâmetro teria a forma de uma lista dentro da
                        lista, por exemplo [0, [1, 2], 3] indica que os dados
                        das colunas carregadas 1 e 2 vão ser transformados na
                        segunda coluna de saída e os dados carregados nas
                        colunas 0 e 3 serão fonte para a primeira e a terceira
                        colunas de saída, respectivamente
        tp_cols_entrada tipos das colunas de entrada, no formato de um array de
                        objetos TpColBD, na ordem das colunas lidas. Se None,
                        os tipos serão obtidos de cols_saida
        estrategia:     estratégia de gravação que será utilizada (enum
                        TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão chave de
                            um eventual update na tabela. Esse parâmetro só faz
                            sentido para se parâmetro
                            estrategia=TpEstrategia.UPDATE_INSERT ou
                            INSERT_UPDATE ou UPDATE e é obrigatório nestes
                            casos. Essas colunas também têm que fazer parte do
                            parâmetro cols_saida
        """

        # determina o tipo de cada coluna para a leitura do json pelo pandas
        dtype = self.__monta_dtype(cols_saida, tp_cols_entrada)

        if header is not None:
            # no pandas, esse parâmetro é zero-based, não é a quantidade em si
            header -= 1

        if skipfooter is None:
            skipfooter = 0

        arq_posicional = ArquivoPosicional()
        arq_posicional.carrega_dados(
            arquivo, 
            tam_colunas, 
            header=header, 
            skipfooter=skipfooter,
            skiprows=skiprows,
            nrows=qtd_linhas,
            usecols=cols,
            encoding=encoding, 
            decimal=decimal,
            thousands=thousands,
            dtype=dtype)

        self.__formata_dataframe(arq_posicional, uso_cols, cols_saida)

        self.__grava_tabela(arq_posicional, 
                            conn_saida, 
                            nome_tab_saida, 
                            cols_saida, 
                            estrategia,
                            cols_chave_update)

    def copia_tabelas(self,
            conn_entrada,
            conn_saida,
            tabelas,
            prefixo_tabelas_entrada="",
            prefixo_tabelas_saida="",
            sufixo_tabelas_entrada="",
            sufixo_tabelas_saida="",
            estrategia=TpEstrategia.DELETE):

        """
        Copia tabelas de um esquema para outro, sem transformação de dados. As
        colunas das tabelas devem ter o mesmo tipo e nome. Os nomes das tabelas
        informados no parâmetro deste método podem variar por um sufixo ou
        prefixo em relação à tabela no banco de dados, por exemplo um parâmetro
        "USUARIO" pode corresponder a uma tabela de entrada MVW_USUARIO e uma
        tabela de saída DIM_USUARIO.

        Apenas tabelas em bancos Oracle são suportadas, pois esse método busca
        os metadados das tabelas no dicionário de dados do Oracle.

        Args:
        conn_entrada:   conexão com o esqumea de entrada (geralmente o staging)
        conn_saida:     conexão com o esqumea de saída (geralmente a produção)
        tabelas:        lista com os nomes das tabelas a serem copiadas; ver
                        abaixo detalhes da formatação desta lista
        prefixo_tabelas_entrada:    prefixo que será adicionado aos nomes das
                                    tabelas de entrada
        prefixo_tabelas_saida:      prefixo que será adicionado aos nomes das
                                    tabelas de saida
        sufixo_tabelas_entrada:     sufixo que será adicionado aos nomes das
                                    tabelas de entrada
        sufixo_tabelas_saida:       sufixo que será adicionado aos nomes das
                                    tabelas de saida
        estrategia:     estratégia de gravação que será utilizada (enum
                        TpEstrategia)

        Cada item do parâmetro "tabelas" pode ser apenas o nome da tabela (sem
        prefixo ou sufixo) ou uma outra lista, onde o primeiro elemento é o
        nome da tabela e os demais são os nomes das colunas que serão copiadas. 

        Por exemplo:
        tabelas = ["TABELA1", "TABELA2", ["TABELA3", "COL1", "COL2"]]

        Neste caso, de TABELA1 e TABELA2 serão copiados todos os campos e de
        TABELA3 serão copiados apenas os campos COL1 e COL2.

        Apenas são suportados os tipos de colunas NUMBER, VARCHAR2, CHAR e DATE.

        Os campos do tipo BLOB ou CLOB são sempre ignorados.
        """

        for t in tabelas:
            if type(t) is list:
                tabela = t[0]
                cols_entrada = t[1:]
                cols_informado = True
            else:
                tabela = t
                cols_entrada = []
                cols_informado = False

            # tem que setar essas variáveis em duas etapas, pois o python não
            # permitiu prefixo + str + sufixo numa mesma sentença
            tabela_in = prefixo_tabelas_entrada + tabela 
            tabela_in += sufixo_tabelas_entrada
            tabela_out = prefixo_tabelas_saida + tabela 
            tabela_out += sufixo_tabelas_saida

            cursor = conn_saida.executa(f"""
                select column_name, data_type
                from all_tab_columns
                where owner = {conn_saida.usuario!r}
                and table_name = {tabela_out!r}
                order by column_id
            """)

            indice = -1
            tipos_cols = []
            while True:
                try:
                    reg = next(cursor)
                    if reg[1] in ["BLOB", "CLOB"]:
                        continue

                    if cols_informado:
                        achou = False
                        for i in range(len(cols_entrada)):
                            if cols_entrada[i] == reg[0]:
                                # as colunas já são informadas na chamada do
                                # método, indice é usado apenas para montar a
                                # lista com o tipo de cada coluna, pois a ordem
                                # em que as colunas foram informadas não
                                # necessariamente é a mesma ordem da consulta
                                # ao dicionário de dados do banco
                                indice = i
                                achou = True
                                break

                        if not achou:
                            # esta coluna não está entre as colunas informadas,
                            # vai para o próximo registro com a coluna seguinte
                            continue # while
                    else:
                        cols_entrada.append(reg[0])
                        indice += 1

                    while indice >= len(tipos_cols):
                        # se necessário, vai aumentando a lista com qualquer
                        # valor apenas para alocar o espaço, depois ela será
                        # alterada abaixo com o valor real
                        tipos_cols.append(tp.NUMBER)

                    if reg[1] == "NUMBER":
                        tipos_cols[indice] = tp.NUMBER
                    elif reg[1] in ["VARCHAR2", "CHAR"]:
                        tipos_cols[indice] = tp.STRING
                    elif reg[1] == "DATE":
                        tipos_cols[indice] = tp.DATE
                    else:
                        raise NotImplementedError(
                            "Tipo de coluna não suportado: " + reg[1])

                except StopIteration:
                    break

            cols_saida = []
            for i in range(len(tipos_cols)):
                cols_saida.append([cols_entrada[i], tipos_cols[i]])

            self.importa_tabela_banco(
                conn_entrada,
                conn_saida,
                tabela_in,
                tabela_out,
                cols_entrada,
                cols_saida,
                estrategia=estrategia)

    def __grava_tabela(self, 
            entrada, 
            conn_saida, 
            nome_tabela_saida, 
            cols_saida, 
            estrategia,
            cols_chave_update=None):
        """
        Grava uma tabela no banco de dados.

        Args:
        entrada:            a fonte de entrada dos dados (tabela de banco,
                            planilha etc.)
        conn_saida:         conexão com o esqumea de saída (geralmente a
                            produção)
        nome_tabela_saida:  nome da tabela de saida
        cols_saida:         lista das colunas que serão gravadas na tabela de
                            saida, com o nome da coluna, seu tipo, a função de
                            transformanção a ser aplicada (opcional; se não
                            informado, faz só uma cópia do dado) e a quantidade
                            de colunas de entrada que serão usadas na
                            transformação, se for mais de uma
        estrategia:         estratégia de gravação que será utilizada (enum
                            TpEstrategia)
        cols_chave_update:  lista com os nomes das colunas que serão
                            chave de um eventual update na tabela
        """

        cols = {}
        qtd_colunas_calculo = {}
        for item in cols_saida:
            if len(item) == 2:
                # função de transformanção não informada, faz só uma cópia do
                # dado
                cols[item[0]] = ts.Coluna(item[0], item[1], ft.f_copia)
                qtd_colunas_calculo[item[0]] = 1
            else:
                # usa a função de transformanção informada
                cols[item[0]] = ts.Coluna(item[0], item[1], item[2])

                # terceiro parâmetro é a função de transformação, quarto
                # (se houver) é a quantidade de colunas de entrada que
                # serão usadas no cálculo da coluna de saída
                if len(item) == 3:
                    qtd_colunas_calculo[item[0]] = 1
                else:
                    qtd_colunas_calculo[item[0]] = item[3]

        tab_saida = ts.TabelaSaida(
                nome_tabela_saida, 
                cols, 
                conn_saida)
        if self.__qtd_insercoes_simultaneas is not None:
            tab_saida.qtd_insercoes_simultaneas = self.__qtd_insercoes_simultaneas

        # primeiro limpa tabela de saída, se for o caso
        if estrategia == TpEstrategia.DELETE:
            conn_saida.apaga_registros(nome_tabela_saida)
        elif estrategia == TpEstrategia.TRUNCATE:
            conn_saida.trunca_tabela(nome_tabela_saida)
        elif estrategia == TpEstrategia.INSERT:
            pass
        elif estrategia == TpEstrategia.UPDATE_INSERT:
            pass
        elif estrategia == TpEstrategia.INSERT_UPDATE:
            pass
        elif estrategia == TpEstrategia.UPDATE:
            pass
        else:
            raise NotImplementedError

        qtd_registros = 0
        while True:
            registro = entrada.le_prox_registro()
            if registro is None:
                self.__reset_func_pre_pos_processamento()
                break

            if not self.__funcao_pre_processamento(registro):
                continue

            i = 0
            registro_gravado = []
            for k in cols.keys():
                dados_entrada = []
                for _ in range(qtd_colunas_calculo[k]):
                    dados_entrada.append(registro[i])
                    i += 1

                tab_saida.col[k].calcula_valor( tuple(dados_entrada) )
                registro_gravado.append(tab_saida.col[k].valor)

            if  estrategia == TpEstrategia.UPDATE_INSERT or  \
                estrategia == TpEstrategia.INSERT_UPDATE or  \
                estrategia == TpEstrategia.UPDATE:

                # atualmente, nem todos os métodos de carga implementam essas
                # estratégias
                if cols_chave_update is None:
                    raise RuntimeError("É necessário informar as colunas chave "
                                       "para a atualização dos dados.")

                if estrategia == TpEstrategia.UPDATE_INSERT:
                    # tenta primeiro atualizar o registro no banco
                    if not tab_saida.atualiza_registro(cols_chave_update):
                        # atualização falhou porque o registro ainda não existia,
                        # então insere-o
                        tab_saida.insere_registro()

                elif estrategia == TpEstrategia.INSERT_UPDATE:
                    # o teste de existência do registro é feito não com base
                    # em chave primária do banco, mas se um registro com exatamente
                    # os mesmos dados na(s) coluna(s) de cols_chave_update já existe
                    # no banco
                    if tab_saida.registro_existe(cols_chave_update):
                        tab_saida.atualiza_registro(cols_chave_update)
                    else:
                        tab_saida.insere_registro()

                elif estrategia == TpEstrategia.UPDATE:
                    tab_saida.atualiza_registro(cols_chave_update)

            else:
                tab_saida.insere_registro()

            qtd_registros += 1
            
            self.__funcao_pos_processamento(registro, tuple(registro_gravado))
 
        if self.__verbose:
            if entrada.nome == "":
                # a consulta de entrada não leu uma só tabela, mas um
                # select provavelmente com joins de tabelas
                print(  str(qtd_registros) +  \
                        " \tregistros lidos dos dados de entrada e" 
                        " salvos na tabela " +  \
                        nome_tabela_saida)
            else:
                print(  str(qtd_registros) +  \
                        " \tregistros de entrada lidos de " + entrada.nome + \
                        " e salvos na tabela " +  \
                        nome_tabela_saida)

    def __monta_dtype(self, cols_saida, tp_cols_entrada):
        # seta o parâmetro dtype do pandas para a importação de dados num
        # dataframe

        if tp_cols_entrada is None:
            # as colunas de saída terão os mesmos tipos das colunas de entrada
            dtype = {}
            for i, item in enumerate(cols_saida):
                if item[1] == tp.NUMBER:
                    dtype[i] = float
                elif item[1] == tp.INT:
                    dtype[i] = int
                elif item[1] == tp.STRING:
                    dtype[i] = str
                elif item[1] == tp.DATE:
                    dtype[i] = str
                else:
                    raise NotImplementedError
        else:
            # os tipos das colunas de entrada foram informados explicitamente
            dtype = {}
            for i, item in enumerate(tp_cols_entrada):
                if item == tp.NUMBER:
                    dtype[i] = float
                elif item == tp.INT:
                    dtype[i] = int
                elif item == tp.STRING:
                    dtype[i] = str
                elif item == tp.DATE:
                    dtype[i] = str
                else:
                    raise NotImplementedError

        return dtype

    def __formata_dataframe(self, dados_entrada, uso_cols, cols_saida):
        # formata o dataframe de entrada de dados, para permitir 1) mais de uma
        # coluna do dataframe ser fonte de dados para uma só coluna de saída e
        # 2) uma mesma coluna do dataframe ser fonte de dados para mais de uma
        # coluna de saída

        if uso_cols is not None:
            dados_entrada.formata_colunas(uso_cols)

            # permite mais de uma coluna de entrada como fonte para uma única
            # coluna de saída
            for i, col in enumerate(uso_cols):
                if isinstance(col, list):
                    qtd_colunas = len(col)
                    cols_saida[i].append(qtd_colunas)

