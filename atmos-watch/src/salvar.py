import csv

# Função para salvar dados em CSV
def salvar(arquivo, campos, dados):
    """
    Salva os dados de leitura em um arquivo CSV.

    Args:
        arquivo (str): Caminho para o arquivo de destino.
        campos (list): Lista com o nome das colunas (headers).
        dados (dict): Dicionário contendo os valores a serem gravados.

    Returns:
        bool: True se a gravação foi bem-sucedida, False caso contrário.
    """

    # Realiza uma tentativa de escrita dos dados
    try:
        # Realiza o processo de escrita
        with open(file=arquivo, mode='a', newline='') as arq:
            # Passa para o escritor o arquivo, bem como os headers e o delimitador
            escritor = csv.DictWriter(arq, fieldnames=campos)

            # Verifica se o arquivo está vazio para escrever o cabeçalho
            if arq.tell() == 0:
                # Escreve o cabeçalho
                escritor.writeheader()

            # Grava os dados no arquivo passado
            escritor.writerow(dados)
        return True

    # Retorna uma mensagem de erro caso encontre algum erro
    except Exception as excecao:
        print(f"Ocorreu um erro ao registrar os dados: {excecao}\n")
        return False
