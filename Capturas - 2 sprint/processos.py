import psutil
import socket
import platform
import time
import json
import os
from datetime import datetime

# =========================
# CONFIGURAÇÃO
# =========================

INTERVALO_CPU = 0.5  # segundos

# =========================
# PRIMEIRA LEITURA CPU
# =========================

for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except:
        pass

# janela de medição
time.sleep(INTERVALO_CPU)

# =========================
# INFORMAÇÕES DO SERVIDOR
# =========================

resultado = {
    "timestamp": datetime.now().isoformat(),
    "servidor": socket.gethostname(),
    "sistema": platform.system(),
    "versao_sistema": platform.version(),
    "arquitetura": platform.machine(),

    "cpu_total": {
        "uso_percentual": psutil.cpu_percent(),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "nucleos_totais": psutil.cpu_count(logical=True)
    },

    "ram_total": {
        "total_mb": round(psutil.virtual_memory().total / 1024 / 1024),
        "usado_mb": round(psutil.virtual_memory().used / 1024 / 1024),
        "disponivel_mb": round(psutil.virtual_memory().available / 1024 / 1024),
        "uso_percentual": psutil.virtual_memory().percent
    },

    "disco_total": {
        "total_gb": round(psutil.disk_usage('/').total / 1024 / 1024 / 1024),
        "usado_gb": round(psutil.disk_usage('/').used / 1024 / 1024 / 1024),
        "livre_gb": round(psutil.disk_usage('/').free / 1024 / 1024 / 1024),
        "uso_percentual": psutil.disk_usage('/').percent
    },

    "processos": []
}

# =========================
# PROCESSOS
# =========================

for proc in psutil.process_iter([
    'pid',
    'name',
    'username',
    'status',
    'create_time'
]):
    try:

        # =========================
        # DADOS BÁSICOS
        # =========================

        pid = proc.info['pid']
        nome = proc.info['name']
        usuario = proc.info['username']
        status = proc.info['status']

        # =========================
        # CPU
        # =========================

        cpu = round(proc.cpu_percent(interval=None), 2)

        # =========================
        # MEMÓRIA RAM
        # =========================

        memoria = proc.memory_info()

        ram_mb = round(memoria.rss / 1024 / 1024)

        # memória virtual
        memoria_virtual_mb = round(memoria.vms / 1024 / 1024)

        # =========================
        # DISCO
        # =========================

        try:
            io = proc.io_counters()

            leitura_mb = round(io.read_bytes / 1024 / 1024, 2)
            escrita_mb = round(io.write_bytes / 1024 / 1024, 2)

        except:
            leitura_mb = 0
            escrita_mb = 0

        # =========================
        # THREADS / SUBPROCESSOS
        # =========================

        threads = proc.num_threads()

        subprocessos = len(proc.children(recursive=True))

        # =========================
        # TEMPO DE EXECUÇÃO
        # =========================

        tempo_execucao_segundos = round(
            time.time() - proc.info['create_time']
        )

        # =========================
        # PRIORIDADE
        # =========================

        try:
            prioridade = proc.nice()
        except:
            prioridade = "N/A"

        # =========================
        # MONTA JSON
        # =========================

        resultado["processos"].append({
            "pid": pid,
            "nome": nome,
            "usuario": usuario,
            "status": status,

            "cpu": {
                "uso_percentual": cpu
            },

            "ram": {
                "uso_mb": ram_mb,
                "virtual_mb": memoria_virtual_mb
            },

            "disco": {
                "leitura_mb": leitura_mb,
                "escrita_mb": escrita_mb
            },

            "threads": threads,
            "subprocessos": subprocessos,

            "tempo_execucao_segundos": tempo_execucao_segundos,

            "prioridade": prioridade
        })

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):
        pass

# =========================
# ORDENA PELO MAIOR CONSUMO
# =========================

resultado["processos"].sort(
    key=lambda p: (
        p["cpu"]["uso_percentual"],
        p["ram"]["uso_mb"]
    ),
    reverse=True
)

# =========================
# EXIBE JSON
# =========================

# print(json.dumps(
#     resultado,
#     indent=2,
#     ensure_ascii=False
# ))

nome_arquivo = 'processos.json'
if not os.path.isfile(nome_arquivo):
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)
        print("Arquivo criado com sucesso!")
