# Atmos Watch

Script de captura e leitura de dados de máquinas

## Descrição do projeto

Este é um script em python que faz uso da biblioteca psutil para obter dados da máquina como CPU, Disco e a RAM.
Este repositório faz parte de uma solução software desenvolvida para âmbito acadêmico no **2º semestr**e do curso de **Ciência da Computação** da São Paulo Tech School - SPTECH [@BandTec](https://github.com/BandTec)

## Instalação

Para realizar a instalação e usar este projeto, é necessário possuir o **python** e o **pip** instalado.

Você pode clonar este repositório em seu computador e instalar todas as dependências usando o pip no terminal:

```
pip install -r requeriments.txt
```

Caso você esteja em um ambiente Linux, é recomendável usar um ambiente virtual python:
```
# Cria a venv
python3 -m venv ~/atmos-venv

# Ativa a venv
source ~/atmos-venv/bin/activate
```

Caso queira, pode criar um _alias_ para o script usando o `install.sh` na raíz do projeto

**Obs.: Disponível apenas em ambientes linux**

```
# Dê permissão de execução do instalador
chmod +x install.sh

# Executa o instalador
./install.sh
```
