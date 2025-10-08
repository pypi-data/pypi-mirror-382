import sys
sys.path.append('..')

from blipy.conexao_bd import ConexaoBD
from blipy.job import Job, TpEstrategia
from blipy.enum_tipo_col_bd import TpColBD as tp
import blipy.func_transformacao as ft

# # import blipy.utils as utils

# # trim = ft.Trim()


# # domínios dos campos
# categoria_emitente = {
#     None: None, 
#     2222: "Pequeno Produtor Rural", 
#     3333: "Médio Produtor Rural sant'angelo", 
#     4444: "Grande Produtor Rural", 
#     7777: "Repasse a Cooperativa Singular de Crédito", 
#     8888: "Repasse a Cooperativa Central de Crédito", 
#     5555: "Todas Categorias de Produtores Rurais"}

# fase_ciclo_producao = {
#     None: None, 
#     1: "Indeterminado - ENCERRADO",
#     2: "Fundação - ENCERRADO",
#     3: "Renovação - ENCERRADO",
#     4: "Primeiro Desbaste - ENCERRADO",
#     5: "Segundo Desbaste - ENCERRADO",
#     6: "Terceiro Desbaste - ENCERRADO",
#     7: "Primeiro Corte - ENCERRADO",
#     8: "Segundo Corte - ENCERRADO",
#     9: "Terceiro Corte - ENCERRADO",
#     10: "Quarto Corte - ENCERRADO",
#     11: "Corte Raso Final",
#     12: "Corte Raso Intermediário - ENCERRADO",
#     13: "Demais Cortes - ENCERRADO",
#     21: "Semestral",
#     22: "Anual",
#     23: "Bienal",
#     24: "Cria/Recria/Engorda (Ciclo Completo)",
#     50: "Creche - ENCERRADO",
#     51: "Cria ou Multiplicação",
#     52: "Cria/Creche - ENCERRADO",
#     53: "Cria/Recria",
#     54: "Cria/Recria/Engorda - ENCERRADO",
#     55: "Engorda",
#     56: "Recria",
#     57: "Recria e Engorda",
#     58: "Recria/Terminação - ENCERRADO",
#     59: "Terminação - ENCERRADO",
#      0: "Não se aplica",
#     88: "Regime de Integração",
#     61: "Cria e Engorda",
#     25: "Colheita",
#     70: "Criação sob condições de bem-estar animal",
#     90: "Retenção de Matrizes",
#     60: "Engorda em confinamento"}

# fonte_recurso = {
#     None: None, 
#     403: "RECURSOS LIVRES EQUALIZÁVEIS",
#     250: "FACULDADE DE APLICAÇÃO - COMPULSÓRIO",
#     100: "TESOURO NACIONAL",
#     201: "OBRIGATÓRIOS - MCR 6.2",
#     300: "POUPANÇA RURAL - CONTROLADOS - SUBVENÇÃO ECONÔMICA",
#     301: "POUPANÇA RURAL - CONTROLADOS - CONDIÇÕES MCR 6.2",
#     302: "POUPANÇA RURAL - CONTROLADOS - FATOR DE PONDERAÇÃO",
#     303: "POUPANÇA RURAL - LIVRE",
#     402: "RECURSOS LIVRES",
#     405: "FUNDO DE COMMODITIES",
#     501: "FUNDO CONSTITUCIONAL DE FINANCIAMENTO DO NORTE (FNO)",
#     502: "FUNDO CONSTITUCIONAL DE FINANCIAMENTO DO NORDESTE (FNE)",
#     503: "FUNDO CONSTITUCIONAL DE FINANCIAMENTO DO CENTRO-OESTE (FCO)",
#     505: "BNDES/FINAME - EQUALIZÁVEL",
#     650: "FAT - FUNDO DE AMPARO AO TRABALHADOR",
#     800: "FUNCAFE-FUNDO DE DEFESA DA ECONOMIA CAFEEIRA",
#     520: "FUNDO DE TERRAS E DA REFORMA AGRÁRIA",
#     507: "INCRA",
#     600: "GOVERNOS E FUNDOS ESTADUAIS OU MUNICIPAIS",
#     680: "PIS/PASEP",
#     850: "CAPTAÇÃO EXTERNA",
#     990: "OUTRAS FONTES DE RECURSOS NÃO ESPECIFICADAS",
#     900: "ATIVIDADE NÃO FINANCIADA ENQUADRADA NO PROAGRO (MCR 16.8)",
#     450: "INSTR HIBRIDO CAPITAL DÍVIDA-IHCD (Lei 12.793/2013 - Art. 6º) - EQUALIZÁVEL",
#     260: "COMPULSÓRIO SOBRE RECURSOS À VISTA - REFORÇO DO INVESTIMENTO (CIRC 3.745)",
#     430: "LETRA DE CRÉDITO DO AGRONEGÓCIO (LCA) - TAXA LIVRE",
#     506: "BNDES LIVRE",
#     440: "LETRA DE CRÉDITO DO AGRONEGÓCIO (LCA) - TAXA FAVORECIDA",
#     451: "INSTR HIBRIDO CAPITAL DÍVIDA-IHCD (Lei 12.793/2013 - Art. 6º) - LIVRE",
#     222: "Exigibilidade Adicional dos Recursos à Vista - Resolução 5030",
#     202: "EXIGIBILIDADE ADICIONAL DOS RECURSOS À VISTA",
#     304: "EXIGIBILIDADE ADICIONAL DA POUPANÇA RURAL"}

# instrumento_credito = {
#     None: None, 
#      1: "Cédula Rural Pignoratícia - CRP", 
#      2: "Cédula Rural Hipotecária - CRH", 
#      3: "Cédula Rural Pignoratícia e Hipotecária - CRPH", 
#      4: "Nota de Crédito Rural - NCR", 
#     99: "Termo de Adesão ao Proagro - TAP", 
#      9: "Cédula de Produto Rural-CPR (AVAL) - ENCERRADO - CPR", 
#      5: "Cédula de Crédito Bancário - CCB", 
#      6: "Duplicata Rural - DR", 
#      7: "Nota Promissória Rural - NPR", 
#      8: "Outros Instrumentos de Crédito Rural - OIC", 
#     10: "Contrato de Crédito Rural - CAC"}

# programa = {
#     None: None, 
#        1: "PRONAF - PROGRAMA NACIONAL DE FORTALECIMENTO DA AGRICULTURA FAMILIAR",
#      100: "PRLC-BA (PROG RECUP LAVOURA CACAUEIRA BAIANA) ENCERRADO",
#      110: "PRODECER III - PROG COOP NIPO-BRASILEIRA P DESENV DOS CERRADOS - ENCERRADO",
#      151: "PROCAP-AGRO (PROGRAMA DE CAPITALIZAÇÃO DAS COOPERATIVAS DE PRODUÇÃO AGROPECUÁRIAS)",
#      152: "PROIRRIGA - antigo Moderinfra, alterado em 01/07/2021",
#      153: "MODERAGRO - PROGRAMA DE MODERNIZAÇÃO DA AGRICULTURA E CONSERVAÇÃO DE RECURSOS NATURAIS",
#      154: "MODERFROTA - PROGRAMA DE MODERNIZAÇÃO DA FROTA DE TRATORES AGRÍCOLAS E IMPL ASSOC E COLHEITADEIRAS",
#      155: "PRODECOOP - PROGRAMA DE DESENVOLVIMENTO COOPERATIVO PARA AGREGAÇÃO DE VALOR À PRODUÇÃO AGROPECUÁRIA",
#      156: "ABC + Programa para a Adaptação à Mudança do Clima e Baixa Emissão de Carbono",
#      157: "PSI-RURAL - PROG SUSTENTAÇÃO  INVESTIMENTO ENCERRADO",
#      158: "PROCAP-CRED (PROG CAPIT COOP CRÉDITO) ENCERRADO",
#       50: "PRONAMP - PROGRAMA NACIONAL DE APOIO AO MÉDIO PRODUTOR RURAL",
#      159: "MODERMAQ - PROG MOD PARQUE IND NACIONAL - ENCERRADO",
#      200: "PROCERA - PROG ESPECIAL DE CRÉDITO PARA A REFORMA AGRÁRIA - ENCERRADO",
#      240: "ANF - ATIVIDADE NÃO FINANCIADA ENQUADRADA NO PROAGRO",
#      160: "PRI - PROGRAMA DE REFORÇO DO INVESTIMENTO (CIRC 3.745) - ENCERRADO",
#      777: "Linha Crédito Rural inst Res. 4.147/2012 e 4.260/2013 (Demais Agricultores) ENCERRADO",
#      721: "Linha Crédito Rural instit Res. 4.028/2011 (Dívidas Composição e Renegoc PRONAF) - ENCERRADO",
#      722: "Linha Crédito Rural inst Res. 4.029/2011 (Reneg Crédito Fundiário) ENCERRADO",
#      779: "Linha de Crédito Rural instituida pela Res. 4.161/2012 (Produtores de Arroz) ENCERRADO",
#      730: "Linha Crédito Rural inst Res. 4.083/2012 (Enchentes Reg Norte) ENCERRADO",
#      783: "Linha Crédito Rural inst pelas Res 4.189 e 4.212/2013-PRONAF (Estiagem Area Sudene) ENCERRADO",
#      776: "Linha Crédito Rural Inst Res. 4.147/2012 e 4.260/2013 (Agricultores Familiares) ENCERRADO",
#      784: "Linha Credito Rural inst Res. 4.188 e 4.211/2013-Demais Produtores (Estiagem Area Sudene) ENCERRADO",
#      161: "PRORENOVA-RURAL- PROG APOIO  RENOV IMPLANTAÇÃO NOVOS CANAVIAIS- ENCERRADO",
#      162: "INOVAGRO - Programa de Incentivo à Inovação Tecnológica na Produção Agropecuária",
#      163: "PCA - Programa para Construção e Ampliação de Armazéns",
#      201: "PROGRAMA NACIONAL DE CRÉDITO FUNDIÁRIO (PNCF-FTRA)",
#      735: "Linha de Crédito Rural instituida pela Res. 4.126/2012 (Produtores de Maçã) ENCERRADO",
#      785: "Linha Crédito Rural inst  Res. 4.220/2013 (Recursos BNDES-Estiagem Área da Sudene) ENCERRADO",
#      164: "PRORENOVA-IND- PROG APOIO RENOV IMPLANT NOVOS CANAVIAIS - ENCERRADO",
#      165: "PROAQÜICULTURA-PROG APOIO DESENVSETOR AQUÍCOLA - ENCERRADO",
#      888: "Outras Linhas de Crédito Rural não Especificadas - ENCERRADO",
#      786: "Linha de Crédito Rural Instituída pela Res. 4.289/2013 (Renegociação Café Arábica) ENCERRADO",
#       70: "FUNCAFÉ (PROGRAMA DE DEFESA DA ECONOMIA CAFEEIRA)",
#      999: "FINANCIAMENTO SEM VÍNCULO A PROGRAMA ESPECÍFICO",
#      180: "FNO-ABC (PROG FINANC AGRICULTURA BAIXO CARBONO) ENCERRADO"}

# tipo_agricultura = {
#     None: None, 
#     8: "Agroecológica", 
#     3: "Convencional", 
#     7: "Transgênica", 
#     9: "Orgânica", 
#     1: "Exploração Pecuária - ENCERRADO", 
#     0: "Não se aplica", 
#     4: "Floresta Nativa", 
#     6: "Floresta Plantada", 
#     5: "Plantio Direto"}

# tipo_cultivo = {
#     None: None, 
#     14: "Agroecológica - ENCERRADO", 
#      1: "Convencional - ENCERRADO", 
#      2: "Plantio Direto - ENCERRADO", 
#      3: "Cultivo Mínimo", 
#      4: "No Toco - ENCERRADO", 
#      5: "Pré-Germinado", 
#      6: "Estufa - ENCERRADO", 
#      7: "Em Galpão - ENCERRADO", 
#      8: "Hidroponia", 
#      9: "Extrativismo - ENCERRADO", 
#     10: "Pecuária Extensiva - ENCERRADO", 
#     11: "Pecuária Semi-intensiva - ENCERRADO", 
#     12: "Pecuária Intensiva - ENCERRADO", 
#     13: "Pecuária Confinamento - ENCERRADO", 
#      0: "Não se aplica", 
#     21: "Criação em áreas marinhas delimitadas", 
#     22: "Criação em ranário", 
#     25: "cultivo/manejo em floresta pública", 
#     16: "Criação em Tanques Escavados", 
#     18: "Criação em Tanques Redes/Fluxo Contínuo", 
#     15: "CULTIVO PROTEGIDO", 
#     20: "Substrato"}

# enc_financ_complementar = {
#     None: None, 
#      1: "TR", 
#      2: "TJLP", 
#      3: "Outros", 
#      4: "FAM", 
#      5: "CDI", 
#      6: "IRP – Poupança",
#      7: "IPCA",
#      8: "TLP",
#      9: "Sem complemento",
#      0: "Correção cambial",
#     10: "Selic"}

# grao_semente = {
#     None: None, 
#     0: "Não se aplica", 
#     3: "Semente", 
#     8: "Grão/Consumo"}

# tipo_integracao = {
#     None: None, 
#     1: "Consórcio", 
#     3: "Integração Lavoura Pecuária", 
#     4: "Sistemas Agroflorestais", 
#     5: "Integração Lavoura-Pecuária-Floresta/Sistema Agro-Silvo-Pastoril", 
#     2: "Lavoura Solteira", 
#     0: "Não se aplica", 
#     6: "Integração Lavoura-Floresta", 
#     7: "Integração Pecuária-Floresta"}

# tipo_irrigacao = {
#     None: None, 
#      1: "Não Irrigado", 
#      2: "Gotejamento", 
#      3: "Micro-aspersão", 
#      4: "Aspersão", 
#      5: "Xique-Xique", 
#      6: "Pivô", 
#      7: "Canhão", 
#      8: "Auto-Propelido", 
#      9: "Sulcos", 
#     10: "Inundação", 
#      0: "Não se aplica", 
#     11: 'Irrigação com cobertura contra a seca MCR 12-2-3-"c"'}

# tipo_seguro = {
#     None: None, 
#     0: "Não se aplica", 
#     1: "Proagro tradicional", 
#     2: "Proagro mais", 
#     3: "Outro seguro", 
#     9: "Sem adesão a seguro"}

# subprograma = {
#     None: None, 
#        1: "Custeio (MCR 10-4)", 
#        2: "Mais Alimentos (MCR 10-5)", 
#        3: "Agroindústria (investimento) (MCR 10-6)", 
#        4: "Pronaf ABC+ Floresta (MCR 10-7)", 
#        5: "Pronaf ABC+ Semiárido (MCR 10-8)", 
#        6: "Jovem (MCR 10-10)", 
#        7: "Cotas Partes (MCR 10-12)", 
#        8: "Pronaf ABC+ Agroecologia (industrialização) (MCR 10-14)", 
#        9: "Produtivo Orientado (MCR 10-17)", 
#       10: "Financiamento (custeio e comercialização) (MCR 9-2 e 9-3)", 
#       11: "Estocagem", 
#       12: "Aquisição de Café (FAC) (MCR 9-4)", 
#       13: "Contratos de Opções e Mercados Futuros(MCR 9-5)", 
#       14: "Capital de Giro p Ind Café Solúvel Torrefação (MCR 9-6)", 
#       15: "Recuperação de Cafezais Danificados (MCR 9-7)", 
#       16: "Composição de Dívidas  ENCERRADO", 
#       17: "Controle da Doença Vassoura de Bruxa ENCERRADO", 
#       18: "Enxertia de Cacaueiros Tolerantes ENCERRADO", 
#       19: "Recomposição de Estande ENCERRADO", 
#       20: "Investimentos Fixos e Semifixos ENCERRADO", 
#       21: "Aquisição de Glebas de Terras ENCERRADO", 
#       22: "Despesas de Custeio e Adicional do Proagro ENCERRADO", 
#       23: "Integralização Cotas-Partes Cap Social (MCR 11-2)", 
#       24: "Capital de Giro para Cooperativas - Procap-Agro (MCR 11-2)", 
#       25: "Construção e Ampliação de Armazéns - ENCERRADO", 
#       26: 'Agropecuária Irrigada Sustentável (MCR 11-3-1-"a"-I)', 
#       27: "Recuperação de Solos - ENCERRADO", 
#       28: 'Fomentação Prod Benef Industr Acond Armaz (MCR 11-4-"a"-I)', 
#       29: 'Fomentação de Ações de Defesa Animal (MCR 11-4-"a"-II)', 
#       30: "Aquis Tratores Colheitad Implem Associados Novos (MCR 11-5)", 
#       31: "Aquis Tratores Colheitad Implem Associados Usados (MCR 11-5)", 
#       32: 'ABC + Recuperação - (MCR 11-7-1-"c"-I)', 
#       33: 'ABC + Orgânico - (MCR 11-7-1-"c"-II)', 
#       34: 'ABC + Plantio Direto (MCR 11-7-1-"c"-III)', 
#       35: 'ABC + Integração - (MCR 11-7-1-"c"-IV)', 
#       36: 'ABC + Florestas - (MCR 11-7-1-"c"-V)', 
#       37: 'ABC + Ambiental - (MCR 11-7-1-"c"-VI)', 
#       38: 'ABC + Manejo de Resíduos - (MCR 11-7-1-"c"-VII)', 
#       39: 'ABC + Dendê - (MCR 11-7-1-"c"-VIII)', 
#       40: "Fixação Biológica de Nitrogênio - ENCERRADO", 
#       41: "Ampliação Modernização de Armazéns Existentes (MCR 11-9)", 
#       42: "Construção de Armazéns Novos (MCR 11-9)", 
#       43: "Plantio Direto ENCERRADO", 
#       44: "Recuperação de Pastagens ENCERRADO", 
#       45: "Integ Lav Pec Flor Sist Agroflorestais ENCERRADO", 
#       46: "Florestas ENCERRADO", 
#       47: "Trat Dejetos e Resíduos ENCERRADO", 
#       48: "Fixação Biológica de Nitrogênio ENCERRADO", 
#       49: "Consolidação da Agricultura Familiar ENCERRADO", 
#       50: "Combate a Pobreza Rural ENCERRADO", 
#       51: "Nossa Primeira Terra ENCERRADO", 
#       52: "Pronaf ABC+ Bioeconomia (MCR 10-16)", 
#       53: "Pronaf Industrialização Agroind. Familiar (MCR10-11)", 
#       54: "Reforma Agrária Beneficiários PNCF, PNRA, PCRF(MCR10-3)", 
#       55: "Reforma agrária (microcrédito) ENCERRADO", 
#       56: "Microcrédito Produtivo Rural - Grupo B (MCR 10-13)", 
#       57: "Mulher (MCR 10-9)", 
#       58: "Finan Recursos Fundos Constitucionais ENCERRADO", 
#       60: "PRONAMP -  ENCERRADO", 
#       62: 'Açaí, Cacau, Oliveira, Nogueira (MCR 11-7-1-"d"-X) ENCERRADO', 
#       59: 'Produção em Ambiente Protegido (MCR 11-3-1-"a"-II)', 
#       63: "Financiamentos com Recursos da Poupança Rural ENCERRADO", 
#       64: 'Construção e Ampliação de Instalações (MCR 11-4-"a"-IV)', 
#     9999: "FGPP - Res4801 Art 2 ENCERRADO", 
#     1234: "Pronaf ABC+ Bioeconomia Silvicultura ENCERRADO", 
#     1235: 'ABC + Manejo dos Solos - (MCR 11-7-1-"c"-XI)', 
#     1240: 'ABC + Bioinsumos -  (MCR 11-7-1-"c"-IX)', 
#     6789: "PNCF Social", 
#     6790: "PNCF Mais", 
#     6791: "PNCF Empreendedor", 
#       65: 'Fruticultura clima temperado Granizo (MCR 11-3-1-"a"-III)'}

# situacao = {
#     None: None, 
#      1: "Curso normal", 
#      2: "Em atraso", 
#      3: "Prorrogada", 
#      4: "Renegociada Sem Nova Operação", 
#      5: "Renegociada Parcialmente Com Nova Operação", 
#      6: "Renegociada Totalmente Com Nova Operação", 
#      7: "Liquidada", 
#      8: "Desclassificada", 
#      9: "Baixada como Prejuízo", 
#     10: "Excluída", 
#     11: "Inscrita em Dívida Ativa da União", 
#     12: "Inadimplente", 
#     13: "Desclassificada Parcialmente"}

# import numpy as np
# from datetime import datetime
# class FormataData():
#     def transforma(self, entradas):
#         if entradas[0] is not np.nan:
#             return datetime.strptime(entradas[0][:10], "%m/%d/%Y")
#         else:
#             return entradas[0]
# formata_data = FormataData()

# def __carrega_operacao_basica_estados(conn_stg):
#     job = Job("Carga dos dados de Operação Básica Estado")
#     job.qtd_insercoes_simultaneas = 20000

#     # arq_csv_anterior = "SICOR_OPERACAO_BASICA_ESTADO_2018_ATUAL.anterior.csv"
#     # arq_csv_atualizado =  "SICOR_OPERACAO_BASICA_ESTADO_2018_ATUAL"

#     arq_reg_incluidos = "SICOR_OPERACAO_BASICA_ESTADO_2018_ATUAL.25k.csv"
#     # arq_reg_incluidos = "SICOR_OPERACAO_BASICA_ESTADO_2018_ATUAL.3k.csv"
#     arq_reg_excluidos = None
#     # arq_csv_anterior = "SICOR_OPERACAO_BASICA_ESTADO_2018_ATUAL.25k.anterior.csv"
#     # arq_csv_atualizado =  "teste_atualizado.csv"

#     if arq_reg_incluidos is not None:
#         # insere os registros novos e os alterados
#         cols_saida = [  ["CO_REF_BACEN", tp.NUMBER], 
#                         ["NR_ORDEM", tp.NUMBER], 
#                         ["CO_CNPJ_IF", tp.NUMBER], 
#                         ["DT_EMISSAO", tp.DATE, formata_data], 
#                         ["DT_VENCIMENTO", tp.DATE, formata_data],
#                         ["DS_INST_CREDITO", tp.STRING, 
#                             ft.DePara(  instrumento_credito, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_CATEG_EMITENTE", tp.STRING, 
#                             ft.DePara(  categoria_emitente, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_FONTE_RECURSO", tp.STRING, 
#                             ft.DePara(  fonte_recurso, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["CO_CNPJ_AGENTE_INVEST", tp.NUMBER], 
#                         ["SG_ESTADO", tp.STRING],
#                         ["CO_REF_BACEN_INVESTIMENTO", tp.NUMBER], 
#                         ["DS_TIPO_SEGURO", tp.STRING, 
#                             ft.DePara(  tipo_seguro, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["CO_EMPREENDIMENTO", tp.NUMBER], 
#                         ["DS_PROGRAMA", tp.STRING, 
#                             ft.DePara(  programa, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_TIPO_ENCARG_FINANC", tp.STRING, 
#                             ft.DePara(  enc_financ_complementar, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_TIPO_IRRIGACAO", tp.STRING, 
#                             ft.DePara(  tipo_irrigacao, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_TIPO_AGRICULTURA", tp.STRING, 
#                             ft.DePara(  tipo_agricultura, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_FASE_CICLO_PRODUCAO", tp.STRING, 
#                             ft.DePara(  fase_ciclo_producao, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_TIPO_CULTIVO", tp.STRING, 
#                             ft.DePara(  tipo_cultivo, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_TIPO_INTGR_CONSOR", tp.STRING, 
#                             ft.DePara(  tipo_integracao, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["DS_TIPO_GRAO_SEMENTE", tp.STRING, 
#                             ft.DePara(  grao_semente, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["VL_ALIQ_PROAGRO", tp.NUMBER], 
#                         ["VL_JUROS", tp.NUMBER], 
#                         ["VL_PRESTACAO_INVESTIMENTO", tp.NUMBER], 
#                         ["VL_PREV_PROD", tp.NUMBER], 
#                         ["VL_QUANTIDADE", tp.NUMBER], 
#                         ["VL_RECEITA_BRUTA_ESPERADA", tp.NUMBER], 
#                         ["VL_PARC_CREDITO", tp.NUMBER], 
#                         ["VL_REC_PROPRIO", tp.NUMBER], 
#                         ["VL_PERC_RISCO_STN", tp.NUMBER], 
#                         ["VL_PERC_RISCO_FUNDO_CONST", tp.NUMBER], 
#                         ["VL_REC_PROPRIO_SRV", tp.NUMBER], 
#                         ["VL_AREA_FINANC", tp.NUMBER], 
#                         ["DS_SUBPROGRAMA", tp.STRING, 
#                             ft.DePara(  subprograma, 
#                                         copia_se_nao_encontrado=False,
#                                         trim=True)], 
#                         ["VL_PRODUTIV_OBTIDA", tp.NUMBER], 
#                         ["DT_FIM_COLHEITA", tp.DATE, formata_data], 
#                         ["DT_FIM_PLANTIO", tp.DATE, formata_data], 
#                         ["DT_INIC_COLHEITA", tp.DATE, formata_data], 
#                         ["DT_INIC_PLANTIO", tp.DATE, formata_data], 
#                         ["VL_JUROS_ENC_FINAN_POSFIX", tp.NUMBER], 
#                         ["VL_PERC_CUSTO_EFET_TOTAL", tp.NUMBER], 
#                         ["CO_CONTRATO_STN", tp.STRING]]

#         # determina explicitamente os tipos das colunas de entrada, pois
#         # nas colunas onde é feito o de/para os tipos de entrada são
#         # diferentes dos tipos de saída (os tipos de entrada são numéricos
#         # mas os tipos de saída são strings)
#         tp_cols_entrada = [
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.DATE, tp.DATE, tp.NUMBER,
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.STRING, tp.NUMBER,
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER,
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER,
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER,
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER,
#             tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.NUMBER, tp.DATE, tp.DATE,
#             tp.DATE, tp.DATE, tp.NUMBER, tp.NUMBER, tp.STRING]
#         job.importa_arquivo_csv(
#             conn_stg, 
#             "TABELA_SICOR", 
#             cols_saida,
#             arq_reg_incluidos,
#             tp_cols_entrada=tp_cols_entrada, 
#             estrategia=TpEstrategia.INSERT)

# if __name__ == "__main__":
    # from blipy.tabela_entrada import TabelaEntrada
    # try:
    #     job = Job("Teste de conexão com JDV")
    # 
    #     conn_stg, conn_jdv  = ConexaoBD.from_json()
    # 
    #     cols_saida = [["CO_ABA", tp.NUMBER]]
    #     job.importa_tabela_por_sql(
    #             conn_jdv,
    #             conn_stg,
    #             "select distinct(id_aba) from wd_aba",
    #             "TESTE_JDV",
    #             cols_saida)
    #     
    #     entrada_jdv = TabelaEntrada(conn_jdv)
    #     entrada_jdv.carrega_dados("select distinct(id_aba) from wd_aba")
    #     entrada_jdv.recarrega_dados()
    # except Exception as err:
    #     print(err)
    #     raise

    # try:
    #     conn_stg, = ConexaoBD.from_json()
    #     __carrega_operacao_basica_estados(conn_stg)

    # except Exception as err:
    #     print(err)
    #     raise err
    #     pass





# from blipy.conexao_bd import ConexaoBD
# from blipy.job import Job, TpEstrategia
# from blipy.enum_tipo_col_bd import TpColBD as tp
# 
# # select_orgaos = """select	a11.ID_ORGAO  ID_ORGAO, --Órgão (SIORG)
# select_orgaos = """select	CAST (a11.ID_ORGAO AS INTEGER) ID_ORGAO, --Órgão (SIORG)
#     trim(max(a11.CO_ORGAO))   CO_ORGAO,
#     max(a11.NO_ORGAO)   NO_ORGAO--,
#     --trim(a13.CO_SIORG_N05)  CO_SIORG_N05,
#     --CAST (a13.ID_ANO AS INTEGER)  ID_ANO,
#     --max(a16.DS_SIORG_N05)  DS_SIORG_N05,
#     --max(a16.SG_SIORG_N05)  SG_SIORG_N05,
#     --trim(a13.CO_SIORG_N06)  CO_SIORG_N06,
#     --max(a17.DS_SIORG_N06)  DS_SIORG_N06,
#     --max(a17.SG_SIORG_N06)  SG_SIORG_N06,
#     --trim(a13.CO_SIORG_N07)  CO_SIORG_N07,
#     --max(a18.DS_SIORG_N07)  DS_SIORG_N07,
#     --max(a18.SG_SIORG_N07)  SG_SIORG_N07,
#     --CAST (a13.ID_PODER_SIORG AS INTEGER)  ID_PODER_SIORG,
#     --max(a15.DS_PODER_SIORG)  DS_PODER_SIORG,
#     --CAST (a13.ID_NATUREZA_JURIDICA_SIORG AS INTEGER)  ID_NATUREZA_JURIDICA_SIORG,
#     --max(a14.DS_NATUREZA_JURIDICA_SIORG)  DS_NATUREZA_JURIDICA_SIORG
# from	WD_ORGAO	a11
#     join	WD_ORGAO_EXERCICIO	a12
#       on 	(a11.ID_ORGAO = a12.ID_ORGAO)
#     join	WD_SIORG_EXERCICIO	a13
#       on 	(a12.CO_SIORG = a13.CO_SIORG and 
#     a12.ID_ANO = a13.ID_ANO)
#     join	WD_NATUREZA_JURIDICA_SIORG	a14
#       on 	(a13.ID_NATUREZA_JURIDICA_SIORG = a14.ID_NATUREZA_JURIDICA_SIORG)
#     join	WD_PODER_SIORG	a15
#       on 	(a13.ID_PODER_SIORG = a15.ID_PODER_SIORG)
#     join	WD_SIORG_N05_EXERCICIO	a16
#       on 	(a13.CO_SIORG_N05 = a16.CO_SIORG_N05 and 
#     a13.ID_ANO = a16.ID_ANO)
#     join	WD_SIORG_N06	a17
#       on 	(a13.CO_SIORG_N06 = a17.CO_SIORG_N06)
#     join	WD_SIORG_N07	a18
#       on 	(a13.CO_SIORG_N07 = a18.CO_SIORG_N07)
# where	a13.CO_SIORG_N04 = '000026' -- manter?
# group by	a11.ID_ORGAO,
#     a13.CO_SIORG_N05,
#     a13.ID_ANO,
#     a13.CO_SIORG_N06,
#     a13.CO_SIORG_N07,
#     a13.ID_PODER_SIORG,
#     a13.ID_NATUREZA_JURIDICA_SIORG"""
# 
# if __name__ == '__main__':
#     try:
#         job = Job("Teste de conexão com JDV")
# 
#         conn_stg, conn_jdv  = ConexaoBD.from_json()
# 
#         cols_saida = [["ID_ORGAO", tp.NUMBER],
#                       ["CO_ORGAO", tp.STRING],
#                       ["NO_ORGAO", tp.STRING]#,
#                       #["CO_SIORG_N05", tp.STRING],
#                       #["ID_ANO", tp.NUMBER],
#                       #["DS_SIORG_N05", tp.STRING],
#                       #["SG_SIORG_N05", tp.STRING],
#                       #["CO_SIORG_N06", tp.STRING],
#                       #["DS_SIORG_N06", tp.STRING],
#                       #["SG_SIORG_N06", tp.STRING],
#                       #["CO_SIORG_N07", tp.STRING],
#                       #["DS_SIORG_N07", tp.STRING],
#                       #["SG_SIORG_N07", tp.STRING],
#                       #["ID_PODER_SIORG", tp.NUMBER],
#                       #["DS_PODER_SIORG", tp.STRING],
#                       #["ID_NATUREZA_JURIDICA_SIORG", tp.NUMBER],
#                       #["DS_NATUREZA_JURIDICA_SIORG", tp.STRING]
#                       ]
#         job.importa_tabela_por_sql(
#                 conn_jdv,
#                 conn_stg,
#                 select_orgaos,
#                 "CUSTOS_ORGAOS",
#                 cols_saida)
#         
#     except Exception as err:
#         print(err)
#         raise


# if __name__ == '__main__':
#     job = Job("Teste")
# 
#     try:
#         conn_teste, = ConexaoBD.from_json()
# 
#         cols_saida = [ ["ID_ABRANG", tp.NUMBER],
#                        ["QT_PONTOS1", tp.NUMBER],
#                        ["QT_PONTOS2", tp.NUMBER]]
#         job.importa_planilha(   
#                 conn_teste, 
#                 "ZZ_TESTE",
#                 cols_saida,
#                 "teste.xlsx", 
#                 usecols=[1,2,3],
#                 skiprows=0,
#                 # thousands=".",
#                 estrategia=TpEstrategia.INSERT)
# 
#     except Exception as err:
#         print(err)
#         raise


# class MeuSomatorio():
#     def transforma(self, entradas):
#         if entradas[3] == "S":
#             return ft.Somatorio().transforma(entradas[:3])

#         return None

# if __name__ == '__main__':
#     job = Job("Teste")

#     try:
#         conn_teste, = ConexaoBD.from_json()

#         cols_entrada = ["ID_CHAVE",
#                         "QT_VALOR1",
#                         "QT_VALOR2",
#                         "QT_VALOR3",
#                         ["QT_VALOR1", "QT_VALOR2", "QT_VALOR3", "SN_CONDICAO"],
#                         "SN_CONDICAO"]
#         cols_saida = [ ["ID_CHAVE", tp.NUMBER],
#                        ["QT_VALOR1", tp.NUMBER],
#                        ["QT_VALOR2", tp.NUMBER],
#                        ["QT_VALOR3", tp.NUMBER],
#                        ["QT_VALOR4", tp.NUMBER, MeuSomatorio()],
#                        ["SN_CONDICAO", tp.STRING]]
#         job.importa_tabela_por_nome(
#                 conn_teste,
#                 conn_teste,
#                 "ZZ_SOMATORIO_IN",
#                 "ZZ_SOMATORIO_OUT",
#                 cols_entrada,
#                 cols_saida)

#     except:
#         raise



# if __name__ == "__main__":
#     try:
#         conn_prd, = ConexaoBD.from_json()

#         job = Job("Teste de carga de fato")

#         # fato FATO_EXEC_RECEITA
#         # cols_entrada = [["ME_EXECUCAO_RECEITA", "AN_EXECUCAO_RECEITA"],
#         #                 ["CO_FONTE_RECURSO_DETALHE", "CO_FONTE_RECURSO"]]
#         # cols_saida = [  ["DATA1", tp.DATE, 
#         #                     ft.MontaDataMesAno(dia=1)],
#         #                 ["VAL1", tp.STRING, 
#         #                     ft.ConcatenaStrings(trim="resultado", sep=" - ")]]
#         # job.importa_tabela_por_nome(   
#         #         conn_stg, 
#         #         conn_prd, 
#         #         "EXECUCAO_RECEITA", 
#         #         "ZZ_TESTE1",
#         #         cols_entrada, 
#         #         cols_saida)

#         dados_entrada = [
#             (1, "Tesouro-Exerc. Corrente"), 
#             (2, "Exercício Corrente"), 
#             (3, "Exercícios Anteriores"), 
#             (6, "Exercícios Anteriores"), 
#             (7, "Operações de Crédito"), 
#             (9, "Recursos Condicionados")]
#         cols_saida = [  ["ID_ABRANG", tp.NUMBER],
#                         ["NO_ABRANG", tp.STRING]]
#         job.importa_valores(conn_prd, "ZZ_TESTE", cols_saida, dados_entrada)

#     except:
#         raise

# if __name__ == "__main__":
#     try:
#         job = Job("Teste inversão sinal")
#         conn_stg, conn_prd = ConexaoBD.from_json()

#         cols_entrada = ["VALOR_INT",
#                         "VALOR_STR",
#                         "VALOR_STR"]
#         cols_saida = [ ["VALOR_INT", tp.NUMBER, ft.InverteSinal()],
#                        ["VALOR_FLOAT", tp.NUMBER, ft.InverteSinal()],
#                        ["VALOR_INT2", tp.NUMBER, ft.InverteSinal()]]
#         job.importa_tabela_por_nome(
#                 conn_stg,
#                 conn_prd,
#                 "ZZ_SOMATORIO_IN",
#                 "ZZ_SOMATORIO_OUT",
#                 cols_entrada,
#                 cols_saida)

#         job.grava_log_atualizacao(conn_prd)

#     except:
#         raise 




import numpy as np
from datetime import datetime
class FormataDataEmpreendimento():
    def transforma(self, entradas):
        if entradas[0] is not np.nan:
            return datetime.strptime(entradas[0][:10], "%d/%m/%Y")
        else:
            return entradas[0]
formata_data_empreendimento = FormataDataEmpreendimento()

def filtra_descricao_comecando_com_A(registro):
    # return True
    # DS_PRODUTO começa com "A"
    if registro[3][:1] == "A":
        return True

    return False

def imprime_data_antes_depois(registro_original, registro_gravado):
    # return
    print(str(registro_original[1]) + " virou " + str(registro_gravado[1]))

if __name__ == "__main__":
    try:
        conn_stg, = ConexaoBD.from_json()
        job = Job("Teste pré e pós func")

        cols_saida = [
            ["CO_EMPREENDIMENTO", tp.NUMBER], 
            ["DT_INICIO", tp.DATE, formata_data_empreendimento], 
            ["DT_FIM", tp.DATE, formata_data_empreendimento], 
            # ["DS_FINALIDADE", tp.STRING], 
            # ["DS_ATIVIDADE", tp.STRING], 
            # ["DS_MODALIDADE", tp.STRING], 
            ["DS_PRODUTO", tp.STRING], 
            # ["DS_VARIEDADE", tp.STRING], 
            # ["DS_CESTA", tp.STRING], 
            # ["DS_ZONEAMENTO", tp.STRING], 
            # ["DS_UNIDADE_MEDIDA", tp.STRING], 
            # ["DS_UNIDADE_MEDIDA_PREVISAO", tp.STRING], 
            ["DS_CONSORCIO", tp.STRING], 
            ["CO_CEDULA_MAE", tp.NUMBER],
            ["CO_TIPO_CULTURA", tp.NUMBER]]

        job.set_func_pre_processamento(filtra_descricao_comecando_com_A)
        job.set_func_pos_processamento(imprime_data_antes_depois)
        job.importa_arquivo_csv(
            conn_stg, 
            "ZZ_EMPREENDIMENTO", 
            cols_saida,
            "Empreendimento.csv",
            sep=",",
            encoding="latin1",
            usecols=[0, 1, 2, 6, 12, 13, 14])
    except:
        raise 

