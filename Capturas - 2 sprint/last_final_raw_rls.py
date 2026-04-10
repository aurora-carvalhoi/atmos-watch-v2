import psutil
import os
import time
import platform
import sys
import csv
import socket
import boto3
from dotenv import load_dotenv
from datetime import datetime

identificador = "kaio"
hostname = socket.gethostname()

# ===================== COLETA =====================
def coletar_dados(top_n=5):
    sistema_operacional = platform.uname().system

    if sistema_operacional == "Linux":
        root = '/'
    elif sistema_operacional == "Windows":
        root = 'C:\\'
    else:
        print("Plataforma não suportada")
        sys.exit()

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    disk1 = psutil.disk_io_counters()
    net1 = psutil.net_io_counters()

    psutil.cpu_percent(interval=None)

    ram = psutil.virtual_memory()
    disco = psutil.disk_usage(root)

    time.sleep(1)

    disk2 = psutil.disk_io_counters()
    net2 = psutil.net_io_counters()

    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq().current

    bytes1 = disk1.read_bytes + disk1.write_bytes
    bytes2 = disk2.read_bytes + disk2.write_bytes
    disk_throughput = (bytes2 - bytes1) / (1024**2)

    upload = (net2.bytes_sent - net1.bytes_sent) / (1024**2)
    download = (net2.bytes_recv - net1.bytes_recv) / (1024**2)

    conexoes = len(psutil.net_connections())

    processos = []
    procs = list(psutil.process_iter(['pid', 'name']))

    for proc in procs:
        try:
            proc.cpu_percent(interval=None)
        except:
            pass

    time.sleep(0.5)

    for proc in procs:
        try:
            nome = proc.info['name']

            if nome == "System Idle Process":
                continue

            cpu = proc.cpu_percent(interval=None) / psutil.cpu_count()
            mem = proc.memory_percent()

            processos.append({
                'pid': proc.pid,
                'name': nome,
                'cpu': cpu,
                'mem': mem
            })

        except:
            pass

    total_processos = len(processos)

    top_cpu = sorted(processos, key=lambda x: x['cpu'], reverse=True)[:top_n]
    top_mem = sorted(processos, key=lambda x: x['mem'], reverse=True)[:top_n]

    return {
        "datahora": timestamp,
        "cpu_perc": cpu_percent,
        "cpu_freq": cpu_freq,
        "ram_perc": ram.percent,
        "ram_usada": ram.used,
        "ram_livre": ram.available,
        "disco_perc": disco.percent,
        "disco_usado": disco.used,
        "disco_livre": disco.free,
        "disco_total": disco.total,
        "disco_throughput": round(disk_throughput, 2),
        "upload": round(upload, 2),
        "download": round(download, 2),
        "network_total": round(upload + download, 2),
        "conexoes": conexoes,
        "total_processos": total_processos,
        "top_cpu": top_cpu,
        "top_mem": top_mem,
        "identificador": identificador,
        "hostname": hostname
    }

# ===================== CSV =====================
def salvar_csv(caminho, dados):
    arquivo_existe = os.path.isfile(caminho)

    dados_filtrados = {k: v for k, v in dados.items() if not isinstance(v, list)}

    with open(caminho, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=dados_filtrados.keys())

        if not arquivo_existe:
            writer.writeheader()

        writer.writerow(dados_filtrados)


# ===================== LOOP PRINCIPAL =====================
def gerar_nome_arquivo(identificador):
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return f"{identificador}_{timestamp}.csv"


def main():
    identificador = "kaio"
    caminho_csv = gerar_nome_arquivo(identificador)
    contador = 0

    tempo_inicio_loop = time.time() 

    while True:
        inicio = time.time()

        dados = coletar_dados(10)
        salvar_csv(caminho_csv, dados)

        contador += 1
        print(f"Arquivo atual: {caminho_csv}")
        print(f"Loop: {contador}")
        print(f"Loop finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        tempo_decorrido = time.time() - tempo_inicio_loop


        if contador >= 100 or tempo_decorrido >= 60000:
            upload_s3(caminho_csv)

            contador = 0
            tempo_inicio_loop = time.time()

            caminho_csv = gerar_nome_arquivo(identificador)

        # GARANTE 1 MINUTO EXATO
        tempo_execucao = time.time() - inicio
        tempo_restante = max(0, 60 - tempo_execucao)

        time.sleep(tempo_restante)


# ===================== EXECUÇÃO =====================
if __name__ == "__main__":
    main()


def upload_s3(caminho_csv):
    # Carrega .env
    load_dotenv()

    # Pega variáveis
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_DEFAULT_REGION")
    bucket = os.getenv("S3_BUCKET_NAME")
    endpoint = os.getenv("S3_ENDPOINT_URL")

    # Cria cliente S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region,
        endpoint_url=endpoint
    )

    # Nome do arquivo no S3 (mesmo do local)
    nome_no_s3 = os.path.basename(caminho_csv)

    # upload
    try:
        s3.upload_file(caminho_csv, bucket, nome_no_s3)
        print(f"Upload realizado com sucesso: {bucket}/{nome_no_s3}")
    except Exception as e:
        print(f"Erro no upload: {e}")
    

