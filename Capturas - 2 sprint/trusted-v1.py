import os
import pandas as pd
import time

caminho_amostras = f"./empresaX"
nome_trusted = "trusted_v1.csv"
nome_empresa= ""


diretorio_trusted = os.path.join(caminho_amostras, "trusted")
os.makedirs(diretorio_trusted, exist_ok=True)

dataframe = []

for root, dirs, files in os.walk(caminho_amostras):
    if "trusted" in root:
        continue

    for file in files:
        if file.endswith(".csv"):
            caminho_amostras = os.path.join(root, file)
            print(f"lendo: {caminho_amostras}")

            try:
                df = pd.read_csv(caminho_amostras)
                nome_empresa = os.path.basename(os.path.dirname(root))
                df["empresa"] = nome_empresa
                dataframe.append(df)
            except Exception as e:
                print(f"Erro ao ler {caminho_amostras}: {e}")

if dataframe:
    dataframe_final = pd.concat(dataframe, ignore_index=True)
    caminho_saida = os.path.join(diretorio_trusted, "trusted_teste.csv")

    dataframe_final.to_csv(caminho_saida, index=False)
    print(f"\n Arquivo final criado em: {caminho_saida}")
    
    df_final = pd.read_csv(caminho_saida)
    print("Convertendo unidade de medida da ram...")
    time.sleep(1)
    try:
        df_final['ram_usada'] = round(df_final['ram_usada'].apply(lambda x: (x / 10**9)), 2)
        df_final['ram_livre'] = round(df_final['ram_livre'].apply(lambda x: (x / 10**9)), 2)
        df_final['disco_usado'] = round(df_final['disco_usado'].apply(lambda x: (x / 10**9)), 2)
        df_final['disco_livre'] = round(df_final['disco_livre'].apply(lambda x: (x / 10**9)), 2)
        df_final['disco_total'] = round(df_final['disco_total'].apply(lambda x: (x / 10**9)), 2)

        print("Unidades de medidas convertidaas com sucesso em")
    except:
        print("Erro ao converter unidade de medidas.")

    caminho_trusted = f"{nome_empresa}/trusted/{nome_trusted}"
    df_final.to_csv(caminho_trusted, index=False)

else:
    print("Nenhum CSV encontrado.")
