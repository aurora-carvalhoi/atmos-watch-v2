import os
import pandas as pd

CAMINHO_AMOSTRAS = "./empresaX"
NOME_TRUSTED = "trusted_v1.csv"

diretorio_trusted = os.path.join(CAMINHO_AMOSTRAS, "trusted")
os.makedirs(diretorio_trusted, exist_ok=True)

dataframes = []

for root, dirs, files in os.walk(CAMINHO_AMOSTRAS):
    if "trusted" in root:
        continue

    for file in files:
        if file.endswith(".csv"):
            caminho_arquivo = os.path.join(root, file)
            print(f"Lendo: {caminho_arquivo}")

            try:
                df = pd.read_csv(caminho_arquivo)

                # Nome da empresa baseado na pasta
                nome_empresa = os.path.basename(os.path.dirname(root))
                df["company"] = nome_empresa

                dataframes.append(df)

            except Exception as e:
                print(f"Erro ao ler {caminho_arquivo}: {e}")

if dataframes:
    df = pd.concat(dataframes, ignore_index=True)

    print("\nTransformando dados...")

    # =========================
    # Conversão de tipos
    # =========================
    colunas_numericas = [
        "cpu_perc", "cpu_freq", "ram_perc", "ram_usada", "ram_livre",
        "disco_perc", "disco_usado", "disco_livre", "disco_total",
        "disco_throughput", "upload", "download", "network_total",
        "conexoes", "total_processos"
    ]

    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # =========================
    # Conversão de unidades (bytes -> GB)
    # =========================
    BYTES_TO_GB = 1024 ** 3

    df["ram_used_gb"] = (df["ram_usada"] / BYTES_TO_GB).round(2)
    df["ram_free_gb"] = (df["ram_livre"] / BYTES_TO_GB).round(2)
    df["ram_total_gb"] = (df["ram_used_gb"] + df["ram_free_gb"]).round(2)

    df["disk_used_gb"] = (df["disco_usado"] / BYTES_TO_GB).round(2)
    df["disk_free_gb"] = (df["disco_livre"] / BYTES_TO_GB).round(2)
    df["disk_total_gb"] = (df["disco_total"] / BYTES_TO_GB).round(2)

    # =========================
    # Network
    # =========================
    df["network_total_mb_s"] = (df["upload"] + df["download"]).round(2)

    # =========================
    # Renomear colunas (padrão profissional)
    # =========================
    df = df.rename(columns={
        "datahora": "timestamp",
        "cpu_perc": "cpu_usage_percent",
        "cpu_freq": "cpu_frequency_mhz",
        "ram_perc": "ram_usage_percent",
        "disco_perc": "disk_usage_percent",
        "disco_throughput": "disk_throughput_mb_s",
        "upload": "network_upload_mb_s",
        "download": "network_download_mb_s",
        "conexoes": "active_connections",
        "total_processos": "total_processes",
        "identificador": "host_id"
    })

    # =========================
    # Selecionar colunas finais
    # =========================
    colunas_finais = [
        "timestamp",
        "host_id",
        "hostname",
        "company",

        "cpu_usage_percent",
        "cpu_frequency_mhz",

        "ram_usage_percent",
        "ram_used_gb",
        "ram_free_gb",
        "ram_total_gb",

        "disk_usage_percent",
        "disk_used_gb",
        "disk_free_gb",
        "disk_total_gb",
        "disk_throughput_mb_s",

        "network_upload_mb_s",
        "network_download_mb_s",
        "network_total_mb_s",

        "active_connections",
        "total_processes"
    ]

    df_final = df[colunas_finais]

    # =========================
    # Salvar
    # =========================
    caminho_saida = os.path.join(diretorio_trusted, NOME_TRUSTED)
    df_final.to_csv(caminho_saida, index=False)

    print(f"\nArquivo trusted criado em: {caminho_saida}")

else:
    print("Nenhum CSV encontrado.")