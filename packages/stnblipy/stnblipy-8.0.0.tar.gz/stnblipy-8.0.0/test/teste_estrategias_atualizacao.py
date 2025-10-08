import sys
sys.path.append('..')

from blipy.conexao_bd import ConexaoBD
from blipy.job import Job, TpEstrategia
from blipy.enum_tipo_col_bd import TpColBD as tp
import blipy.func_transformacao as ft


def filtra_numero_not_null(registro):
    # return True
    # VALOR_ACUMULADO diferente de null
    if registro[0] is not None:
        return True

    return False

def atualiza_indices(conn_stg):
    job = Job("Carga Indice Calculados")

    # Carga na tabela Valor Indexador 
# TODO: ajeitar and ((0 = 1)) no select abaixo (no talend é um parâmetro "calcula todos os anos", que fica no contexto)
# TODO: lista de códigos em IDX.CO_BCB IN(433,189,196) é mesmo fixa ou foi só pra testes?
    sql_entrada = """
        select 
                DEV_CORPORATIVO.PKG_INDEXADORES.INDEXADOR_NO_ANO(
                    IDX.CO_BCB,
                    EXTRACT(year FROM VI.DT_INDEXADOR),
                    EXTRACT(MONTH FROM VI.DT_INDEXADOR)) 
            AS VALOR_ACUMULADO,
            VI.ID_INDEXADOR,
            VI.DT_INDEXADOR,
            VI.TESTE_STRING
        from 
            VALOR_INDEXADOR VI, INDEXADOR IDX
        where 
            VI.ID_INDEXADOR = IDX.ID_INDEXADOR 
            and IDX.CO_BCB IN (433,189,196) 
            and (
                (0 = 1) 
                or (VI.DT_INDEXADOR = ( select 
                                            max(VI_DENTRO.DT_INDEXADOR) 
                                        from 
                                            VALOR_INDEXADOR VI_DENTRO 
                                        where 
                                            VI.ID_INDEXADOR = VI_DENTRO.ID_INDEXADOR))
            ) 
        order by 
            VI.ID_INDEXADOR, VI.DT_INDEXADOR
        """

    cols_saida = [ 
        ["VA_INDEXADOR", tp.NUMBER],
        ["ID_INDEXADOR", tp.NUMBER, ft.LookupViaTabela(
            conn_stg, 
            "INDEXADOR", 
            "ID_INDEXADOR", 
            "ID_INDEXADOR_PAI",
            filtro="NO_FONTE = 'Calculado STN'")],  
        ["DT_INDEXADOR", tp.DATE],
        ["TESTE_STRING", tp.STRING]    
    ]

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

    job.set_func_pre_processamento(filtra_numero_not_null)
    job.importa_tabela_por_sql(   
            conn_stg, 
            conn_stg, 
            sql_entrada,
            "VALOR_INDEXADOR_TESTE",
            cols_saida,
            # estrategia=TpEstrategia.UPDATE_INSERT,
            # estrategia=TpEstrategia.INSERT_UPDATE,
            estrategia=TpEstrategia.UPDATE,
            # cols_chave_update=["ID_INDEXADOR", "VA_INDEXADOR"]
            cols_chave_update=["ID_INDEXADOR"]
            # cols_chave_update=["ID_INDEXADOR"]
    ) 

def atualiza_planilha_teste(conn_stg, csv):
    job = Job("Carga Indice Calculados")

    # cols_saida = [ 
    #     ["VA_INDEXADOR", tp.NUMBER],
    #     ["ID_INDEXADOR", tp.NUMBER, ft.LookupViaTabela(
    #         conn_stg, 
    #         "INDEXADOR", 
    #         "ID_INDEXADOR", 
    #         "ID_INDEXADOR_PAI",
    #         filtro="NO_FONTE = 'Calculado STN'")],  
    #     ["DT_INDEXADOR", tp.DATE],
    #     ["TESTE_STRING", tp.STRING]    
    # ]

    cols_saida = [ 
        ["VA_INDEXADOR", tp.NUMBER],
        ["ID_INDEXADOR", tp.NUMBER],
        ["DT_INDEXADOR", tp.DATE, ft.ValorFixo("2020-01-01")],
        ["TESTE_STRING", tp.STRING]    
    ]

    if csv:
        job.importa_arquivo_csv(
            conn_stg, 
            "VALOR_INDEXADOR_TESTE",
            cols_saida,
            "teste_carga_indices.csv",
            cols_entrada=[5,2,1,7],
            decimal=",",
            # estrategia=TpEstrategia.UPDATE_INSERT,
            # estrategia=TpEstrategia.INSERT_UPDATE,
            estrategia=TpEstrategia.UPDATE,
            # cols_chave_update=["ID_INDEXADOR", "VA_INDEXADOR"]
            cols_chave_update=["ID_INDEXADOR", "DT_INDEXADOR"]
            # cols_chave_update=["ID_INDEXADOR"]
        )
    else:
        job.importa_planilha(
            conn_stg, 
            "VALOR_INDEXADOR_TESTE",
            cols_saida,
            "teste_carga_indices.xlsx",
            cols_entrada=[5,2,1,7],
            # decimal=",",
            # estrategia=TpEstrategia.UPDATE_INSERT,
            # estrategia=TpEstrategia.INSERT_UPDATE,
            estrategia=TpEstrategia.UPDATE,
            # cols_chave_update=["ID_INDEXADOR", "VA_INDEXADOR"]
            cols_chave_update=["ID_INDEXADOR", "DT_INDEXADOR"]
            # cols_chave_update=["ID_INDEXADOR"]
        )
    
if __name__ == "__main__":
    try:
        conn_stg,  = ConexaoBD.from_json()

        # atualiza_indices(conn_stg)
        # atualiza_planilha_teste(conn_stg, csv=True)
        atualiza_planilha_teste(conn_stg, csv=False)

# TODO: testar carga de registros com insert e delete, pra ver se continuam funcionando
# TODO: testar carga de registros com insert de várias linhas de uma só vez, ao mesmo tempo em que faz update linha a linha; acho que vai funcionar, pois as linhas a serem inseridas vão ficando na memória como já era antes mesmo, independentemente de algumas linhas terem sido atualizadas antes

    except:
        raise
        #sys.exit(1)

