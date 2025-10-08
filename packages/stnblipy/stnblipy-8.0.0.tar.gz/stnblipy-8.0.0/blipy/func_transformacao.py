"""
Funções de transformação a serem usadas nas cargas ("T" do ETL).
"""

import os
import hashlib
import html
import re
from datetime import date, datetime


"""
Módulo com as classes de transformação de dados ("T" do ETL)
"""

class TpData():
    # em todos os casos, a informação de horário é no formato hh:mm:ss, 
    # com hora no formato 24h e com um espaço em branco entre a data e a hora

    # dd/mm/yy ou dd/mm/yyyy, com ou sem informação de horário
    BR = "BR"

    # dd-mm-yy ou dd-mm-yyyy, com ou sem informação de horário
    BR_HF = "BR_HF"
    BR_HIFEN = "BR_HF"

    # ddmmyy ou ddmmyyyy, com ou sem informação de horário
    BR_SN = "BR_SN"
    BR_SO_NUMEROS = "BR_SN"

    # mm/dd/yy ou mm/dd/yyyy, com ou sem informação de horário
    EN = "EN"

    # mm-dd-yy ou mm-dd-yyyy, com ou sem informação de horário
    EN_HF = "EN_HF"
    EN_HIFEN = "EN_HF"

    # mmddyy ou mmddyyyy, com ou sem informação de horário
    EN_SN = "EN_SN"
    EN_SO_NUMEROS = "EN_SN"

    # "UN" de "universal"
    # yy/mm/dd ou yyyy/mm/dd, com ou sem informação de horário
    UN = "UN"

    # yy-mm-dd ou yyyy-mm-dd, com ou sem informação de horário
    UN_HF = "UN_HF"
    UN_HIFEN = "UN_HF"

    # yymmdd ou yyyymmdd, com ou sem informação de horário
    UN_SN = "UN_SN"
    UN_SO_NUMEROS = "UN_SN"

class Copia():
    """
    Cópia simples de dados, sem transformações ou nenhum tipo de alteração.
    """

    def transforma(self, entradas):
        """
        Copia a entrada, sem nenhuma transformação.

        Args:
            entradas   : tupla com o valor a ser copiado; como não faz
                         transformação alguma, só pode haver um elemento na
                         tupla
        Ret:
            cópia do valor de entrada
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para cópia.")

        return entradas[0]

class ValorFixo():
    """
    Transforma a entrada num valor fixo.
    """

    def __init__(self, valor):
        self.__valor = valor

    def transforma(self, entradas):
        """
        Retorna um valor fixo, definido na instanciação do objeto. Para valores
        NULL em banco de dados, informar tipo de dados None do Python.

        Args:
            entradas   : não é necessário, mantido apenas para consistência da 
                         interface
        Ret:
            Valor definido na instanciação da classe
        """

        return self.__valor

class DePara():
    """
    Faz um de/para dos valores de entrada.
    """

    def __init__(self, 
            de_para, 
            se_nao_encontrado,
            default="", 
            copia_null=True, 
            trim=True):
        """
        Args:
            de_para:            dict com o de/para desejado
            se_nao_encontrado:  o que fazer se o valor de entrada não for
                                encontrado no de/para. Opções possíveis: 
                                "copia":    copia o valor da entrada para a
                                            saída
                                "null":     preenche a saída com NULL do banco
                                            de dados
                                "erro":     dispara uma exceção
                                "default":  preenche a saída com um valor
                                            default (parâmetro default)
            default:            valor default para a saída, caso o parâmetro
                                se_nao_encontrado for "default"
            copia_null:         indica se uma entrada NULL (ou None ou NaN) será
                                copiada para a saída, ou seja, se este
                                parâmetro for True e a entrada for NULL, a
                                saída será NULL, ignorando a opção do parâmetro
                                se_nao_encontrado
            trim:               indica se será feito um trim no dado de entrada
        """
        self.__de_para = de_para
        self.__se_nao_encontrado = se_nao_encontrado
        self.__default = default
        self.__copia_null = copia_null
        self.__trim = trim

    def transforma(self, entradas):
        """
        Retorna um de/para dos valores de entrada.

        Args:
            entradas   : tupla com o valor a ser transformado; como só
                         transforma um valor em outro, só pode haver um
                         elemento na tupla
        Ret:
            Valor do de/para correspondente ao valor de entrada.
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para um de/para.")

        # formata o valor de entrada
        valor = entradas[0]
        if str(valor) == "nan":
            # pandas utiiliza nan para valores não informados num dataframe
            valor = None

        if valor is not None and self.__trim:
            try:
                valor = valor.strip()
            except:
                # se tipo não for uma string (ou seja, não implementar strip())
                # então não faz nada
                pass

        if self.__copia_null:
            self.__de_para.update({None: None})

        if valor in list(self.__de_para):
            ret = self.__de_para[valor]
        else:
            if self.__se_nao_encontrado == "copia":
                ret = valor
            elif self.__se_nao_encontrado == "default":
                ret = self.__default
            elif self.__se_nao_encontrado == "null":
                ret = None
            elif self.__se_nao_encontrado == "erro":
                raise RuntimeError(
                        "Impossível fazer a transformação, valor de de/para "
                        "não encontrado: " + str(valor)+ ". " + 
                        "De/Para: " + str(self.__de_para))
            else:
                raise NotImplementedError(  "Parâmetro se_nao_encontrado "
                                            "inválido em DePara: " + 
                                            self.__se_nao_encontrado)

        return ret

class DeParaSN(DePara):
    """
    Faz um de/para de campos S/N para 1/0 e vice-versa. Considera também
    a língua (por exemplo, Y/N ao invés de S/N).
    """

    def __init__(self, 
            se_nao_encontrado,
            default="", 
            copia_null=True, 
            inverte=False, 
            val_int=True, 
            lingua="pt"):
        """
        Args:
            se_nao_encontrado:  o que fazer se o valor de entrada não for
                                encontrado no de/para. Opções possíveis: 
                                "copia":    copia o valor da entrada para a
                                            saída
                                "null":     preenche a saída com NULL do banco
                                            de dados
                                "erro":     dispara uma exceção
                                "default":  preenche a saída com um valor
                                            default (parâmetro default)
            default:            valor default para a saída, caso o parâmetro
                                se_nao_encontrado for "default"
            copia_null:         indica se uma entrada NULL (ou None ou NaN) será
                                copiada para a saída, ou seja, se este
                                parâmetro for True e a entrada for NULL, a
                                saída será NULL, ignorando a opção do parâmetro
                                se_nao_encontrado
            inverte:            se de/para é de S/N para 1/0 (False) ou de 1/0 
                                para S/N (True)
            val_int:            se valor 1/0 (entrada ou saída) deve ser um
                                inteiro ou uma string
            lingua:             "pt" ou "en"
        """

        if lingua == "pt" and val_int and not inverte:
            de_para = {"S": 1, "N": 0}
        elif lingua == "pt" and not val_int and not inverte: 
            de_para = {"S": "1", "N": "0"}

        elif lingua == "pt" and val_int and inverte: 
            de_para = {1: "S", 0: "N"}
        elif lingua == "pt" and not val_int and inverte: 
            de_para = {"1": "S", "0": "N"}

        elif lingua == "en" and val_int and not inverte: 
            de_para = {"Y": 1, "N": 0}
        elif lingua == "en" and not val_int and not inverte: 
            de_para = {"Y": "1", "N": "0"}

        elif lingua == "en" and val_int and inverte: 
            de_para = {1: "Y", 0: "N"}
        elif lingua == "en" and not val_int and inverte: 
            de_para = {"1": "Y", "0": "N"}
        else:
            raise NotImplementedError("Língua inválida em DeParaSN: " + lingua)

        super().__init__(de_para, 
                         se_nao_encontrado, 
                         default, 
                         copia_null, 
                         trim=True)

class DeParaChar():
    """
    Faz um de/para de um ou mais caracteres em um texto.

    Atenção: não é preciso trocar aspa simples (') por duas aspas simples ('')
    antes de salvar uma string com aspas simples no banco (por exemplo, a
    string "d'água"), o Blipy já faz essa troca por default.
    """

    def __init__(self, de_para = None):
        """
        Args:
             de_para  : dict com o(s) de/para de caracteres desejados
        """
        self.__de_para = de_para

    def transforma(self, entradas):
        """
        Retorna um texto com um conjunto de caracteres transformados a partir de
        um dict de/para.

        Args:
            entradas : tupla contendo o texto de entrada a ser transformado
        """

        if self.__de_para is None:
            raise RuntimeError(
                "Impossível fazer a transformação, dicionário de/para não encontrado.")

        texto = entradas[0]

        # pandas utiiliza nan para valores não informados num dataframe
        if str(texto) == "nan":
            texto = None

        if texto is not None:
            for chave in self.__de_para.keys():
                texto = texto.replace(chave, self.__de_para[chave])

        return texto

class Somatorio():
    """
    Calcula o somatório dos valores de entrada.
    """

    def transforma(self, entradas):
        """
        Calcula o somatório dos valores de entrada.

        Args:
            entradas   : tupla com os valores a serem somados
        Ret:
            somatório dos valores de entrada
        """

        soma = 0
        for item in entradas:
            if item is not None and str(item) != "nan":
                soma += item
        return soma

class Media():
    """
    Calcula a média dos valores de entrada.
    """

    def transforma(self, entradas):
        """
        Calcula a média dos valores de entrada.

        Args:
            entradas   : tupla com os valores dos quais calcular a média
        Ret:
            média dos valores de entrada
        """

        soma = f_somatorio.transforma(entradas)
        return soma/len(entradas)

class Agora():
    """
    Calcula o dia ou dia/hora atual do banco de dados ou do sistema 
    operacional.
    """

    def __init__(self, conexao=None, so_data=False):
        """
        Args:
            conexao : conexão com o banco de dados (caso se busque a
                      informação no banco) ou None se for para buscar no
                      sistema operacional
            so_data : flag se é para trazer só a data ou a hora também
        """
        self.__so_data = so_data
        self.__conn = conexao

    def transforma(self, entradas):
        """
        Calcula o dia/hora atual.

        Args:
            entradas   : não é necessário, mantido apenas para consistência da 
                         interface
        Ret:
            Dia (ou dia/hora) atual do banco de dados ou do sistema
            operacional, a depender de como o objeto foi construído.
        """

        if self.__conn is None:
            # busca do sistema operacional
            if self.__so_data:
                ret = date.today()
            else:
                ret = datetime.now().replace(microsecond=0)
        else:
            # busca do banco de dados
            if self.__so_data:
                ret = self.__conn.data_hora_banco().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                ret = self.__conn.data_hora_banco().replace(microsecond=0)

        return ret

class HTMLParaTxt():
    """
    Converte uma string com formatação em HTML (tags e acentuação) para um
    texto puro. As tags encontradas serão simplesmente eliminadas do texto
    final. 

    Como textos em HMTL tendem a ser grandes, opcionalmente a string de retorno
    pode ser truncada em uma determinada quantidade de bytes; este trunc leva
    em consideração os bytes necessários para acentuação em UTF-8.
    """
 
    def __init__(self, qtd_bytes=None):
        """
        Args:
        :param qtd_bytes: opcional; quantidade de bytes para um trunc da string
        final.
        """
        self.__qtd_bytes = qtd_bytes
 
    def transforma(self, entradas):
        """
        Retorna a string da entrada em HTML transformada para texto puro, com
        ou sem trunc. Se entrada for None, retorna None.

        # TODO: FIXME: se o HTML tiver os caracteres '<' ou '>' na sua parte
        # textual essa função provavelmente falhará

        Args:
            entradas : tupla contendo a string a ser transformada
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada.")

        if entradas[0] is None or   \
           str(entradas[0]) == "nan":
            return None

        ret = entradas[0]
        ret = ret.replace("\r", " ")
        ret = ret.replace("\n", " ")
        ret = ret.replace("\t", " ")

        # trata o html, corrigindo os acentos e retirando as tags
        ret = re.sub("(?<=<).*?(?=>)", "", html.unescape(ret))
        ret = ret.replace("\xa0", " ")
        ret = ret.replace("<>", "")

        # troca aspas simples do texto por duas aspas simples, para não dar
        # problema na hora da inserção no oracle
        ret = DeParaChar({"'": "''"}).transforma((ret, ))

        # retira excessos de espaços em branco
        ret = Trim().transforma((ret, ))
        ret = re.sub("\s{2,}", " ", ret)

        if self.__qtd_bytes is not None:
            ret = TruncaStringByte(self.__qtd_bytes).transforma((ret, ))

        return ret

class Trim():
    """
    Faz um trim numa string. Pode-se parametrizar se será um trim no início e
    fim, só no início ou só no fim.
    """
 
    def __init__(self, tipo_trim = "inicio_fim"):
        """
        Args:
        :param tipo_trim: tipo de trim a ser feito. Valores possíveis:
        "inicio_fim", "inicio", "fim"
        """
        self.__tipo_trim = tipo_trim
 
    def transforma(self, entradas):
        """
        Retorna a string da entrada com trim. Se entrada for None, retorna
        None.

        Args:
            entradas : tupla contendo a string a ser transformada
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para trim.")

        if entradas[0] is None or   \
           str(entradas[0]) == "nan":
            return None

        if self.__tipo_trim == "inicio_fim":
            trim = entradas[0].strip()
        elif self.__tipo_trim == "inicio":
            trim = entradas[0].ltrip()
        elif self.__tipo_trim == "fim":
            trim = entradas[0].rtrip()
        else:
            raise RuntimeError(
                "Tipo de trim incorreto.")

        return trim

class TruncaStringByte():
    """
    Trunca uma string até o número de bytes informado. Caracteres acentuados
    são considerados, de forma que é garantido que a quantidade de bytes
    utilizados para a string nunca é maior que a quantidade máxima de bytes
    informado no construtor.
    """
 
    def __init__(self, qtd_bytes):
        """
        Args:
        :param qtd_bytes: quantidade de bytes que a string terá ao final
        """
        self.__qtd_bytes = qtd_bytes
 
    def transforma(self, entradas):
        """
        Retorna a string truncada. Se entrada for None, retorna None.

        Args:
            entradas : tupla contendo a string a ser transformada
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para truncar.")

        if entradas[0] is None or       \
           str(entradas[0]) == "nan":
            return None
        
        # solução obtida em https://stackoverflow.com/questions/13665001/python-truncating-international-string
        if len(entradas[0].encode('utf-8')) > self.__qtd_bytes:
            trunc = \
                entradas[0].encode('utf-8')[:self.__qtd_bytes].decode('utf-8',
                'ignore')
        else: 
            trunc = entradas[0]

        return trunc

class Lookup():
    """
    Transforma o dado a partir de uma tabela de lookup informada.
    """
 
    def __init__(self, 
            conexao, 
            tabela_lookup, 
            campo, 
            chave,
            filtro = ""):
        """
        Args:
        conexao:        conexão com o banco de dados que contém a tabela de
                        lookup
        tabela_lookup:  a tabela de lookup
        campo:          o campo a ser retornado da lookup
        chave:          o(s) campo(s) na tabela de lookup que liga(m) as duas
                        tabelas. Pode ser uma string apenas ou uma lista de
                        strings com os nomes dos campos
        filtro:         opcional; um filtro que pode ser aplicado ao montar a
                        cláusula WHERE do SQL de busca

        Por exemplo, para buscar o texto de informação na tabela de informação
        da solução para o tipo 31 de uma determinada solução, ou seja, para
        executar o comando SQL abaixo:

        'select TX_INFORMACAO 
        from INFO_SOLUCAO 
        where
        ID_TIPO_INFORMACAO = 31 and ID_SOLUCAO = 2207'

        e considerando que a chave que liga as duas tabelas na lookup é
        ID_SOLUCAO, os parâmetros devem ser:

        tabela_lookup = 'INFO_SOLUCAO'
        campo = 'TX_INFORMACAO'
        chave = 'ID_SOLUCAO'
        filtro = 'ID_TIPO_INFORMACAO = 31'

        O valor de ID_SOLUCAO no SQL final será preenchido automaticamente a
        cada linha no loop de carga da tabela de origem.
        """

        self.__conexao = conexao
        self.__tabela_lookup = tabela_lookup
        self.__campo = campo
        self.__chave = chave
        self.__filtro = filtro
 
    def transforma(self, entradas):
        """
        Retorna o dado buscado numa tabela de lookup, usando a entrada
        informada como parâmetro de busca na lookup.

        Args:
            entradas: lista com a(s) chave(s) de busca da lookup
        """

        # não faz sentido buscar por uma chave que seja NULL
        for i in entradas:
            if i is None or str(i) == "nan":
                return None

        where = \
            self.__filtro + " AND " if self.__filtro != "" else \
            ""

        sql =   "select " + self.__campo +              \
                " from " + self.__tabela_lookup +       \
                " where " + where

        # TODO: FIXME: se o tipo da chave for date, o código abaixo
        # provavelmente não vai funcionar, pois datas devem ter uma formatação
        # específica para serem usadas na string SQL. Mas quem põe data como
        # chave de lookup merece sofrer mesmo
        if type(self.__chave) is list:
            chave = ""
            for i, v in enumerate(self.__chave):
                chave += v + " = "
                chave += \
                    str(entradas[i]) if type(entradas[i]) is not str else \
                    "'" + str(entradas[i]) + "'"
                chave += " AND "
            chave = chave[:-5]
        else:
            chave = self.__chave + " = "
            chave += \
                str(entradas[0]) if type(entradas[0]) is not str else \
                "'" + str(entradas[0]) + "'"
        sql += chave

        try:
            registro = self.__conexao.executa(sql)
        except:
            raise RuntimeError("Erro na execução do SELECT no banco de dados.")

        try:
            ret = next(registro)[0]
        except StopIteration:
            ret = None

        return ret
    

class ConcatenaStrings():
    """
    Concatena duas ou mais strings.
    """
 
    def __init__(self, trim=None, sep=None):
        """
        Args:
        trim:   tipo de trim que será feito nas strings de entrada e/ou de
                saída. Valores possíveis: None (nenhum trim é efetuado),
                "entradas" (um trim é feito em cada string de entrada antes da
                concatenação) ou "resultado" (um trim é feito apenas na string
                resultante da concatenação das entradas). Todos os trims, se
                feitos, são feitos tanto no início como no fim da string
        sep:    string opcional para ser usada como um separador entre as
                strings de entrada
        """
        if trim is not None and trim != "entradas" and trim != "resultado":
            raise RuntimeError("Parâmetro de trim incorreto.")

        self.__trim = trim
        self.__sep = sep

    def transforma(self, entradas):
        """
        Retorna a concatenação das strings de entrada, na ordem em que foram
        informadas.

        Args:
            entradas : tupla com as strings a serem concatenadas
        """

        if len(entradas) < 2:
            raise RuntimeError(
                    "São necessárias ao menos duas strings para fazer a "
                    "concatenação.")

        ret = ""
        for s in entradas:
            if s is not None:
                if self.__trim == "entradas":
                    ret += str(s).strip()
                else:
                    ret += str(s)

                if self.__sep is not None:
                    ret += self.__sep

        if self.__sep is not None and ret != "":
            ret = ret[0:len(ret) - len(self.__sep)]

        if self.__trim == "resultado":
            ret = ret.strip()

        return ret

class StrParaData():
    """
    Cria uma data (tipo datetime do Python) a partir de uma string e um formato
    informados. Por conveniência, alguns formatos mais comuns já são
    disponibilizados na forma de constantes via classe TpData, mas um formato
    específico pode ser passado como uma string reconhecível pelo método
    datetime.strptime do Python.
    """
 
    def __init__(self, formato, ignora_horario=False):
        self.__formato = formato
        self.__ignora_horario = ignora_horario

    def transforma(self, entradas):
        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para "
                "formatar uma string como data.")

        data = str(entradas[0])

        if data is None or data == "nan":
            return None

        if True: # só pra criar uma identação e ficar melhor de ver o código
            if self.__formato == TpData.BR:
                if len(data) == 8:
                    formato = "%d/%m/%y"
                elif len(data) == 10:
                    formato = "%d/%m/%Y"
                elif len(data) == 17:
                    formato = "%d/%m/%y %H:%M:%S"
                elif len(data) == 19:
                    formato = "%d/%m/%Y %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                       " inválida para o formato BR.")

            elif self.__formato == TpData.BR_HF:
                if len(data) == 8:
                    formato = "%d-%m-%y"
                elif len(data) == 10:
                    formato = "%d-%m-%Y"
                elif len(data) == 17:
                    formato = "%d-%m-%y %H:%M:%S"
                elif len(data) == 19:
                    formato = "%d-%m-%Y %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                       " inválida para o formato BR_HIFEN.")

            elif self.__formato == TpData.BR_SN:
                if len(data) == 6:
                    formato = "%d%m%y"
                elif len(data) == 8:
                    formato = "%d%m%Y"
                elif len(data) == 15:
                    formato = "%d%m%y %H:%M:%S"
                elif len(data) == 17:
                    formato = "%d%m%Y %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                   " inválida para o formato BR_SO_NUMEROS.")

            elif self.__formato == TpData.EN:
                if len(data) == 8:
                    formato = "%m/%d/%y"
                elif len(data) == 10:
                    formato = "%m/%d/%Y"
                elif len(data) == 17:
                    formato = "%m/%d/%y %H:%M:%S"
                elif len(data) == 19:
                    formato = "%m/%d/%Y %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                       " inválida para o formato EN.")
                    
            elif self.__formato == TpData.EN_HF:
                if len(data) == 8:
                    formato = "%m-%d-%y"
                elif len(data) == 10:
                    formato = "%m-%d-%Y"
                elif len(data) == 17:
                    formato = "%m-%d-%y %H:%M:%S"
                elif len(data) == 19:
                    formato = "%m-%d-%Y %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                       " inválida para o formato EN_HIFEN.")

            elif self.__formato == TpData.EN_SN:
                if len(data) == 6:
                    formato = "%m%d%y"
                elif len(data) == 8:
                    formato = "%m%d%Y"
                elif len(data) == 15:
                    formato = "%m%d%y %H:%M:%S"
                elif len(data) == 17:
                    formato = "%m%d%Y %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                   " inválida para o formato EN_SO_NUMEROS.")
                    
            elif self.__formato == TpData.UN:
                if len(data) == 8:
                    formato =  "%y/%m/%d"
                elif len(data) == 10:
                    formato =  "%Y/%m/%d"
                elif len(data) == 17:
                    formato = "%y/%m/%d %H:%M:%S"
                elif len(data) == 19:
                    formato = "%Y/%m/%d %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                       " inválida para o formato UN.")

            elif self.__formato == TpData.UN_HF:
                if len(data) == 8:
                    formato =  "%y-%m-%d"
                elif len(data) == 10:
                    formato =  "%Y-%m-%d"
                elif len(data) == 17:
                    formato = "%y-%m-%d %H:%M:%S"
                elif len(data) == 19:
                    formato = "%Y-%m-%d %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                                       " inválida para o formato UN_HIFEN.")

            elif self.__formato == TpData.UN_SN:
                if len(data) == 6:
                    formato =  "%y%m%d"
                elif len(data) == 8:
                    formato =  "%Y%m%d"
                elif len(data) == 15:
                    formato = "%y%m%d %H:%M:%S"
                elif len(data) == 17:
                    formato = "%Y%m%d %H:%M:%S"
                else:
                    raise RuntimeError("Data " + data + 
                               " inválida para o formato UN_SO_NUMEROS.")

            else:
                formato = self.__formato

        data = datetime.strptime(data, formato)

        if self.__ignora_horario:
            data = data.replace(hour=0, minute=0, second=0, microsecond=0)

        return data

class MontaDataMesAno():
    """
    Dados um mês e ano obtidos de um registro de entrada, cria uma data com o
    dia informado no construtor desta classe. Se mês ou ano forem None, retorna
    None. O ano pode ter 2 ou 4 dígitos. 

    Por padrão, força o último dia válido para o mês em questão, se o dia não
    for válido para aquele mês (por exemplo, 31/04/yyyy vira 30/04/yyyy, ou
    30/02/yyyy vira 29/02/yyyy ou 28/02/yyyy, dependendo se o ano for bissexto
    ou não), mas esse comportamento pode ser alterado para disparar uma exceção
    nestes casos.
    """
 
    def __init__(self, dia=1, trata_ult_dia=True):
        """
        Args:
        dia:            o dia a ser juntado ao mês e ano para formar uma data
        trata_ult_dia:  garante que seja usado o último dia válido para o mês.
                        Por exemplo, se dia=30 e mês=2, retorna 28/02/yyyy ou
                        29/02/yyyy (dependendo de ano ser bissexto ou não), ou
                        se dia=31 e mes=4, retorna 30/04/yyyy. Se False,
                        dispara uma exceção nestes casos
        """

        if dia < 1 or dia > 31:
            raise RuntimeError(
                "Dia para criação da data tem que estar entre 1 e 31.")

        self.__dia = dia
        self.__trata_ult_dia = trata_ult_dia

    def transforma(self, entradas):
        """
        Gera uma data a partir do mês e ano lidos do registro de entrada.

        Args:
            entradas :  tupla com o mês e o ano para a geração da data. Se mês
                        ou ano forem None, retorna None. O ano pode ter 2 ou 4
                        dígitos.
        """

        if len(entradas) != 2:
            raise RuntimeError(
                "Um mês e um ano devem ser informados para gerar uma data.")

        if entradas[0] is None or entradas[1] is None:
            return None

        # esse cast para int é necesário pois quando usa o pandas para ler um
        # valor, ele considera float, aí por exemplo str(mes) ficaria "1.0" ao
        # invés de "1"
        mes = int(entradas[0])
        ano = int(entradas[1])

        formato = "%d/%m/%Y" if len(str(ano)) == 4 else "%d/%m/%y" 
        mesano = "/" + str(mes).zfill(2) + "/" + str(ano)

        try:
            if self.__trata_ult_dia:
                try:
                    data = datetime.strptime(str(self.__dia) + mesano, formato)
                except ValueError:
                    if mes == 2:
                        try:
                            # dia era 31 ou 30, ou dia era 29 e ano não era
                            # bissexto. Tenta novamente com dia 29 (não se se
                            # ano é bissexto ou não) e se ainda não der, usa
                            # dia 28
                            data = datetime.strptime(str(29) + mesano, formato)
                        except ValueError:
                            data = datetime.strptime(str(28) + mesano, formato)
                    else:
                        # dia era 31 mas mês só tem 30 dias
                        data = datetime.strptime(str(30) + mesano, formato)
            else:
                # se data ficar inválida (por exemplo 31/04) deixa disparar uma
                # exceção
                data = datetime.strptime(str(self.__dia) + mesano, formato)
        except:
            raise ValueError("Data inválida: " + str(self.__dia) + mesano)
        
        return data

class InverteSinal():
    """
    Inverte o sinal de um valor. Trata tanto números quanto strings que
    contenham um número.
    """

    def transforma(self, entradas):
        """
        Inverte o sinal do valor passado como argumento. Caso o argumento seja
        uma string, ela é primeiro transformada num número, não importando se
        o separador de decimal da string é vírgula ou ponto.

        Args:
        entradas: tupla com o valor a ter o sinal invertido
        """
        
        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para uma "
                "inversão de sinal.")

        if entradas[0] is None or entradas[0] == "nan":
            return None

        if type(entradas[0]) == str:
            val = entradas[0].replace(",", ".")
            val = float(val)
        else:
            val = entradas[0]

        return val*(-1)
    
class Hash():
    """
    Função que retorna um hash de um valor. Utiliza o algoritmo md5. Se o
    parâmetro salt_hash for None, será utilizado o valor padrão definido numa
    variável de ambiente chamada SALT_HASH.
    """

    def __init__(self, salt_hash=None):
        self.__salt_hash = salt_hash

    def transforma(self, entradas):                
        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para um "
                "hash.")

        if entradas[0] is None or entradas[0] == "nan":
            return None

        val = str(entradas[0])
        salt_hash = self.__salt_hash

        if salt_hash is None:
            salt_hash = os.getenv("SALT_HASH")
        else:
            salt_hash = str(salt_hash)

        if salt_hash is None:
            raise RuntimeError("A variável de ambiente SALT_HASH não foi "
                               "encontrada.")

        val = (val + salt_hash).encode("utf-8")

        return str.upper(hashlib.md5(val).hexdigest())
    
class HashCPF(Hash):
    """
    Função que retorna um hash de um valor de um CPF, garantindo que o hash de
    CPFs de mesma numeração serão iguais independentemente de suas formatações.
    Utiliza o algoritmo herdado da classe Hash. Sempre será utilizado o valor
    padrão de salt definido numa variável de ambiente chamada SALT_HASH.
    """

    # 'None' é passado como parâmetro para o construtor da classe pai, para
    # garantir que o valor do salt vai ser buscado da variável de ambiente
    # SALT_HASH    
    def __init__(self):
        super().__init__(None)

    def transforma(self, entradas):
        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um CPF de entrada para um "
                "hash.")

        if entradas[0] is None or entradas[0] == "nan":
            return None
        
        # Retirando do cpf caracteres indesejados, para que ele fique apenas
        # com números
        cpf = str(entradas[0]).strip()
        cpf = cpf.replace(".", "")
        cpf = cpf.replace("-", "")

        # Laço para completar o cpf com zeros, caso ele tenha menos que 11
        # dígitos
        while len(cpf) < 11:
            cpf = "0" + cpf

        return super().transforma([cpf])

class Incrementa():
    """
    Função que retorna, a partir de um valor inicial, um incremento ou
    decremento a cada chamada. Se o valor inicial não for informado, será 1. O
    passo default para o incremento ou decremento é 1, mas ele pode ser
    customizado, inclusive com valores negativos (decremento).
    """

    def __init__(self, valor_inicial=1, passo=1):
        self.__valor_inicial = valor_inicial
        self.__passo = passo
        self.__primeiro = False
        self.__valor = None

    def transforma(self, entradas):
        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um valor a ser incrementado/decrementado.")

        if entradas[0] is None or entradas[0] == "nan":
            return None

        if not self.__primeiro:
            self.__valor = self.__valor_inicial
            self.__primeiro = True
        else:
            self.__valor += self.__passo

        return self.__valor

class AlteraCaixa():
    """
    Função para alterar a caixa de uma palavra/frase.

    Tipos de conversão possíveis:
    "cxalta": MAIÚSCULAS
    "cxbaixa": minúsculas
    "titulo": A Primeira Letra De Cada Palavra
    "frase": A primeira letra da frase
    """

    def __init__(self, tipo):
        self.__tipo = tipo

    def transforma(self, entradas):
        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um valor para alteração de caixa.")

        if entradas[0] is None or entradas[0] == "nan":
            return None

        if self.__tipo == "cxalta":
            ret = entradas[0].upper()

        elif self.__tipo == "cxbaixa": 
            ret = entradas[0].lower()

        elif self.__tipo == "frase": 
            palavras = entradas[0].split() 

            # muda tudo para caixa baixa, menos siglas
            palavras = [palavra if palavra.isupper() else palavra.lower() 
                        for palavra in palavras]

            # apenas primeira letra da primeira palavra pra caixa alta, exceto
            # se for sigla
            if not palavras[0].isupper():
                palavras[0] = palavras[0].capitalize()

            ret = ' '.join(palavras)

        elif self.__tipo == "titulo": 
            excecao = [ "de", "da",  "das", "do", "dos", 
                        "e", 
                        "a", "as", "o", "os",  "à", "às", "ao", "aos", 
                        # "um", "uma", "uns", "umas",
                        "em", "na", "nas", "no", "nos",
                        "com",
                        "ou"]

            palavras = entradas[0].split() 

            # muda tudo para caixa baixa, menos siglas e as exceções
            palavras = [palavra 
                        if palavra in excecao or palavra.isupper() 
                        else palavra.capitalize()
                        for palavra in palavras]

            # apenas primeira letra da primeira palavra pra caixa alta, exceto
            # se for sigla
            if not palavras[0].isupper():
                palavras[0] = palavras[0].capitalize()

            ret = self.__trata_palavras_compostas(palavras)

        else:
            raise RuntimeError("Tipo de alteração de caixa não implementado.")

        return ret

    def __trata_palavras_compostas(self, palavras):
        # torna maiúscula a primeira letra de cada palavra que tenha hífen,
        # para evitar por exemplo que Coordenação-Geral vire Coordenação-geral
        for i, palavra in enumerate(palavras):
            j = palavra.find("-")

            if j != -1 and (j + 1) != len(palavra):
                p = palavra[:j+1] + palavra[j+1].upper() + palavra[j+2:]

                palavras[i] = p

        return  ' '.join(palavras)


# TODO: implementar classe de transformação de conversão tipo

#  objetos de classes de transformação que só fazem sentido ter uma instância 
#  (singletons). Desta forma, ao importar este módulo estes objetos já estarão
#  instanciandos e bastará utilizá-los, sem necessidade de criar uma nova
#  instância no código que importou este módulo
f_copia     = Copia()
f_somatorio = Somatorio()
f_media     = Media()

