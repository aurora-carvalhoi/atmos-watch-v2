import os
import boto3
from datetime import datetime
from dotenv import load_dotenv

# carregar .env uma vez
load_dotenv(".env")

def upload_s3(caminho_csv, empresa, hostname):
    # =========================
    # Config AWS
    # =========================
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    region = os.getenv("AWS_DEFAULT_REGION")
    bucket = os.getenv("S3_BUCKET_NAME")
    endpoint = os.getenv("S3_ENDPOINT_URL") or None  # evita erro

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region,
        endpoint_url=endpoint
    )

    # =========================
    # Montar caminho no S3
    # =========================
    nome_arquivo = os.path.basename(caminho_csv)
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    s3_key = f"raw/{empresa}/{hostname}/{data_hoje}/{nome_arquivo}"

    # =========================
    # Upload
    # =========================
    try:
        s3.upload_file(caminho_csv, bucket, s3_key)
        print(f"✅ Upload OK: s3://{bucket}/{s3_key}")
    except Exception as e:
        print(f"❌ Erro no upload: {e}")

print("KEY:", os.getenv("AWS_ACCESS_KEY_ID"))
caminho_csv = "empresaX/kaio/kaio_20260408_115842.csv"
empresa = "empresaX"
hostname = 'laptop_nz13'
upload_s3(caminho_csv, empresa, hostname)