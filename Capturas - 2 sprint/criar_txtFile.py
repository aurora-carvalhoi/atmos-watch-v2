import json
import os
nome_arquivo = "arquivo.json"
conteudo_inicial = {
    "identificador": "",
    "empresa": ""
}

if not os.path.isfile(nome_arquivo):
    with open(nome_arquivo, 'w', encoding="utf-8") as arquivo:
        json.dump(conteudo_inicial , arquivo, indent=4, ensure_ascii=False)
        print("Arquivo criado com o conteudo inicial")
else:
    print("Arquivo ja existe!")


def sobescrita(conteudo):
    with open(nome_arquivo, 'w', encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=4, ensure_ascii=False)
        print("Arquivo sobescrito com sucesso!")


with open(nome_arquivo, 'r', encoding="utf-8") as arquivo:
    conteudo = json.load(arquivo)
    if conteudo['identificador'] == "" or conteudo["empresa"] == "" :
        conteudo["identificador"] = input("Escreva o nome da maquina: ")
        conteudo["empresa"] = input("Escreva o nome da empresa: ")
        sobescrita(conteudo)

    

