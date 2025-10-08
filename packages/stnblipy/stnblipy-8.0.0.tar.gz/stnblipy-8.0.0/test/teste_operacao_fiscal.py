import sys
sys.path.append('..')

import blipy.func_transformacao as ft
from blipy.job import Job, TpEstrategia
from blipy.conexao_bd import ConexaoBD
from blipy.enum_tipo_col_bd import TpColBD as tp


class LookupStrParaData:
    def __init__(self, conexao, tabela_lookup, campo, chave):
        self.__conexao          = conexao
        self.__tabela_lookup    = tabela_lookup
        self.__campo            = campo
        self.__chave            = chave

    def transforma(self, entradas):
        ret = ft.LookupViaTabela(
            self.__conexao,
            self.__tabela_lookup,
            self.__campo,
            self.__chave).transforma(entradas)

        ret = ft.StrParaData(ft.TpData.UN_SN, True).transforma((ret, ))

        return ret


def atualiza_dimensoes_siseco(conn_stg, conn_prd):
    job = Job("Carga de Dimensões Siseco")


    # dimensão USUARIO / DEMANDA / DEMANDA_LINHA
    # job.qtd_insercoes_simultaneas=1
    job.copia_tabelas(conn_stg, 
                      conn_prd,
                      tabelas=[["USUARIO",
                                "ID_USUARIO",
                                "CO_CPF",
                                "NO_USUARIO"
                                ], 
                                ["DEMANDA", 
                                 "ID_ARQUIVO_CONFORMIDADE",
                                 "ID_DEMANDA",
                                 "ID_USUARIO_CONFORMIDADE",
                                 "DT_CONFORMIDADE",
                                 "DT_ENVIO_OFICIO",
                                 "CO_SITUACAO",
                                 "TX_MOTIVO_REMOCAO_ATESTE",
                                 "SN_IGNORAR_ATUALIZACAO",
                                 "CO_CALCULO_ATUALIZACAO",
                                 "TX_FALHA_CALCULO_ATUALIZACAO"
                                 ], 
                                ["DEMANDA_LINHA",
                                 "ID_DEMANDA",
                                 "ID_LINHA_DEMANDA",
                                 "ID_ARQUIVO_CONFORMIDADE",
                                 "ID_SEQUENCIAL",
                                 "ID_PAGAMENTO",
                                 "CO_ACAO",
                                 "CO_PI",
                                 "NR_DATA_REFERENCIA",
                                 "NR_DATA_CONCESSAO",
                                 "NR_DATA_INICIO_ATUALIZACAO",
                                 "NR_DATA_PAGAMENTO",
                                 "VL_SMD",
                                 "VL_NOMINAL",
                                 "VL_PAGAMENTO",
                                 "SN_FORMULA_VALIDADA",
                                 "SN_INVALIDADA_USUARIO",
                                 "CO_SMD_VALIDADO",
                                 "CO_SIT_PROC_ORIGINAL",
                                 "TX_LINHA_ARQUIVO_CONFORMIDADE",
                                 "TX_MOTIVO_ALTERACAO_SIT_PROC",
                                 "NR_DATA_PGTO_ORIGINAL_ESTORNO",
                                 "VL_DEVOLUCAO_ESTORNO",
                                 "CO_PAGAMENTO_ORIGINAL_ESTORNO",
                                 "CO_EMPENHO_ORIGINAL_ESTORNO",
                                 "NR_QTD_CONTRATOS"
                                 ]
                            ], 
                      prefixo_tabelas_saida='OF_'
                    )
    

    # dimensão CONFORMIDADE
    cols_entrada = [
        "ID_ARQUIVO_CONFORMIDADE",
        "NO_ARQUIVO_CONFORMIDADE",
        "CO_TIPO",
        "CO_IDENTIFICADOR_ARQUIVO"
    ]
    cols_saida = [  
        ["ID_ARQUIVO_CONFORMIDADE", tp.NUMBER],
        ["NO_ARQUIVO_CONFORMIDADE", tp.STRING],
        ["DS_TIPO", tp.STRING],
        ["CO_ARQUIVO", tp.STRING]        
    ]
    job.importa_tabela_por_nome(
            conn_stg, 
            conn_prd, 
            "ARQUIVO_CONFORMIDADE", 
            "OF_ARQUIVO_CONFORMIDADE",
            cols_entrada, 
            cols_saida)
    

    # dimensão SEQUENCIAL
    cols_entrada = [
        "CO_ACAO",
        "CO_PI",
        "CO_SEQUENCIAL",
        "CO_SEQUENCIAL_PRINCIPAL",
        "CO_SITUACAO",
        "CO_TIPO_PERIODICIDADE",
        "DT_PERIODO_CONTRATACAO_FIM",
        "DT_PERIODO_CONTRATACAO_INICIO",
        "DT_PRAZO_FINAL_REEMBOLSO",
        "ID_FAVORECIDO",
        "ID_GRUPO_FORMULA",
        "ID_SEQUENCIAL",
        "ID_SEQUENCIAL_LOTE",
        "ID_SEQUENCIAL_PRINCIPAL",
        "ID_TIPO_SUBVENCAO",
        "NO_ACAO",
        "NO_FONTE",
        "NO_PROGRAMA",
        "NU_ANO_SAFRA",
        "NU_SPREAD_BANCO",
        "NU_TAXA_MUTUARIO",
        "SN_STATUS",
        "SN_UTILIZADO_CONFORMIDADE",
        "SN_UTILIZADO_PAGAMENTO",
        "TX_MOTIVO_RETORNO",
        "TX_PORTARIA_NORMATIVO",
        "VL_LIMITE_SMDA",
        "ID_FAVORECIDO",
        "ID_FAVORECIDO",
        "ID_TIPO_SUBVENCAO"
    ]
    cols_saida = [  
        ["CO_ACAO", tp.STRING],
        ["CO_PI", tp.STRING],
        ["CO_SEQUENCIAL", tp.STRING],
        ["CO_SEQUENCIAL_PRINCIPAL", tp.STRING],   
        ["CO_SITUACAO", tp.NUMBER],  
        ["CO_TIPO_PERIODICIDADE", tp.NUMBER], 
        ["DT_PERIODO_CONTRATACAO_FIM", tp.DATE], 
        ["DT_PERIODO_CONTRATACAO_INICIO", tp.DATE], 
        ["DT_PRAZO_FINAL_REEMBOLSO", tp.DATE], 
        ["ID_FAVORECIDO", tp.NUMBER], 
        ["ID_GRUPO_FORMULA", tp.NUMBER], 
        ["ID_SEQUENCIAL", tp.NUMBER], 
        ["ID_SEQUENCIAL_LOTE", tp.NUMBER], 
        ["ID_SEQUENCIAL_PRINCIPAL", tp.NUMBER], 
        ["ID_TIPO_SUBVENCAO", tp.NUMBER], 
        ["NO_ACAO", tp.STRING], 
        ["NO_FONTE", tp.STRING], 
        ["NO_PROGRAMA", tp.STRING], 
        ["NU_ANO_SAFRA", tp.NUMBER], 
        ["PE_SPREAD_BANCO", tp.NUMBER], 
        ["PE_TAXA_MUTUARIO", tp.NUMBER], 
        ["SN_STATUS", tp.NUMBER],  
        ["SN_UTILIZADO_CONFORMIDADE", tp.NUMBER],  
        ["SN_UTILIZADO_PAGAMENTO", tp.NUMBER],  
        ["TX_MOTIVO_RETORNO", tp.STRING], 
        ["TX_PORTARIA_NORMATIVO", tp.STRING], 
        ["VL_LIMITE_SMDA", tp.NUMBER],
        ["NO_FAVORECIDO", tp.STRING, ft.LookupViaTabela(conn_stg, 
                                                        "FAVORECIDO", 
                                                        "NO_FAVORECIDO", 
                                                        "ID_FAVORECIDO"
                                                        )],
        ["CO_CNPJ", tp.STRING, ft.LookupViaTabela(conn_stg,
                                                  "FAVORECIDO",
                                                  "CO_CNPJ_RESERVA",
                                                  "ID_FAVORECIDO",
                                                  )],
        ["NO_TIPO_SUBVENCAO", tp.STRING, ft.LookupViaTabela(conn_stg,
                                                            "TIPO_SUBVENCAO",
                                                            "NO_TIPO_SUBVENCAO",
                                                            "ID_TIPO_SUBVENCAO"
                                                            )]
    ]
    job.importa_tabela_por_nome(
            conn_stg, 
            conn_prd, 
            "SEQUENCIAL", 
            "OF_SEQUENCIAL",
            cols_entrada, 
            cols_saida)


def atualiza_fatos_siseco(conn_stg, conn_prd):
    job = Job("Carga das Fatos")

    # carga de GRU_COFIN
    cols_entrada = [
        "ID_ARQUIVO_CONFORMIDADE",
        "ID_DEMANDA",
        "ID_PAGAMENTO",
        "ID_USUARIO_PAGAMENTO",
        "CO_ACAO",
        "CO_PI",
        "DT_CRIACAO",
        "CO_PAGAMENTO",
        "CO_TIPO_PAGAMENTO",


        "CO_SITUACAO",
        "CO_NONCE",
        "DT_PAGAMENTO",
        "CO_EMPENHO",
        "NU_ANO",
        "CO_DH",
        "CO_NS_DH",
        "CO_OP",
        "CO_NS_OP",
        "CO_OB",
        "CO_FONTE",

        "VL_NOMINAL_CONSOLIDADO",
        "VL_PAGAMENTO_CONSOLIDADO",
        "CO_TIPO_ORCAMENTO",
        "VL_DEDUCAO",
        "TX_GRU",
        "CO_REFERENCIA",
        # "ID_DEMANDA",
        



        "CO_PA",
        "CO_NS_PA",
        "CO_NS_PGTO",
        "CO_DF_GR",
        "DT_ASS_GESTOR_FINANCEIRO",
        "DT_ASS_ORDENADOR_DESPESA",
        "DT_INICIO_INTEGRACAO",
        "ID_GESTOR_FINANCEIRO",
        "ID_ORDENADOR_DESPESA", ]

    cols_saida = [  
        ["ID_ARQUIVO_CONFORMIDADE", tp.NUMBER],
        ["ID_DEMANDA", tp.NUMBER],
        ["ID_PAGAMENTO", tp.NUMBER],
        ["ID_USUARIO_PAGAMENTO", tp.NUMBER],
        ["CO_ACAO", tp.STRING],
        ["CO_PI", tp.STRING],
        ["DT_CRIACAO", tp.DATE],
        ["CO_PAGAMENTO", tp.STRING],
        ["DS_TIPO_PAGAMENTO", tp.STRING, 
            ft.DePara(de_para={ 1: "Integrado",
                                2: "Manual"},
                                se_nao_encontrado="copia")],
        ["DS_SITUACAO", tp.STRING],
        ["CO_NONCE", tp.STRING],
        ["DT_PAGAMENTO", tp.DATE],
        ["CO_EMPENHO", tp.STRING],
        ["NU_ANO", tp.NUMBER],
        ["CO_DH", tp.STRING],
        ["CO_NS_DH", tp.STRING],
        ["CO_OP", tp.STRING],
        ["CO_NS_OP", tp.STRING],
        ["CO_OB", tp.STRING],
        ["CO_FONTE", tp.STRING],
        # ["ANO_ORCAMENTO", tp.NUMBER],
        ["VL_NOMINAL_CONSOLIDADO", tp.NUMBER],
        ["VL_PAGAMENTO_CONSOLIDADO", tp.NUMBER],
        ["CO_TIPO_ORCAMENTO", tp.STRING],
        ["VL_DEDUCAO", tp.NUMBER],
        ["TX_GRU", tp.STRING],
        ["CO_REFERENCIA", tp.STRING],
        # ["DT_REFERENCIA", tp.DATE, 
        #     ft.LookupViaTabela( conn_stg,
        #                         "DEMANDA_LINHA",
        #                         "NR_DATA_REFERENCIA",
        #                         "ID_DEMANDA")],
        ["CO_PA", tp.STRING],
        ["CO_NS_PA", tp.STRING],
        ["CO_NS_PGTO", tp.STRING],
        ["CO_DF_GR", tp.STRING],
        ["DT_ASS_GESTOR_FINANCEIRO", tp.DATE],
        ["DT_ASS_ORDENADOR_DESPESA", tp.DATE],
        ["DT_INICIO_INTEGRACAO", tp.DATE],
        ["ID_GESTOR_FINANCEIRO", tp.NUMBER],
        ["ID_ORDENADOR_DESPESA", tp.NUMBER], ]

    # job.qtd_insercoes_simultaneas = 10
    job.importa_tabela_por_nome(
            conn_stg, 
            conn_prd, 
            "DEMANDA_PAGAMENTO", 
            "OF_DEMANDA_PAGAMENTO",
            cols_entrada, 
            cols_saida)
    

def atualiza_dimensoes_sispag(conn_stg, conn_prd):
    job = Job("Carga de Dimensões Sispag")

    # dimensão EXERCICIO / FINALIDADE / ACAO / PI / SITUACAO_DEMANDA
    #          TIPO_ORCAMENTO / SITUACAO_EMPENHO / SITUACAO_VALOR_MES
    job.copia_tabelas(conn_stg, 
                      conn_prd,
                      tabelas=[["EXERCICIO",
                                "ID_EXERCICIO",
                                "AN_EXERCICIO"
                                ],
                                ["FINALIDADE",
                                 "ID_FINALIDADE",
                                 "DS_FINALIDADE",
                                 "ID_ITEM_FINALIDADE",
                                 "SN_ATIVO"
                                ],
                                ["ACAO",
                                 "ID_ACAO",
                                 "CO_ACAO",
                                 "NO_ACAO",
                                 "DS_ACAO"
                                ],
                                ["PI",
                                 "ID_PI",
                                 "CO_PI",
                                 "ID_ACAO",
                                 "DS_PI",
                                 "CO_EVENTO_BACEN",
                                 "CO_FINALIDADE_BACEN",
                                 "CO_PROVISAO"
                                ],
                                ["SITUACAO_DEMANDA",
                                 "ID_SITUACAO_DEMANDA",
                                 "TX_SITUACAO_DEMANDA",
                                 "NR_ORDEM"
                                ],
                                ["TIPO_ORCAMENTO",
                                 "ID_TIPO_ORCAMENTO",
                                 "CO_TIPO_ORCAMENTO",
                                 "DS_TIPO_ORCAMENTO"
                                ],
                                ["SITUACAO_EMPENHO",
                                 "ID_SITUACAO_EMPENHO",
                                 "TX_SITUACAO_EMPENHO"
                                ],
                                ["SITUACAO_VALOR_MES",
                                 "ID_SITUACAO_VALOR_MES",
                                 "TX_SITUACAO_VALOR_MES"
                                ]
                            ]
                    )


def teste_depara(conn_stg, conn_prd):
    job = Job("Teste depara")

    cols_entrada = [
        "ID_ARQUIVO_CONFORMIDADE",
        "ID_DEMANDA",
        "ID_PAGAMENTO",
        "ID_USUARIO_PAGAMENTO",
        "CO_ACAO",
        "CO_PI",
        "DT_CRIACAO",
        # "CO_PAGAMENTO",
        # "CO_TIPO_PAGAMENTO",
        "CO_SITUACAO",
        # "CO_NONCE",
        # "DT_PAGAMENTO",
        # "CO_EMPENHO",
        # "NU_ANO",
        # "CO_DH",
        # "CO_NS_DH",
        # "CO_OP",
        # "CO_NS_OP",
        # "CO_OB",
        # "CO_FONTE",

        # "VL_NOMINAL_CONSOLIDADO",
        # "VL_PAGAMENTO_CONSOLIDADO",
        # "CO_TIPO_ORCAMENTO",
        # "VL_DEDUCAO",
        # "TX_GRU",
        # "CO_REFERENCIA",
        "ID_DEMANDA",
        # "CO_PA",
        # "CO_NS_PA",
        # "CO_NS_PGTO",
        # "CO_DF_GR",
        # "DT_ASS_GESTOR_FINANCEIRO",
        # "DT_ASS_ORDENADOR_DESPESA",
        # "DT_INICIO_INTEGRACAO",
        # "ID_GESTOR_FINANCEIRO",
        # "ID_ORDENADOR_DESPESA",
        
    ]
    cols_saida = [  
        ["ID_ARQUIVO_CONFORMIDADE", tp.NUMBER],
        ["ID_DEMANDA", tp.NUMBER],
        ["ID_PAGAMENTO", tp.NUMBER],
        ["ID_USUARIO_PAGAMENTO", tp.NUMBER],
        ["CO_ACAO", tp.STRING],
        ["CO_PI", tp.STRING],
        ["DT_CRIACAO", tp.DATE],
        # ["CO_PAGAMENTO", tp.STRING],
        # # ["DS_TIPO_PAGAMENTO", tp.STRING, 
        # #      ft.DePara( de_para={1: "Integrado", 2: "Manual"
        # #                         # , None: "Nulo"
        # #                         }, 
        # #                 se_nao_encontrado="erro", 
        # #                 # copia_null=False, 
        # #                 default="Valor incorreto")],
        # ["DS_TIPO_PAGAMENTO", tp.STRING, 
        #     ft.DeParaSN(se_nao_encontrado="null", 
        #                 default="Valor incorreto",
        #                 inverte=True,
        #                 copia_null=False, 
        #                 )],
        ["DS_SITUACAO", tp.STRING],
        # ["CO_NONCE", tp.STRING],
        # ["DT_PAGAMENTO", tp.DATE],
        # ["CO_EMPENHO", tp.STRING],
        # ["NU_ANO", tp.NUMBER],
        # ["CO_DH", tp.STRING],
        # ["CO_NS_DH", tp.STRING],
        # ["CO_OP", tp.STRING],
        # ["CO_NS_OP", tp.STRING],
        # ["CO_OB", tp.STRING],
        # ["CO_FONTE", tp.STRING],
        # # ["ANO_ORCAMENTO", tp.NUMBER],
        # ["VL_NOMINAL_CONSOLIDADO", tp.NUMBER],
        # ["VL_PAGAMENTO_CONSOLIDADO", tp.NUMBER],
        # ["CO_TIPO_ORCAMENTO", tp.STRING],
        # ["VL_DEDUCAO", tp.NUMBER],
        # ["TX_GRU", tp.STRING],
        # ["CO_REFERENCIA", tp.STRING],
        ["DT_REFERENCIA", tp.DATE, 
            LookupStrParaData(
                conn_stg, 
                "DEMANDA_LINHA", 
                "NR_DATA_REFERENCIA", 
                "ID_DEMANDA")],
        # ["CO_PA", tp.STRING],
        # ["CO_NS_PA", tp.STRING],
        # ["CO_NS_PGTO", tp.STRING],
        # ["CO_DF_GR", tp.STRING],
        # ["DT_ASS_GESTOR_FINANCEIRO", tp.DATE],
        # ["DT_ASS_ORDENADOR_DESPESA", tp.DATE],
        # ["DT_INICIO_INTEGRACAO", tp.DATE],
        # ["ID_GESTOR_FINANCEIRO", tp.NUMBER],
        # ["ID_ORDENADOR_DESPESA", tp.NUMBER],
    ]
    job.importa_tabela_por_nome(
            conn_stg, 
            conn_prd, 
            "DEMANDA_PAGAMENTO", 
            "OF_DEMANDA_PAGAMENTO",
            cols_entrada, 
            cols_saida)


if __name__ == "__main__":
    try:
        master_job = Job("Carga do DM Operacao Fiscal")

        conn_stg, conn_prd = ConexaoBD.from_json()

        # teste_depara(conn_stg, conn_prd)
    
        #atualiza_dimensoes_siseco(conn_stg_siseco, conn_prd)
    
        atualiza_fatos_siseco(conn_stg, conn_prd)

        # atualiza_dimensoes_sispag(conn_stg_sispag, conn_prd)
    
        # atualiza_fatos_sispag(conn_stg_sispag, conn_prd)        

        # master_job.grava_log_atualizacao(conn_prd)
    except:
        raise
        # sys.exit(1)

