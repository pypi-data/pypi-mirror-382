
import os
import gzip
import wget
import shutil

import blipy.erro as erro

def gera_dif_arquivos_csv(
        arq_csv_antigo, 
        arq_csv_atualizado, 
        header=None,
        sort=False, 
        sort_command=None,
        diff_command=None):
    """
    Gera arquivos com as diferenças encontradas entre dois arquivos CSV que
    tenham o mesmo formato e que estejam no mesmo diretório. São gerados dois
    arquivos de saída: um arquivo com os registros que foram excluídos de um
    CSV para outro e outro com os registros que foram incluídos. Os registros
    que foram apenas alterados entre um CSV e outro aparecem tanto no arquivo
    de registros excluídos quanto no arquivo de registros incluídos.

    Args:
    arq_csv_antigo:     nome do arquivo CSV com os dados antigos, sem o path
    arq_csv_atualizado: nome do arquivo CSV com os novos dados, sem o path
    header:             header dos arquivos. Esse header tem que ser igual para
                        os dois arquivos de entrada. Se não informado, o header
                        é obtido da primeira linha de arq_csv_antigo. Se
                        informado, considera-se que a primeira linha dos
                        arquivos CSV já contém dados. 
                        IMPORTANTE: este parâmetro deve ter o tipo byte e não
                        string e com um '\n' final, ou seja, deve ser informado
                        como b"campo1;campo2\n" e não "campo1;campo2" por
                        exemplo
    sort:               indica se deve ser feito um sort antes nos arquivos. Se
                        não houver garantia de que a ordem de geração dos
                        registros é a mesma para os dois arquivos, este
                        parâmetro deve ser True
    sort_command:       nome do programa sort que será utilizado, com seu path
                        completo. Por exemplo,
                        "C:\\cmder\\vendor\\git-for-windows\\usr\\bin\\sort.exe".
                        Se não informado, utiliza o sort achado no path da
                        máquina
    diff_command:       nome do programa diff que será utilizado, com seu path
                        completo. Por exemplo,
                        "C:\\cmder\\vendor\\git-for-windows\\usr\\bin\\diff.exe".
                        Se não informado, utiliza o diff achado no path da
                        máquina
    Ret:
    Os dois nomes dos arquivos de diferença, sem o path: primeiro o nome do
    arquivo com os registros incluídos e depois o nome do arquivo com os
    registros excluídos. Se não houver registros incluídos ou excluídos, o
    retorno correspondente é None.
    """

    if header is None:
        with open(arq_csv_antigo, "rb") as f:
            header = f.readline()

    if sort:
        # ordena os arquivos para o diff abaixo poder identificar as diferenças
        # de maneira consistente
        if sort_command is None:
            sort_command = "sort " 
        else:
            sort_command += " "

        os.system(  sort_command + arq_csv_antigo + \
                    " > sort_" + arq_csv_antigo)
        arq_csv_antigo = "sort_" + arq_csv_antigo

        os.system(  sort_command + arq_csv_atualizado + \
                    " > sort_" + arq_csv_atualizado)
        arq_csv_atualizado = "sort_" + arq_csv_atualizado

    if diff_command is None:
        diff_command = "diff " 
    else:
        diff_command += " "
    os.system(  diff_command + arq_csv_antigo + " " + arq_csv_atualizado + 
                " > diff.txt")

    arq_reg_incluidos = "inc_" + arq_csv_antigo
    arq_reg_excluidos = "exc_" + arq_csv_antigo
    houve_inclusao = False
    houve_exclusao = False
    with open(arq_reg_incluidos, "wb") as arq_carga_inclusao:
        arq_carga_inclusao.write(header)

        with open(arq_reg_excluidos, "wb") as arq_carga_exclusao:
            arq_carga_exclusao.write(header)

            with open("diff.txt", "rb") as f:
                for l in f:
                    linha = l[2:]

                    # os registros alterados aparecerão no arquivo de excluídos
                    # e depois no de incluídos, com os novos valores

                    # registros incluídos
                    if l.startswith(b">"):
                        houve_inclusao = True
                        arq_carga_inclusao.write(linha)

                    # registros excluídos
                    if l.startswith(b"<"):
                        houve_exclusao = True
                        arq_carga_exclusao.write(linha)

    return  arq_reg_incluidos if houve_inclusao else None, \
            arq_reg_excluidos if houve_exclusao else None

def descompacta_arquivo(arq_compactado):
    """
    Descompacta um arquivo no diretório corrente. O tipo de compactação do
    arquivo é obtido a partir de sua extensão. Se o tipo de compactação não for
    reconhecido, uma exceção é disparada.

    Args:
    arq_compactado:     arquivo a ser descompactado
    """

    tipo_compactacao = arq_compactado.rsplit(".", 1)[1]
    if tipo_compactacao == "gz":
        if arq_compactado.rsplit(".", 2)[1] == "tar":
            tipo_compactacao = "targz"

    if tipo_compactacao == "gz":
        # tipo gz é apenas um arquivo único compactado (não é um archive (tar))
        with gzip.open(arq_compactado, "rb") as f_in:
            # não é possível saber o nome original do arquivo gzipado, então o
            # nome nome do arquivo descompactado vai ser o mesmo, apenas sem o
            # sufixo ".gz"
            with open(arq_compactado[:-3], "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        # qualquer outro tipo de compactação é um archive, ou seja, pode
        # contter um ou mais arquivos no mesmo arquivo compactado, e então
        # pode-se usar o pacote shutil
        shutil.unpack_archive(arq_compactado)

def baixa_arquivo(url, descompacta=False, sobrescreve=True):
    """
    Baixa um arquivo disponibilizado numa URL e o descompacta, se for o caso. O
    arquivo baixado e o(s) arquivo(s) descompactado(s) serão gravados no
    diretório corrente.
    Em caso de erro, uma exceção será disparada.

    Args:
    url:                url do arquivo a ser baixado
    descompacta:        indica se o arquivo deve ser descompactado após ser
                        baixado
    sobrescreve:        indica se o arquivo deve ser sobrescrito se já existir.
                        Se False, um novo arquivo, com um sufixo apropriado,
                        será criado se o arquivo já existir
    """

    nome_arquivo = url.rsplit('/', 1)[-1]
    if sobrescreve:
        try:
            os.remove(nome_arquivo)
        except:
            # não importa se o arquivo não existia antes
            pass

    try:
        response = wget.download(url)
    except Exception as e:
        erro.console._( "Não foi possível baixar o arquivo " + url + ".\n" + 
                        str(e))
        raise RuntimeError

    if descompacta:
        descompacta_arquivo(nome_arquivo)

