import os
import time
import random
import psutil
import json
import boto3
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv(r"C:/Users/User/OneDrive - SPTech School/Attachments/.env")

BUCKET = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

TempoDeCaptura = 10 * 60
EMPRESA = 1
SERVIDOR = "Servidor_Metereologia"


def raw():
    cpu = psutil.cpu_percent(interval=1)
    variacao = random.uniform(-1, 1)
    temperatura = 45 + (cpu * 0.5) + variacao

    return {
        "timestamp": datetime.now().strftime("%H:%M"),
        "cpu": round(cpu, 1),
        "temperatura": round(temperatura, 1)
    }


def salvar_raw_s3(leitura):

    key = f"raw/{SERVIDOR}/raw.csv"

    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        conteudo = obj["Body"].read().decode("utf-8")
    except:
        conteudo = "timestamp,cpu,temperatura\n"

    nova_linha = f"{leitura['timestamp']},{leitura['cpu']},{leitura['temperatura']}\n"
    conteudo += nova_linha

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=conteudo.encode("utf-8")
    )

    print(f"raw enviado {key}")


def carregar_raw_s3():

    key = f"raw/{SERVIDOR}/raw.csv"

    obj = s3.get_object(Bucket=BUCKET, Key=key)

    return pd.read_csv(BytesIO(obj["Body"].read()))


def regressao_cpu(df):
    if len(df) < 10:
        return 0, 0

    x = df["cpu"].values
    y = df["temperatura"].values

    a, b = np.polyfit(x, y, 1)
    return float(a), float(b)


def regressao_tempo(df):
    if len(df) < 10:
        return None, None

    x = np.arange(len(df))
    y = df["temperatura"].values

    a, b = np.polyfit(x, y, 1)
    return float(a), float(b)


def trusted(df):

    df = df.tail(100)

    a, b = regressao_cpu(df)
    a_t, b_t = regressao_tempo(df)

    cpu_p90 = round(np.percentile(df["cpu"], 90), 1)
    temperatura_atual = float(df.iloc[-1]["temperatura"])

    if a_t is not None:
        temperatura_prevista = round(a_t * (len(df) + 6) + b_t, 1)
    else:
        temperatura_prevista = temperatura_atual

    impacto = round(a * 10, 2)

    status = (
        "CRITICO" if temperatura_atual >= 90 else
        "ALERTA" if temperatura_atual >= 80 else
        "NORMAL"
    )

    historico = df.to_dict(orient="records")

    regressao = [
        {"x": x, "y": round(a * x + b, 1)}
        for x in range(0, 101, 10)
    ]


    agora = datetime.now()
    previsoes = []

    for i in range(1, 25):
        futuro = agora + timedelta(minutes=i * 10)

        previsoes.append({
            "timestamp": futuro.strftime("%H:%M"),
            "temperaturaPrevista": round(temperatura_atual + random.uniform(-3, 3), 1),
            "temperaturaReal": None
        })

    return {
        "kpis": {
            "servidor": SERVIDOR,
            "cpuP90": cpu_p90,
            "temperaturaAtual": temperatura_atual,
            "temperaturaPrevista": temperatura_prevista,
            "status": status,
            "impactoCpuPor10pct": impacto
        },
        "grafico": historico,
        "previsoes": previsoes,
        "regressao": regressao
    }


def salvar_client_s3(dados):

    key = f"client/{EMPRESA}/{SERVIDOR}.json"

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(dados, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json"
    )

    print(f"client enviado {key}")


while True:

    leitura = raw()

    salvar_raw_s3(leitura)

    print(f"CPU {leitura['cpu']}% | Temp {leitura['temperatura']}°C")

    df = carregar_raw_s3()

    dados = trusted(df)

    salvar_client_s3(dados)

    time.sleep(TempoDeCaptura)