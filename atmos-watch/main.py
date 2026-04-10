# Script de captura de dados
import platform, sys, colorama

# Importa componentes do colorama
from colorama import Fore, Style, init

# Importa o arquivo com a função de captura
from src.captura import captura

# Inicializa o colorama
init()

# Atmos ASCII Arte
print(Fore.BLUE + """
   ███    ████████ ██     ██  ███████   ██████  
  ██ ██      ██    ███   ███ ██     ██ ██    ██ 
 ██   ██     ██    ████ ████ ██     ██ ██       
██     ██    ██    ██ ███ ██ ██     ██  ██████  
█████████    ██    ██     ██ ██     ██       ██ 
██     ██    ██    ██     ██ ██     ██ ██    ██ 
██     ██    ██    ██     ██  ███████   ██████  
""" + Style.RESET_ALL)

# Obtém as informações do sistema
sistema_operacional = platform.uname()

# Imprime as informações do sistema
print(Fore.BLUE + "Sistema operacional: " + Style.RESET_ALL + sistema_operacional.system)
print(Fore.BLUE + "Host: " + Style.RESET_ALL + sistema_operacional.node)
print(Fore.BLUE + "Kernel: " + Style.RESET_ALL + sistema_operacional.release)
print(Fore.BLUE + "Versão: " + Style.RESET_ALL + sistema_operacional.version)
print(Fore.BLUE + "Máquina: " + Style.RESET_ALL + sistema_operacional.machine)
print("\n© ATMOS MONITORING SYSTEMS 2026. TODOS OS DIREITOS RESERVADOS.")

# Vetor de argumentos de linha de comando (Ex.: python3 script.py -r - Todos os items após o 'script.py' são argumentos)
argumentos = sys.argv

# Componentes válidos
componentes_validos = ["--all", "-c", "-d", "-r"]

# Frequência padrão
FREQ_PADRAO = 5

# Verifica quantidade correta de argumentos
if len(argumentos) > 3:
    print(Fore.RED + "\nUso incorreto!" + Style.RESET_ALL)
    print("\nUso:", Fore.YELLOW + "python3 main.py [componente] [frequência]" + Style.RESET_ALL)
    print("\nComandos disponíveis:")
    print("  -c   CPU")
    print("  -d   Disco")
    print("  -r   RAM")
    print("  --all  Todos")
    sys.exit(1)

# Componente de captura de dados (Ex.: -c para CPU, -d para Disco, -r para RAM ou --all para todos)
componente = argumentos[1]

# Verifica o argumento de componente
if componente not in componentes_validos:
    print(Fore.RED + "\nErro: Componente inválido!" + Style.RESET_ALL)
    sys.exit(1)

# Verifica se foi passado a frequência em segundos de captura
if len(argumentos) > 2:
    frequencia = float(argumentos[2])

    # Valida a frequência
    if frequencia <= 0:
        print(Fore.RED + "\nErro: Frequência deve ser um número positivo!" + Style.RESET_ALL)
        sys.exit(1)
else:
    # AJusta a frequência para o padrão, caso não seja passada como argumento
    frequencia = FREQ_PADRAO

# Plataforma (Windows, Linux ...)
plataforma = sistema_operacional.system

# Garante que o script não quebre ao tentar sair com (CTRL + C)
try:
    # Executa a captura de dados
    captura(componente, frequencia, plataforma)

# Exceção para interrupção via teclado (CRTL + C)
except KeyboardInterrupt:
    print("\n\nParando captura de dados...")
    sys.exit(0)




