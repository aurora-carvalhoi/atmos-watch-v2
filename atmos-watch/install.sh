#!/bin/bash

# Volta um diretório
cd ..

# Compacta o projeto
zip -r atmos.zip atmos-watch

# Garante que o diretório existe
mkdir -p ~/.local/bin

# Move o zip para o PATH do usuário
mv atmos.zip ~/.local/bin/

# Entra no diretório
cd ~/.local/bin

# Extrai o projeto
unzip atmos.zip

# Remove o zip
rm atmos.zip

# Entra na pasta do projeto
cd atmos-watch

# Cria o executável
cp main.py atmos

# Adiciona shebang
sed -i '1i #!/usr/bin/env python3' atmos

# Permissão de execução
chmod +x atmos

# Cria link simbólico no PATH 
ln -sf ~/.local/bin/atmos-watch/atmos ~/.local/bin/atmos

echo "---"
echo "Instalação concluída:"
which atmos
