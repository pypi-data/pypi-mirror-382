import sys
sys.path.append('..')

from blipy.conexao_bd import ConexaoBD
from blipy.job import Job, TpEstrategia
from blipy.enum_tipo_col_bd import TpColBD as tp
import blipy.func_transformacao as ft


def teste_oracle(con_stg, con_teste):
    job = Job("Teste Oracle pra Oracle")

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
        #     ft.LookupViaTabela( con_stg,
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
            con_stg, 
            con_teste, 
            "DEMANDA_PAGAMENTO", 
            "OF_DEMANDA_PAGAMENTO",
            cols_entrada, 
            cols_saida)

def teste_xlsx_e_csv(con_teste):
    job = Job("Teste planilha xlsx")

    cols_saida = [  
        ["ANO", tp.NUMBER],
        ["MES", tp.NUMBER],
        ["NOME", tp.STRING],
        ["CODIGO", tp.NUMBER],
        ["DIA", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)],
        ["VALOR", tp.NUMBER],
        # ["DATA1", tp.DATE, ft.StrParaData(ft.TpData.BR)], 
        # ["DATA2", tp.DATE, ft.StrParaData(ft.TpData.UN)], 
        # ["DATA3", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)], 
        # ["DATA4", tp.DATE, ft.StrParaData(ft.TpData.UN_SN)], 
    ]

    job.importa_planilha(
        con_teste,
        "ARQPOS",
        cols_saida,
        "arqpos_teste_python13.xlsx",
        # decimal=",",
        # thousands=".",
        header=1,
        qtd_linhas=3,
        skiprows=1,
    )


    job = Job("Teste planilha csv")
    job.qtd_insercoes_simultaneas = 1

    cols_saida = [  
        ["ANO", tp.NUMBER],
        ["MES", tp.NUMBER],
        ["NOME", tp.STRING],
        ["CODIGO", tp.NUMBER],
        ["DIA", tp.DATE, ft.StrParaData(ft.TpData.BR)],
        ["VALOR", tp.NUMBER],
        ["DATA1", tp.DATE, ft.StrParaData(ft.TpData.BR)], 
        ["DATA2", tp.DATE, ft.StrParaData(ft.TpData.BR_SN)], 
        ["DATA3", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)], 
        ["DATA4", tp.DATE, ft.StrParaData("%m%Y%d %H:%M:%S")], 
    ]

    job.importa_arquivo_csv(
        con_teste,
        "ARQPOS",
        cols_saida,
        "arqpos_teste_python13.csv",
        decimal=",",
        thousands=".",
        # header=1,
        # qtd_linhas=3,
        # skiprows=2,
        estrategia=TpEstrategia.INSERT
    )

def teste_txt(con_teste):
    job = Job("Teste txt")

    cols_saida = [  
        ["ANO", tp.NUMBER],
        ["MES", tp.NUMBER],
        ["NOME", tp.STRING],
        ["CODIGO", tp.NUMBER],
        ["DIA", tp.DATE, ft.StrParaData(ft.TpData.BR)],
        ["VALOR", tp.NUMBER],
        ["DATA1", tp.DATE, ft.StrParaData(ft.TpData.UN_SN)], 
        ["DATA2", tp.DATE, ft.StrParaData(ft.TpData.BR_SN)], 
        # ["DATA3", tp.DATE, ft.StrParaData(ft.TpData.UN_HF)], 
        # ["DATA4", tp.DATE, ft.StrParaData(ft.TpData.UN_SN)], 
    ]

    job.importa_arquivo_posicional(
        con_teste,
        "ARQPOS",
        cols_saida,
        "arqpos_teste_python13.txt",
        [4, 2, 10, 5, 10, 6, 17, 17], 
        # decimal=",",
        # thousands=".",
        # header=1,
        # qtd_linhas=3,
        # skiprows=1,
    )


def teste_jdv(con_jdv, con_teste):
    job = Job("Teste de conexão com JDV")

    select_orgaos = """
        select	CAST (a11.ID_ORGAO AS INTEGER) ID_ORGAO, --Órgão (SIORG)
            trim(max(a11.CO_ORGAO))   CO_ORGAO,
            max(a11.NO_ORGAO)   NO_ORGAO--,
            --trim(a13.CO_SIORG_N05)  CO_SIORG_N05,
            --CAST (a13.ID_ANO AS INTEGER)  ID_ANO,
            --max(a16.DS_SIORG_N05)  DS_SIORG_N05,
            --max(a16.SG_SIORG_N05)  SG_SIORG_N05,
            --trim(a13.CO_SIORG_N06)  CO_SIORG_N06,
            --max(a17.DS_SIORG_N06)  DS_SIORG_N06,
            --max(a17.SG_SIORG_N06)  SG_SIORG_N06,
            --trim(a13.CO_SIORG_N07)  CO_SIORG_N07,
            --max(a18.DS_SIORG_N07)  DS_SIORG_N07,
            --max(a18.SG_SIORG_N07)  SG_SIORG_N07,
            --CAST (a13.ID_PODER_SIORG AS INTEGER)  ID_PODER_SIORG,
            --max(a15.DS_PODER_SIORG)  DS_PODER_SIORG,
            --CAST (a13.ID_NATUREZA_JURIDICA_SIORG AS INTEGER)  ID_NATUREZA_JURIDICA_SIORG,
            --max(a14.DS_NATUREZA_JURIDICA_SIORG)  DS_NATUREZA_JURIDICA_SIORG
        from	WD_ORGAO	a11
            join	WD_ORGAO_EXERCICIO	a12
              on 	(a11.ID_ORGAO = a12.ID_ORGAO)
            join	WD_SIORG_EXERCICIO	a13
              on 	(a12.CO_SIORG = a13.CO_SIORG and 
            a12.ID_ANO = a13.ID_ANO)
            join	WD_NATUREZA_JURIDICA_SIORG	a14
              on 	(a13.ID_NATUREZA_JURIDICA_SIORG = a14.ID_NATUREZA_JURIDICA_SIORG)
            join	WD_PODER_SIORG	a15
              on 	(a13.ID_PODER_SIORG = a15.ID_PODER_SIORG)
            join	WD_SIORG_N05_EXERCICIO	a16
              on 	(a13.CO_SIORG_N05 = a16.CO_SIORG_N05 and 
            a13.ID_ANO = a16.ID_ANO)
            join	WD_SIORG_N06	a17
              on 	(a13.CO_SIORG_N06 = a17.CO_SIORG_N06)
            join	WD_SIORG_N07	a18
              on 	(a13.CO_SIORG_N07 = a18.CO_SIORG_N07)
        where	a13.CO_SIORG_N04 = '000026' -- manter?
        group by	a11.ID_ORGAO,
            a13.CO_SIORG_N05,
            a13.ID_ANO,
            a13.CO_SIORG_N06,
            a13.CO_SIORG_N07,
            a13.ID_PODER_SIORG,
            a13.ID_NATUREZA_JURIDICA_SIORG"""

    cols_saida = [["ID_ORGAO", tp.NUMBER],
                  ["CO_ORGAO", tp.STRING],
                  ["NO_ORGAO", tp.STRING]#,
                  #["CO_SIORG_N05", tp.STRING],
                  #["ID_ANO", tp.NUMBER],
                  #["DS_SIORG_N05", tp.STRING],
                  #["SG_SIORG_N05", tp.STRING],
                  #["CO_SIORG_N06", tp.STRING],
                  #["DS_SIORG_N06", tp.STRING],
                  #["SG_SIORG_N06", tp.STRING],
                  #["CO_SIORG_N07", tp.STRING],
                  #["DS_SIORG_N07", tp.STRING],
                  #["SG_SIORG_N07", tp.STRING],
                  #["ID_PODER_SIORG", tp.NUMBER],
                  #["DS_PODER_SIORG", tp.STRING],
                  #["ID_NATUREZA_JURIDICA_SIORG", tp.NUMBER],
                  #["DS_NATUREZA_JURIDICA_SIORG", tp.STRING]
                  ]
    job.importa_tabela_por_sql(
            con_jdv,
            con_teste,
            select_orgaos,
            "JDV_CUSTOS_ORGAOS",
            cols_saida)
    
def testa_json_url(con_teste):
    from blipy.jsonstring import TpJson
    job = Job("Teste importação JSON de uma URL")

    cols_saida = [  
        ["COD_IBGE", tp.NUMBER],
        # ["ENTE", tp.STRING],
        ["ENTE", tp.STRING, ft.DeParaChar({
            "Sao ": "São ",
            "Belem": "Belém"
            })],
        ["CAPITAL", tp.STRING],
        ["REGIAO", tp.STRING],
        ["UF", tp.STRING],
        ["ESFERA", tp.STRING],
        ["EXERCICIO", tp.NUMBER],
        ["POPULACAO", tp.NUMBER],
        ["CNPJ", tp.STRING]
    ]

    job.importa_json_url(
        con_teste,
        "ENTES",
        cols_saida,
        "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes",
        TpJson.DICT,
        "items")


if __name__ == "__main__":
    try:
        master_job = Job("Teste python 13")

        # con_stg_siseco, con_teste = ConexaoBD.from_json([1, 2])
        # teste_oracle(con_stg_siseco, con_teste)
        # teste_xlsx_e_csv(con_teste)
        # teste_txt(con_teste)
        # testa_json_url(con_teste)

        # con_teste, con_jdv = ConexaoBD.from_json([2, 3])
        # teste_jdv(con_jdv, con_teste)


    except Exception as e:
        print(e)
        raise
        # sys.exit(1)

