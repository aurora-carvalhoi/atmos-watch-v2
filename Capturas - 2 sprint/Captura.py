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

# ===================== CONFIG =====================
load_dotenv()

IDENTIFICADOR = "Kaio"
EMPRESA = "empresaX"
HOSTNAME = socket.gethostname()

BUCKET = os.getenv("S3_BUCKET_NAME")

# ===================== LOG =====================
def log(mensagem):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{agora}] {mensagem}")

# ===================== CLIENT S3 =====================
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL") or None
)

# ===================== COLETA =====================
def coletar_dados(top_n=5):
    sistema_operacional = platform.system()

    if sistema_operacional == "Linux":
        root = '/'
    elif sistema_operacional == "Windows":
        root = 'C:\\'
    else:
        log("Plataforma não suportada")
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
    cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0

    disk_throughput = (disk2.read_bytes + disk2.write_bytes - disk1.read_bytes - disk1.write_bytes) / (1024**2)
    upload = (net2.bytes_sent - net1.bytes_sent) / (1024**2)
    download = (net2.bytes_recv - net1.bytes_recv) / (1024**2)

    conexoes = len(psutil.net_connections())

    processos = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
        except:
            pass

    time.sleep(0.5)

    for proc in psutil.process_iter(['pid', 'name']):
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
        "total_processos": len(processos),
        "identificador": IDENTIFICADOR,
        "hostname": HOSTNAME,
        "empresa": EMPRESA
    }

# ===================== CSV =====================
def salvar_csv(caminho, dados):
    arquivo_existe = os.path.isfile(caminho)

    with open(caminho, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=dados.keys())

        if not arquivo_existe:
            writer.writeheader()

        writer.writerow(dados)

# ===================== NOME ARQUIVO =====================
def gerar_nome_arquivo():
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    pasta = f"./amostras/{EMPRESA}/{HOSTNAME}"

    os.makedirs(pasta, exist_ok=True)

    return os.path.join(pasta, f"{IDENTIFICADOR}_{timestamp}.csv")

# ===================== UPLOAD S3 =====================
def upload_s3(caminho_csv):
    if not BUCKET:
        log("UPLOAD_ERROR bucket não definido no .env")
        return

    nome_arquivo = os.path.basename(caminho_csv)
    hostname_safe = HOSTNAME.replace(" ", "_").lower()

    s3_key = f"raw/{EMPRESA}/{hostname_safe}/{nome_arquivo}"

    log(f"UPLOAD_DEBUG bucket={BUCKET} key={s3_key}")

    try:
        s3.upload_file(caminho_csv, BUCKET, s3_key)

        log(
            f"UPLOAD_OK "
            f"bucket={BUCKET} "
            f"key={s3_key} "
            f"file={nome_arquivo}"
        )

    except Exception as e:
        log(f"UPLOAD_ERROR erro={e}")

# ===================== LOOP PRINCIPAL =====================
def main():
    log(f"DEBUG_BUCKET={BUCKET}")
    caminho_csv = gerar_nome_arquivo()
    contador = 0
    tempo_inicio = time.time()

    log(f"START coleta empresa={EMPRESA} host={HOSTNAME}")

    while True:
        inicio = time.time()

        dados = coletar_dados(10)
        salvar_csv(caminho_csv, dados)

        contador += 1
        tempo_execucao = time.time() - inicio
        tempo_total = time.time() - tempo_inicio

        log(
            f"LOOP count={contador} arquivo={os.path.basename(caminho_csv)} "
            f"execucao_s={round(tempo_execucao,2)} total_s={round(tempo_total,2)}"
        )

        # Upload a cada 100 coletas ou 10 minutos
        if contador >= 100 or tempo_total >= 6001:
            log("UPLOAD_START")

            upload_s3(caminho_csv)

            contador = 0
            tempo_inicio = time.time()
            caminho_csv = gerar_nome_arquivo()

            log("NOVO_ARQUIVO iniciado")

        # mantém 60s por ciclo
        time.sleep(max(0, 60 - tempo_execucao))

# ===================== EXECUÇÃO =====================
if __name__ == "__main__":
    main()