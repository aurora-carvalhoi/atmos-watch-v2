import os
import pandas as pd

caminho_amostras = "./amostras"
nome_empresa = "Atmos_teste"

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
                df["empresa"] = nome_empresa
                dataframe.append(df)
            except Exception as e:
                print(f"Erro ao ler {caminho_amostras}: {e}")

if dataframe:
    dataframe_final = pd.concat(dataframe, ignore_index=True)

    caminho_saida = os.path.join(diretorio_trusted, "trusted_teste.csv")

    dataframe_final.to_csv(caminho_saida, index=False)

    print(f"\n Arquivo final criado em: {caminho_saida}")

else:
    print("Nenhum CSV encontrado.")