import sys

import psutil, time
from colorama import Fore, Style

# Importa o arquivo de script de salvar dados
from src.salvar import salvar

# Captura os dados com base num componente e numa frequência
def captura(componente, frequencia, plataforma):
    """
    Faz a captura de dados de um componente de hardware da máquina

    Args:
        componente (str): O nome do componente.
        frequencia (int): O valor da frequência.
    """

    # Valida o tipo de componente a ser capturado os dados
    if componente == '-d':
        print("\n" + Fore.BLUE + f"Leitura de disco a cada {frequencia}s iniciada" + Style.RESET_ALL + "\n")

        # Atribui o tipo correto de partição root do sistema (Windows 'C:\\' e Linux: '/')
        if plataforma == "Linux":
            root = '/'
        elif plataforma == "Windows":
            root = 'C:\\'
        else:
            print("Plataforma não suportada")
            sys.exit()

        # Loop
        while True:
            # Objeto de disco do psutil
            disco = psutil.disk_usage(root)

            # Data e hora atual formatada
            data_hora = time.strftime('%d-%m-%Y %H:%M:%S')

            # Razão de conversão
            razao = (1 / (1024 ** 3))

            # Dicionário de leitura
            leitura = {'data_hora': data_hora, 'total': disco.total, 'livre': disco.free, 'percentual': disco.percent}

            # Nome do arquivo de saída
            arquivo = 'dados_disco.csv'

            # Cabeçalho
            cabecalho = ['data_hora', 'total', 'livre', 'percentual']

            # Salva os dados de leitura
            salvar(arquivo, cabecalho, leitura)

            # Mostra no terminal a leitura
            print(f"{data_hora} | Total: {(disco.total * razao):.2f} GiB | Livre: {(disco.free * razao):.2f} GiB | Percentual: {disco.percent}%")

            # Aguarda para realizar o loop novamente
            time.sleep(frequencia)

    elif componente == '-c':
        print("\n" + Fore.BLUE + f"Leitura de CPU a cada {frequencia}s iniciada" + Style.RESET_ALL + "\n")

        # Loop
        while True:
            # Objeto de frequência da CPU do psutil
            cpu_freq = psutil.cpu_freq()

            # Objeto de percentual de uso da CPU do psutil
            cpu_percentual = psutil.cpu_percent(interval=frequencia)

            # Data e hora
            data_hora = time.strftime('%d-%m-%Y %H:%M:%S')

            # Dicionário de leitura
            leitura = {'data_hora': data_hora, 'freq_atual': cpu_freq.current, 'freq_min': cpu_freq.min, 'freq_max': cpu_freq.max, 'percentual': cpu_percentual}

            # Nome do arquivo de saída
            arquivo = 'dados_cpu.csv'

            # Cabeçalho
            cabecalho = ['data_hora', 'freq_atual', 'freq_min', 'freq_max', 'percentual']

            # Salva os dados de leitura
            salvar(arquivo, cabecalho, leitura)

            # Mostra no terminal a leitura
            print(f"{data_hora} | Uso: {cpu_percentual}% | Freq. atual: {cpu_freq.current :.2f} Mhz | Freq. mínima: {cpu_freq.min :.2f} Mhz | Freq. max: {cpu_freq.max :.2f} Mhz")

            # Aguarda para realizar o loop novamente
            time.sleep(frequencia)

    elif componente == '-r':
        print("\n" + Fore.BLUE + f"Leitura de RAM a cada {frequencia}s iniciada" + Style.RESET_ALL + "\n")

        # Loop
        while True:
            # Objeto de RAM do psutil
            ram = psutil.virtual_memory()

            # Razão de conversão
            razao = (1 / (1024 ** 3))

            # Data e hora
            data_hora = time.strftime('%d-%m-%Y %H:%M:%S')

            # Dicionário de leitura
            leitura = {'data_hora': data_hora, 'total': ram.total, 'livre': ram.free, 'percentual': ram.percent, 'cache': ram.cached}

            # Nome do arquivo de saída
            arquivo = 'dados_ram.csv'

            # Cabeçalho
            cabecalho = ['data_hora', 'total', 'livre', 'percentual', 'cache']

            # Salva os dados de leitura
            salvar(arquivo, cabecalho, leitura)

            # Mostra no terminal a leitura
            print(f"{data_hora} | Total: {(ram.total * razao):.2f} | Livre: {(ram.free * razao):.2f} | Percentual: {ram.percent}%")

            # Aguarda para realizar o loop novamente
            time.sleep(frequencia)

    elif componente == '--all':
        print("\n" + Fore.BLUE + f"Leitura de CPU, RAM e Disco a cada {frequencia}s iniciada" + Style.RESET_ALL + "\n")

        # Atribui o tipo correto de partição root do sistema (Windows 'C:\\' e Linux: '/')
        if plataforma == "Linux":
            root = '/'
        elif plataforma == "Windows":
            root = 'C:\\'
        else:
            print("Plataforma não suportada")
            sys.exit()

        # Razão de conversão
        razao = (1 / (1024 ** 3))

        # Loop
        while True:
            # Objeto de disco do psutil
            disco = psutil.disk_usage(root)

            # Objeto de frequência da CPU do psutil
            cpu_freq = psutil.cpu_freq()

            # Objeto de percentual de uso da CPU do psutil
            cpu_percentual = psutil.cpu_percent(interval=frequencia)

            # Objeto de RAM do psutil
            ram = psutil.virtual_memory()

            # Data e hora atual formatada
            data_hora = time.strftime('%d-%m-%Y %H:%M:%S')

            # Dicionário de leitura
            leitura = {
                'data_hora': data_hora,
                'disco_percentual_uso': disco.percent,
                'disco_livre': disco.free,
                'ram_percentual_uso': ram.percent,
                'ram_total': ram.total,
                'ram_livre': ram.free,
                'cpu_percentual_uso': cpu_percentual,
                'cpu_freq_atual': cpu_freq.current,
            }

            # Nome do arquivo de saída
            arquivo = 'dados_cpu_ram_disco.csv'

            # Cabeçalho
            cabecalho = [
                'data_hora',
                'disco_percentual_uso',
                'disco_livre',
                'ram_percentual_uso',
                'ram_total',
                'ram_livre',
                'cpu_percentual_uso',
                'cpu_freq_atual'
            ]

            # Salvar os dados de leitura
            salvar(arquivo, cabecalho, leitura)

            # Mostra no terminal a leitura
            print(f"{data_hora} | Disco (Uso): {(disco.used * razao):.2f} GB | Disco (Livre): {(disco.free * razao):.2f} GB | RAM (Uso): {(ram.used * razao):.2f} GB | CPU (Uso): {cpu_percentual}% | CPU (Freq): {cpu_freq.current:.2f} Mhz")

            # Aguarda para realizar o loop novamente
            time.sleep(frequencia)

    else:
        print("Função não encontrada")
        sys.exit()
