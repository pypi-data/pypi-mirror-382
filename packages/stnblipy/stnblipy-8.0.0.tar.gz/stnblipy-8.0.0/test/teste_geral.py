import sys
sys.path.append('..')

from blipy.conexao_bd import ConexaoBD
from blipy.job import Job, TpEstrategia
from blipy.enum_tipo_col_bd import TpColBD as tp
from blipy.jsonstring import TpJson
import blipy.func_transformacao as ft


# def filtra_numero_not_null(registro):
#     # return True
#     # VALOR_ACUMULADO diferente de null
#     if registro[0] is not None:
#         return True

#     return False

# def atualiza_indices(conn_stg):
#     job = Job("Carga Indice Calculados")

#     # Carga na tabela Valor Indexador 
# # TODO: ajeitar and ((0 = 1)) no select abaixo (no talend é um parâmetro "calcula todos os anos", que fica no contexto)
# # TODO: lista de códigos em IDX.CO_BCB IN(433,189,196) é mesmo fixa ou foi só pra testes?
#     sql_entrada = """
#         select 
#                 DEV_CORPORATIVO.PKG_INDEXADORES.INDEXADOR_NO_ANO(
#                     IDX.CO_BCB,
#                     EXTRACT(year FROM VI.DT_INDEXADOR),
#                     EXTRACT(MONTH FROM VI.DT_INDEXADOR)) 
#             AS VALOR_ACUMULADO,
#             VI.ID_INDEXADOR,
#             VI.DT_INDEXADOR,
#             VI.TESTE_STRING
#         from 
#             VALOR_INDEXADOR VI, INDEXADOR IDX
#         where 
#             VI.ID_INDEXADOR = IDX.ID_INDEXADOR 
#             and IDX.CO_BCB IN (433,189,196) 
#             and (
#                 (0 = 1) 
#                 or (VI.DT_INDEXADOR = ( select 
#                                             max(VI_DENTRO.DT_INDEXADOR) 
#                                         from 
#                                             VALOR_INDEXADOR VI_DENTRO 
#                                         where 
#                                             VI.ID_INDEXADOR = VI_DENTRO.ID_INDEXADOR))
#             ) 
#         order by 
#             VI.ID_INDEXADOR, VI.DT_INDEXADOR
#         """

#     cols_saida = [ 
#         ["VA_INDEXADOR", tp.NUMBER],
#         ["ID_INDEXADOR", tp.NUMBER, ft.LookupViaTabela(
#             conn_stg, 
#             "INDEXADOR", 
#             "ID_INDEXADOR", 
#             "ID_INDEXADOR_PAI",
#             filtro="NO_FONTE = 'Calculado STN'")],  
#         ["DT_INDEXADOR", tp.DATE],
#         ["TESTE_STRING", tp.STRING]    
#     ]

#     job.importa_tabela_por_nome(
#             conn_stg, 
#             conn_stg, 
#             "VALOR_INDEXADOR_TESTE",
#             "VALOR_INDEXADOR_TESTE",
#             [
#                 "VA_INDEXADOR",
#                 "ID_INDEXADOR",
#                 "DT_INDEXADOR",
#                 "TESTE_STRING"
#             ],
#             cols_saida,
#             filtro_entrada="ID_INDEXADOR = 65",
#             estrategia=TpEstrategia.UPDATE_INSERT,
#             cols_chave_update=["ID_INDEXADOR"]
#     ) 

    # job.set_func_pre_processamento(filtra_numero_not_null)
    # job.importa_tabela_por_sql(   
    #         conn_stg, 
    #         conn_stg, 
    #         sql_entrada,
    #         "VALOR_INDEXADOR_TESTE",
    #         cols_saida,
    #         # estrategia=TpEstrategia.UPDATE_INSERT,
    #         estrategia=TpEstrategia.INSERT_UPDATE,
    #         cols_chave_update=["ID_INDEXADOR", "VA_INDEXADOR"]
    #         # cols_chave_update=["ID_INDEXADOR"]
    # ) 
    
# if __name__ == "__main__":
#     try:
#         conn_stg,  = ConexaoBD.from_json()

#         atualiza_indices(conn_stg)

# # TODO: testar carga de registros com insert e delete, pra ver se continuam funcionando
# # TODO: testar carga de registros com insert de várias linhas de uma só vez, ao mesmo tempo em que faz update linha a linha; acho que vai funcionar, pois as linhas a serem inseridas vão ficando na memória como já era antes mesmo, independentemente de algumas linhas terem sido atualizadas antes


#     except:
#         raise
#         #sys.exit(1)

# if __name__ == "__main__":
#     try:
#         conn_stg_tg, conn_dev_custos_cc = ConexaoBD.from_json([3, 1])
#         pass
#     except:
#         raise



# def atualiza_dimensao_ug_tbl(conn_stg, conn_prd):
#     job = Job("Carga de ug_tbl")

#     # dimensão UG
#     cols_entrada = [
#         "ID_UG", 
#         "TE_EXERCICIO", 
#         "NO_UG", 
#         "DT_ATUALIZACAO_CARGA", 
#         "IN_OPERACAO", 
#         "ID_UG_POLO", 
#         "ID_UG_SETORIAL_CONTABIL", 
#         "ID_ORGAO",
#         ["ID_ORGAO", "TE_EXERCICIO"]
#     ]
#     cols_saida = [  
#         ["ID_UG", tp.STRING],
#         ["TE_EXERCICIO", tp.STRING],
#         ["NO_UG", tp.STRING],
#         ["DT_ATUALIZACAO_CARGA", tp.DATE],
#         ["IN_OPERACAO", tp.STRING],
#         ["ID_UG_POLO", tp.STRING],
#         ["ID_UG_SETORIAL_CONTABIL", tp.STRING],
#         ["ID_ORGAO", tp.STRING],
#         ["NO_ORGAO", tp.STRING,
#             ft.LookupViaTabela(
#                 conn_stg, 
#                 "ORGAO", 
#                 "NO_ORGAO", 
#                 ["ID_ORGAO", "TE_EXERCICIO"])]
#     ]
#     job.importa_tabela_por_nome(
#             conn_stg, 
#             conn_prd, 
#             "UG", 
#             "UG_TBL",
#             cols_entrada, 
#             cols_saida)


# def atualiza_dimensao_servico_tbl(conn_stg, conn_prd):
#     job = Job("Carga de servico_tbl")

#     # dimensão SERVICO
#     cols_entrada = [
#         "ID_SERVICO_SK",
#         "NO_SERVICO",
#         "ID_UG",
#         "TE_EXERCICIO_UG",
#         "ID_RECOLHIMENTO_STN",
#         "TE_EXERCICIO_RECOLHIMENTO_STN",
#         "CO_TIPO_SERVICO",
#         "IN_SITUACAO",
#         "CO_CPF_USUARIO_CRIACAO",
#         "DT_CRIACAO",
#         "CO_CPF_USUARIO_ATUALIZACAO",
#         "DT_ATUALIZACAO",
#         "TX_MOTIVO_ATUALIZACAO",
#         "CO_TIPO_SERVICO"
#     ]
#     cols_saida = [  
#         ["ID_SERVICO_SK", tp.NUMBER],
#         ["NO_SERVICO", tp.STRING],
#         ["ID_UG", tp.STRING],
#         ["TE_EXERCICIO_UG", tp.STRING],
#         ["ID_RECOLHIMENTO_STN", tp.STRING],
#         ["TE_EXERCICIO_RECOLHIMENTO_STN", tp.STRING],
#         ["CO_TIPO_SERVICO", tp.STRING],
#         ["IN_SITUACAO", tp.STRING],
#         ["CO_CPF_USUARIO_CRIACAO", tp.STRING],
#         ["DT_CRIACAO", tp.DATE],
#         ["CO_CPF_USUARIO_ATUALIZACAO", tp.STRING],
#         ["DT_ATUALIZACAO", tp.DATE],
#         ["TX_MOTIVO_ATUALIZACAO", tp.STRING],
#         ["NO_TIPO_SERVICO", tp.STRING, 
#             ft.LookupViaTabela(
#                 conn_stg, 
#                 "TIPO_SERVICO", 
#                 "NO_TIPO_SERVICO", 
#                 "CO_TIPO_SERVICO")],
#     ]
#     job.importa_tabela_por_nome(
#             conn_stg, 
#             conn_prd, 
#             "SERVICO", 
#             "SERVICO_TBL",
#             cols_entrada, 
#             cols_saida)


# if __name__ == "__main__":
#     try:
#         master_job = Job("Teste Geral")

#         conn_stg, conn_prd = ConexaoBD.from_json()
    
#         atualiza_dimensao_ug_tbl(conn_stg, conn_prd)

#         atualiza_dimensao_servico_tbl(conn_stg, conn_prd)
    
#         # atualiza_fatos(conn_stg, conn_prd)

#         # master_job.grava_log_atualizacao(conn_prd)
#     except:
#         # raise
#         sys.exit(1)




# if __name__ == "__main__":
#     try:
#         job = Job("Teste Geral")

#         conn_stg, = ConexaoBD.from_json()

#         job.copia_tabelas(
#             conn_stg,
#             conn_stg,
#             [
#                 # ["ASSUNTO",  "NO_ASSUNTO", "ID_ASSUNTO", "ID_ASSUNTO_PAI"], 
#                 # ["ASSUNTO",  "NO_ASSUNTO", "ID_ASSUNTO"], 
#                  # "ABRANGENCIA"
#                  # "ASSUNTO",
#                  # ["ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "ID_ABRANGENCIA", "QT_PONTOS"]
#                  "FERRAMENTA",
#                  "CADEIA_VALOR"
#             ],
#             # prefixo_tabelas_entrada="MVW_"
#             prefixo_tabelas_saida="AA_"
#         )
    
#     except:
#         raise




# from urllib.request import urlopen
# import json
# from blipy.jsonstring import TpJson
# from datetime import datetime
 
# class FormataData():
#     def transforma(self, entradas):
#         if entradas[0] is not None:
#             return datetime.strptime(entradas[0][:10], "%Y-%m-%d")
#         else:
#             return None

# def carrega_programa_especial(conn_stg):
#     job = Job("Carrega programa especial")

#     # response = urlopen("https://api.transferegov.gestao.gov.br/transferenciasespeciais/programa_especial?limit=10")
#     response = urlopen("https://api.transferegov.gestao.gov.br/transferenciasespeciais/programa_especial")
#     # dados_json = str(json.loads(response.read()))
#     dados_json = json.dumps(json.loads(response.read()), ensure_ascii=False)

#     # tp_cols_entrada = [
#     #     tp.NUMBER,
#     #     tp.NUMBER,
#     #     tp.STRING,
#     #     tp.STRING,
#     #     tp.NUMBER,
#     #     tp.STRING,
#     #     tp.STRING,
#     #     tp.NUMBER,
#     #     tp.STRING,
#     #     tp.STRING,
#     #     tp.NUMBER,
#     #     tp.STRING,
#     #     tp.NUMBER,
#     #     tp.DATE,
#     #     tp.DATE,
#     #     tp.NUMBER,
#     #     tp.NUMBER,
#     #     tp.NUMBER,
#     #     tp.NUMBER,
#     #     tp.NUMBER,
#     #     tp.NUMBER,
#     #     tp.NUMBER
#     # ]

#     # dados_json = '[{"id_programa": 3, "ano_programa": 2020, "modalidade_programa": "ESPECIAL", "codigo_programa": "0903", "id_orgao_superior_programa": 235876, "sigla_orgao_superior_programa": "ME", "nome_orgao_superior_programa": "Ministerio da Economia", "id_orgao_programa": 235876, "sigla_orgao_programa": "ME", "nome_orgao_programa": "Ministerio da Çabedoriaç", "id_unidade_gestora_programa": 1, "documentos_origem_programa": "2020DF00001 - 2020DF00002", "id_unidade_orcamentaria_responsavel_programa": 73101, "data_inicio_ciencia_programa": "2024-01-01", "data_fim_ciencia_programa": "2024-01-01", "valor_necessidade_financeira_programa": 621218088, "valor_total_disponibilizado_programa": 621218088, "valor_impedido_programa": 0, "valor_a_disponibilizar_programa": 0, "valor_documentos_habeis_gerados_programa": 621218088, "valor_obs_geradas_programa": 621218088, "valor_disponibilidade_atual_programa": 0 }]'

#     cols_saida = [  
#         ["ID_PROGRAMA", tp.NUMBER],
#         ["ANO_PROGRAMA", tp.NUMBER],
#         ["MODALIDADE_PROGRAMA", tp.STRING],
#         ["CODIGO_PROGRAMA", tp.STRING],
#         ["ID_ORGAO_SUPERIOR_PROGRAMA", tp.NUMBER],
#         ["SIGLA_ORGAO_SUPERIOR_PROGRAMA", tp.STRING],
#         ["NOME_ORGAO_SUPERIOR_PROGRAMA", tp.STRING, ft.DeParaChar({"Ministerio": "Ministério", "Ministerio da Fazenda": "Ministério da Fazenda"})],
#         # ["NOME_ORGAO_SUPERIOR_PROGRAMA", tp.STRING],
#         ["ID_ORGAO_PROGRAMA", tp.NUMBER],
#         ["SIGLA_ORGAO_PROGRAMA", tp.STRING],
#         ["NOME_ORGAO_PROGRAMA", tp.STRING],
#         ["ID_UNIDADE_GESTORA_PROGRAMA", tp.NUMBER],
#         ["DOCUMENTOS_ORIGEM_PROGRAMA", tp.STRING],
#         ["ID_UNIDADE_ORCAMENTARIA_RESPONSAVEL_PROGRAMA", tp.NUMBER],
#         ["DATA_INICIO_CIENCIA_PROGRAMA", tp.DATE, FormataData()],
#         ["DATA_FIM_CIENCIA_PROGRAMA", tp.DATE, FormataData()],
#         ["VALOR_NECESSIDADE_FINANCEIRA_PROGRAMA", tp.NUMBER],
#         ["VALOR_TOTAL_DISPONIBILIZADO_PROGRAMA", tp.NUMBER],
#         ["VALOR_IMPEDIDO_PROGRAMA", tp.NUMBER],
#         ["VALOR_A_DISPONIBILIZAR_PROGRAMA", tp.NUMBER],
#         ["VALOR_DOCUMENTOS_HABEIS_GERADOS_PROGRAMA", tp.NUMBER],
#         ["VALOR_OBS_GERADAS_PROGRAMA", tp.NUMBER],
#         ["VALOR_DISPONIBILIDADE_ATUAL_PROGRAMA", tp.NUMBER]
#     ]

#     job.importa_json_str(
#         conn_stg,
#         "API_PROGRAMA",
#         cols_saida,
#         dados_json,
#         TpJson.LIST)
#         # estrategia=TpEstrategia.UPDATE_INSERT,
#         # cols_chave_update=["ID_PROGRAMA"],
#         # cols_entrada=[0,0,2],

# def carrega_programa_especial_url(conn_stg):
#     job = Job("Carrega programa especial - URL")

#     cols_saida = [  
#         ["ID_PROGRAMA", tp.NUMBER],
#         ["ANO_PROGRAMA", tp.NUMBER],
#         ["MODALIDADE_PROGRAMA", tp.STRING],
#         ["CODIGO_PROGRAMA", tp.STRING],
#         ["ID_ORGAO_SUPERIOR_PROGRAMA", tp.NUMBER],
#         ["SIGLA_ORGAO_SUPERIOR_PROGRAMA", tp.STRING],
#         ["NOME_ORGAO_SUPERIOR_PROGRAMA", tp.STRING],
#         ["ID_ORGAO_PROGRAMA", tp.NUMBER],
#         ["SIGLA_ORGAO_PROGRAMA", tp.STRING],
#         ["NOME_ORGAO_PROGRAMA", tp.STRING],
#         ["ID_UNIDADE_GESTORA_PROGRAMA", tp.NUMBER],
#         ["DOCUMENTOS_ORIGEM_PROGRAMA", tp.STRING],
#         ["ID_UNIDADE_ORCAMENTARIA_RESPONSAVEL_PROGRAMA", tp.NUMBER],
#         ["DATA_INICIO_CIENCIA_PROGRAMA", tp.DATE, FormataData()],
#         ["DATA_FIM_CIENCIA_PROGRAMA", tp.DATE, FormataData()],
#         ["VALOR_NECESSIDADE_FINANCEIRA_PROGRAMA", tp.NUMBER],
#         ["VALOR_TOTAL_DISPONIBILIZADO_PROGRAMA", tp.NUMBER],
#         ["VALOR_IMPEDIDO_PROGRAMA", tp.NUMBER],
#         ["VALOR_A_DISPONIBILIZAR_PROGRAMA", tp.NUMBER],
#         ["VALOR_DOCUMENTOS_HABEIS_GERADOS_PROGRAMA", tp.NUMBER],
#         ["VALOR_OBS_GERADAS_PROGRAMA", tp.NUMBER],
#         ["VALOR_DISPONIBILIDADE_ATUAL_PROGRAMA", tp.NUMBER]
#     ]

#     job.importa_json_url(
#         conn_stg,
#         "API_PROGRAMA",
#         cols_saida,
#         "https://api.transferegov.gestao.gov.br/transferenciasespeciais/programa_especial",
#         TpJson.LIST)
#         # estrategia=TpEstrategia.UPDATE_INSERT,
#         # cols_chave_update=["ID_PROGRAMA"],
#         # cols_entrada=[0,0,2],

# def carrega_documento_habil_especial(conn_stg):
#     job = Job("Carrega documento hábil especial")

#     cols_saida = [  
#         ["ID_DH", tp.NUMBER],
#         ["ID_MINUTA_DOCUMENTO_HABIL", tp.STRING],
#         ["NUMERO_DOCUMENTO_HABIL", tp.STRING],
#         ["SITUACAO_DH", tp.NUMBER],
#         ["DESCRICAO_SITUACAO_DH", tp.STRING],
#         ["TIPO_DOCUMENTO_DH", tp.STRING],
#         ["UG_EMITENTE_DH", tp.NUMBER],
#         ["DESCRICAO_UG_EMITENTE_DH", tp.STRING],
#         ["DATA_VENCIMENTO_DH", tp.DATE, FormataData()],
#         ["DATA_EMISSAO_DH", tp.DATE, FormataData()],
#         ["UG_PAGADORA_DH", tp.NUMBER],
#         ["DESCRICAO_UG_PAGADORA_DH", tp.STRING],
#         ["VARIACAO_PATRIMONIAL_DIMINUTA_DH", tp.STRING],
#         ["PASSIVO_TRANS_LEGAL_DH", tp.STRING],
#         ["CENTRO_CUSTO_EMPENHO", tp.STRING],
#         ["CODIGO_SIORG_EMPENHO", tp.NUMBER],
#         ["MES_REFERENCIA_EMPENHO", tp.STRING],
#         ["ANO_REFERENCIA_EMPENHO", tp.NUMBER],
#         ["UG_BENEFICIADA_DH", tp.NUMBER],
#         ["DESCRICAO_UG_BENEFICIADA_DH", tp.STRING],
#         ["VALOR_DH", tp.NUMBER],
#         ["VALOR_RATEIO_DH", tp.NUMBER],
#         ["ID_EMPENHO", tp.NUMBER]
#     ]

#     job.importa_json_url(
#         conn_stg,
#         "DOC_HABIL_ESPECIAL",
#         cols_saida,
#         "https://api.transferegov.gestao.gov.br/transferenciasespeciais/documento_habil_especial",
#         TpJson.LIST)
#         # cols_entrada=[0,2],


# def carrega_entes_url(conn_stg):
#     job = Job("Carrega entes")

#     cols_saida = [  
#         ["COD_IBGE", tp.NUMBER],
#         # ["ENTE", tp.STRING],
#         ["ENTE", tp.STRING, ft.DeParaChar({
#             "Sao ": "São ",
#             "Belem": "Belém"
#             })],
#         ["CAPITAL", tp.STRING],
#         ["REGIAO", tp.STRING],
#         ["UF", tp.STRING],
#         ["ESFERA", tp.STRING],
#         ["EXERCICIO", tp.NUMBER],
#         ["POPULACAO", tp.NUMBER],
#         ["CNPJ", tp.STRING]
#     ]

#     job.importa_json_url(
#         conn_stg,
#         "ENTES",
#         cols_saida,
#         "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes",
#         TpJson.DICT,
#         "items")


# def carrega_entes_str(conn_stg):
#     job = Job("Carrega entes")


#     dados_json = '{"items": [{"cod_ibge": 3304904, "ente": "Sao Goncalo", "capital": "0  ", "regiao": "SE", "uf": "RJ", "esfera": "M", "exercicio": 2024, "populacao": 929446, "cnpj": "28636579000100"}], "hasMore": 0, "limit": 6000, "offset": 0, "count": 5597, "links": [{"rel": "self", "href": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes"}, {"rel": "describedby", "href": "https://apidatalake.tesouro.gov.br/ords/siconfi/metadata-catalog/tt/item"}, {"rel": "first", "href": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes"}]}'

#     cols_saida = [  
#         ["COD_IBGE", tp.NUMBER],
#         ["ENTE", tp.STRING],
#         ["CAPITAL", tp.STRING],
#         ["REGIAO", tp.STRING],
#         ["UF", tp.STRING],
#         ["ESFERA", tp.STRING],
#         ["EXERCICIO", tp.NUMBER],
#         ["POPULACAO", tp.NUMBER],
#         ["CNPJ", tp.STRING]
#     ]

#     job.importa_json_str(
#         conn_stg,
#         "ENTES",
#         cols_saida,
#         dados_json,
#         TpJson.DICT,
#         "items")


# def carrega_entes_arquivo(conn_teste):
#     job = Job("Carrega entes - arquivo")

#     cols_saida = [  
#         ["COD_IBGE", tp.NUMBER],
#         ["ENTE", tp.STRING],
#         # ["ENTE", tp.STRING, ft.DeParaChar({
#         #     "Sao ": "São ",
#         #     "Belem": "Belém"
#         #     })],
#         ["CAPITAL", tp.STRING],
#         ["REGIAO", tp.STRING],
#         ["UF", tp.STRING],
#         ["ESFERA", tp.STRING],
#         ["EXERCICIO", tp.NUMBER],
#         ["POPULACAO", tp.NUMBER],
#         ["CNPJ", tp.STRING]
#     ]

#     job.importa_json_arquivo(
#         conn_teste,
#         "ENTES",
#         cols_saida,
#         "teste.json",
#         TpJson.DICT,
#         "items")


# if __name__ == "__main__":
#     try:
#         conn_teste, = ConexaoBD.from_json([2])

#         # carrega_programa_especial(conn_stg)

#         # carrega_programa_especial_url(conn_stg)

#         # carrega_documento_habil_especial(conn_stg)

#         # carrega_entes_url(conn_stg)

#         # carrega_entes_str(conn_stg)

#         carrega_entes_arquivo(conn_teste)

#     except Exception as e:
#         print(e)
#         raise


# class FormataNumero():
#     def transforma(self, entradas):
#         if entradas[0] is not None:
#             return entradas[0] / 100

# from datetime import datetime
# class StrParaData():
#     def transforma(self, entradas):
#         if entradas[0] is not None:
#             return datetime.strptime(entradas[0][:10], "%d/%m/%Y")
#         else:
#             return None

# class FormataData2():
#     def transforma(self, entradas):
#         if entradas[0] is not None:
#             return datetime.strptime(entradas[0], "%Y-%m-%d %H:%M:%S")
#         else:
#             return None
 
# from blipy.enum_tipo_col_bd import TpColBD
# class StrToFloat():
#     def transforma(self, entradas):
#         if entradas[0] is not None and str(entradas[0]) != "nan":
#             return float(entradas[0])
#         else:
#             return None

# def carrega_arquivo_posicional(conn_stg):
#     job = Job("Carrega arquivo posicional")

#     cols_saida = [  
#         ["ANO", tp.NUMBER],
#         ["MES", tp.NUMBER],
#         ["NOME", tp.STRING],
#         # ["NOME", tp.STRING, StrToFloat()],
#         ["CODIGO", tp.NUMBER],
#         ["DIA", tp.DATE, StrParaData()],
#         # ["DIA", tp.DATE, FormataData2()],
#         # ["VALOR", tp.NUMBER, FormataNumero()],
#         ["VALOR", tp.NUMBER],
#         ["DATA1", tp.DATE, ft.StrParaData(ft.TpData.BR)], 
#         # ["DATA1", tp.DATE, ft.MontaDataMesAno(31, trata_ult_dia=True)], 
#         # ["DATA2", tp.DATE, ft.MontaDataMesAno(19)], 
#         ["DATA2", tp.DATE, ft.StrParaData(ft.TpData.UN)], 
#         ["DATA3", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)], 
#         # ["DATA4", tp.DATE, ft.FormataData(ft.FmtDt.BR_SO_NUMEROS)], 
#         # ["DATA4", tp.DATE, ft.FormataData(ft.FmtDt.BR_SN)], 
#         # ["DATA4", tp.DATE, ft.StrParaData("%m%Y%d %H:%M:%S", ignora_horario=False)], 
#         # ["DATA4", tp.DATE, ft.StrParaData("%m%Y%d %H:%M:%S", ignora_horario=False)], 
#         ["DATA4", tp.DATE, ft.StrParaData(ft.TpData.UN_SN)], 
#     ]

#     job.importa_arquivo_csv(
#         conn_stg,
#         "ARQPOS",
#         cols_saida,
#         "arqpos_teste.csv",
#         decimal=",",
#         thousands=".",
#         # uso_cols=[0, 1, 2, 3, 4, 5, [1, 0], 7, 8, 9],
#         uso_cols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
#         # qtd_linhas=2,
#         # header=1,
#         # engine="python",
#         # engine="c",
#         # skipfooter=None, 
#         skiprows=1,
#     )

    # tp_cols_entrada = [
    #     TpColBD.NUMBER, 
    #     TpColBD.NUMBER,
    #     TpColBD.NUMBER,
    #     TpColBD.NUMBER
    # ]

    # job.importa_planilha(
    #     conn_stg,
    #     "ARQPOS",
    #     cols_saida,
    #     "arqpos_teste.xlsx",
    #     # decimal=",",
    #     # thousands=".",
    #     # header=1,
    #     qtd_linhas=3,
    #     # engine="python",
    #     # engine="c",
    #     # skipfooter=1, 
    #     skiprows=2,
    # )

    # job.importa_arquivo_posicional(
    #     conn_stg,
    #     "ARQPOS",
    #     cols_saida,
    #     "arqpos_teste.txt",
    #     [4, 2, 10, 5, 10, 10],
    #     # header=2,
    #     # qtd_linhas=5,
    #     # skipfooter=2,
    #     # skiprows=1,
    #     # cols_entrada=[4,5],
    #     # decimal=",",
    #     # thousands=".",
    #     # header=2,
    #     # cols_entrada=[0,3]) 
    #     # tp_cols_entrada=[tp.DATE, tp.NUMBER, tp.NUMBER, tp.NUMBER])
    #     # decimal=",",
    #     # cols=[0, 1, 2, 3],
    #     # ordem_uso_cols=[1, 1, 2, 3],
    #     # tp_cols_entrada=tp_cols_entrada,
    #     # estrategia=TpEstrategia.UPDATE_INSERT,
    #     # cols_chave_update=["ANO", "MES"]
    # )

# def hash(conn_stg):
#     job = Job("Aplica hash")

#     cols_entrada = [
#         "ID_ABRANG",
#         "NO_ABRANG"
#     ]

#     cols_saida = [  
#         ["ID_ABRANG", tp.NUMBER],
#         ["NO_ABRANG_HASH", tp.STRING, ft.HashCPF()]
#     ]

#     job.importa_tabela_por_nome(
#         conn_stg,
#         conn_stg,
#         "ZZ_TESTE_HASH",
#         "ZZ_TESTE_HASH",
#         cols_entrada,
#         cols_saida,
#         estrategia=TpEstrategia.UPDATE,
#         cols_chave_update=["ID_ABRANG"]
#     )
   

# def teste_planilha_python313(conn_teste):
#     job = Job("Teste python 13")

#     cols_saida = [  
#         ["ANO", tp.NUMBER],
#         ["MES", tp.NUMBER],
#         ["NOME", tp.STRING],
#         ["CODIGO", tp.NUMBER],
#         ["DIA", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)],
#         ["VALOR", tp.NUMBER],
#         # ["DATA1", tp.DATE, ft.StrParaData(ft.TpData.BR)], 
#         # ["DATA2", tp.DATE, ft.StrParaData(ft.TpData.UN)], 
#         # ["DATA3", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)], 
#         # ["DATA4", tp.DATE, ft.StrParaData(ft.TpData.UN_SN)], 
#     ]

#     job.importa_planilha(
#         conn_teste,
#         "ARQPOS",
#         cols_saida,
#         "arqpos_teste_python13.xlsx",
#         # decimal=",",
#         # thousands=".",
#         header=1,
#         qtd_linhas=3,
#         skiprows=1,
#     )


    # job.importa_planilha(
    #     conn_teste,
    #     "ARQPOS",
    #     cols_saida,
    #     "arqpos_teste.xlsx",
    #     # decimal=",",
    #     # thousands=".",
    #     header=1,
    #     qtd_linhas=3,
    #     skiprows=1,
    # )


# if __name__ == "__main__":
#     try:
#         # conn_stg, = ConexaoBD.from_json()
#         # hash(conn_stg)

#         conn_teste, = ConexaoBD.from_json([2])
#         teste_planilha_python313(conn_teste)

#     except Exception as e:
#         print(e)
#         # raise
#         # print("except")
#         # raise RuntimeError("Deu pau")
#         # sys.exit(1)

# # teste função transformação Incrementa
# if __name__ == "__main__":
#     try:
#         # conn_stg é STG_COSIS_CATALOGA
#         conn_stg, conn_teste = ConexaoBD.from_json()

#         job = Job("Teste funcão transformação Incrementa")

#         cols_entrada = [
#             "id_unidade", 
#             "id_unidade_pai", 
#             "id_tipo_unidade", 
#             "sg_unidade", 
#             "sg_lotacao", 
#             "no_unidade", ]
#         cols_saida = [
#             ["id_unidade", tp.NUMBER], 
#             ["id_unidade_pai", tp.NUMBER, ft.Incrementa(0, -5)], 
#             ["id_tipo_unidade", tp.NUMBER, ft.Incrementa(-1, -1)], 
#             ["sg_unidade", tp.STRING, ft.Incrementa("k")], 
#             ["sg_lotacao", tp.STRING], 
#             ["no_unidade", tp.STRING] ]
#         sql = """
#             select id_unidade, id_unidade_pai, id_tipo_unidade, sg_unidade, sg_lotacao, no_unidade
#             from MVW_UNIDADE 
#             order by id_unidade"""
#         job.importa_tabela_por_sql(
#             conn_stg,
#             conn_teste,
#             sql, 
#             "UNIDADE", 
#             cols_saida)
#         # job.importa_tabela_por_nome(
#         #     conn_stg,
#         #     conn_teste,
#         #     "MVW_UNIDADE", 
#         #     "UNIDADE", 
#         #     cols_entrada,
#         #     cols_saida)
        
# teste função transformação AlteraCaixa
if __name__ == "__main__":
    try:
        # conn_stg é STG_COSIS_CATALOGA
        conn_stg_cataloga, conn_teste = ConexaoBD.from_json()

        job = Job("Teste funcão transformação AlteraCaixa")

        cols_entrada = [
            "id_unidade", 
            "sg_unidade", 
            "sg_lotacao", 
            "no_unidade", ]
        cols_saida = [
            ["id_unidade", tp.NUMBER], 
            ["sg_unidade", tp.STRING, ft.AlteraCaixa("cxalta")], 
            ["sg_lotacao", tp.STRING, ft.AlteraCaixa("cxalta")], 
            ["no_unidade", tp.STRING, ft.AlteraCaixa("frase")]]
            # ["no_unidade", tp.STRING, ft.AlteraCaixa("titulo")]]
            # ["no_unidade", tp.STRING]]
            # ["no_unidade", tp.STRING, ft.AlteraCaixa("upper")]]
        job.importa_tabela_por_nome(
            conn_stg_cataloga,
            conn_teste,
            "MVW_UNIDADE", 
            "UNIDADE", 
            cols_entrada,
            cols_saida)

    except Exception as e:
        print(e)
        raise
        # sys.exit(1)

