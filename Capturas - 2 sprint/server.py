import psutil
import os
import time
import platform
import sys
import csv
import socket

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

    # ================= PERÍODO 1 =================
    disk1 = psutil.disk_io_counters()
    net1 = psutil.net_io_counters()

    psutil.cpu_percent(interval=None)

    ram = psutil.virtual_memory()
    disco = psutil.disk_usage(root)

    time.sleep(1)

    # ================= PERÍODO 2 =================
    disk2 = psutil.disk_io_counters()
    net2 = psutil.net_io_counters()

    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq().current

    # ================= CÁLCULOS =================
    bytes1 = disk1.read_bytes + disk1.write_bytes
    bytes2 = disk2.read_bytes + disk2.write_bytes
    disk_throughput = (bytes2 - bytes1) / (1024**2)

    upload = (net2.bytes_sent - net1.bytes_sent) / (1024**2)
    download = (net2.bytes_recv - net1.bytes_recv) / (1024**2)

    conexoes = len(psutil.net_connections())

    # ================= PROCESSOS =================
    processos = []

    procs = list(psutil.process_iter(['pid', 'name']))


    for proc in procs:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
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

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    total_processos = len(processos)

    top_cpu = sorted(processos, key=lambda x: x['cpu'], reverse=True)[:top_n]
    top_mem = sorted(processos, key=lambda x: x['mem'], reverse=True)[:top_n]

    return {
        "datahora": timestamp,

        # CPU
        "cpu_perc": cpu_percent,
        "cpu_freq": cpu_freq,

        # RAM
        "ram_perc": ram.percent,
        "ram_usada": ram.used,
        "ram_livre": ram.available,

        # DISCO
        "disco_perc": disco.percent,
        "disco_usado": disco.used,
        "disco_livre": disco.free,
        "disco_total": disco.total,
        "disco_throughput": round(disk_throughput, 2),

        # REDE
        "upload": round(upload, 2),
        "download": round(download, 2),
        "network_total": round(upload + download, 2),
        "conexoes": conexoes,

        # PROCESSOS
        "total_processos": total_processos,
        "top_cpu": top_cpu,
        "top_mem": top_mem,

        # INDENTIFICADORES
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

# ===================== PRINT =====================
def print_dados(d):
    print("\n===== ID =====")
    print("Identificador: ", d["identificador"])
    print("Hostname: ", d["hostname"])

    print("\n===== DISCO =====")
    print("Total:", d["disco_total"])
    print("Usado:", d["disco_usado"])
    print("Livre:", d["disco_livre"])
    print("Uso (%):", d["disco_perc"])
    print("Throughput (MB/s):", d["disco_throughput"])

    print("\n===== CPU =====")
    print("Frequência:", d["cpu_freq"])
    print("Uso (%):", d["cpu_perc"])

    print("\n===== RAM =====")
    print("Usada:", d["ram_usada"])
    print("Livre:", d["ram_livre"])
    print("Uso (%):", d["ram_perc"])

    print("\n===== REDE =====")
    print("Upload (MB/s):", d["upload"])
    print("Download (MB/s):", d["download"])
    print("Total (MB/s):", d["network_total"])
    print("Conexões:", d["conexoes"])

    print("\n===== PROCESSOS =====")
    print("Total de processos:", d["total_processos"])

    print("\nTop processos por CPU:")
    for p in d["top_cpu"]:
        print(f"PID {p['pid']} | {p['name']} | CPU: {p['cpu']:.2f}%")

    print("\nTop processos por Memória:")
    for p in d["top_mem"]:
        print(f"PID {p['pid']} | {p['name']} | RAM: {p['mem']:.2f}%")

# ===================== EXECUÇÃO =====================
dados = coletar_dados(10)

salvar_csv("registros.csv", dados)

print_dados(dados)