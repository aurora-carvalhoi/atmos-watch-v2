import boto3       #SDK da AWS — usada pra acessar o S3
import csv         #lê e interpreta arquivos CSV
import json        #converte dicionários Python em JSON
import io          #permite tratar texto como se fosse um arquivo
import calendar    #calendário (pra saber quantos dias tem o mês)
from datetime import datetime, date  # manipulação de datas e horários

#conexão com o S3
s3 = boto3.client('s3')

#configurações
BUCKET = 'nome_bucket_aqui' # nome do bucket no S3

#nomes das colunas no CSV de métricas, tem q ajustar com a etl do kaio 
COL_TIMESTAMP = 'datahora'
COL_CPU = 'cpu_perc'
COL_RAM = 'ram_perc'
COL_DISCO = 'disco_perc'


#aqui inicia a lambda
def lambda_handler(event, _):
    
    empresa = event['empresa']

    hoje = date.today()
    mes = hoje.month
    ano = hoje.year
    total_dias  = calendar.monthrange(ano, mes)[1]  #quantos dias tem o mês (28/29/30/31)
    data_inicio = date(ano, mes, 1)                 #primeiro dia do mês
    data_fim = date(ano, mes, total_dias)         #último dia do mês

    #Aqui é onde ele buscaria o "raw" da empresa, tem q arrumar de acordo com nosso bucket
    prefix = f"raw/{empresa}/"

    incidentes = {}  #esse dicionario vai ser usado pro heatmap
    metricas = {}  #esse pros graficos

    # O paginator busca todos os arquivos do S3, mesmo que sejam mais de 1000
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET, Prefix=prefix)

    for page in pages:
        for obj in page.get('Contents', []):
            chave = obj['Key']  #caminho completo do arquivo no S3, precisa ajustar isso aqui

            if not chave.endswith('.csv'):
                continue

            csv_obj = s3.get_object(Bucket=BUCKET, Key=chave)
            conteudo = csv_obj['Body'].read().decode('utf-8')

            reader = csv.DictReader(io.StringIO(conteudo))
            if not reader.fieldnames:
                continue

            #Aqui ele vai ver qual dicionario ele vai alimentar:
            if 'tipo_incidente' in reader.fieldnames:
                processar_incidente(reader, data_inicio, data_fim, incidentes)
            else:
                # O servidor é identificado pelo caminho: raw/{empresa}/{hostname}/arquivo.csv
                partes = chave.split('/')
                if len(partes) < 4:
                    continue
                servidor = partes[2]  #terceiro segmento do caminho = hostname
                processar_metrica(reader, data_inicio, data_fim, metricas, servidor)

    #json final
    output = {
        "empresa": empresa,
        "gerado_em": datetime.now().isoformat(), #timestamp de quando a ETL rodou
        "mes_referencia": {"mes": mes, "ano": ano},
        "total_dias_mes": total_dias,
        "incidentes": incidentes, # dados pro heatmap
        "metricas": metricas # dados pros gráficos
    }

    chave_saida = f"client/{empresa}/dashboard/client_{mes:02d}_{ano}.json"

    s3.put_object(
        Bucket=BUCKET,
        Key=chave_saida,
        Body=json.dumps(output, ensure_ascii=False, indent=2),
        ContentType='application/json'
    )

    #confirma que tudo rodou e informa o arquivo gerado
    return {
        'statusCode': 200,
        'body': json.dumps({
            'mensagem': 'ETL concluída',
            'arquivo':  chave_saida
        })
    }


def processar_incidente(reader, data_inicio, data_fim, incidentes):
    #processa as linhas do CSV de incidentes e agrupa por servidor.
    #serve p/ oheatmap com quantidade de incidentes por dia.

    for linha in reader:
        #converte o texto do timestamp para um objeto de data real
        try:
            ts = datetime.strptime(linha['Timestamp'], '%Y-%m-%d %H:%M:%S')
        except (ValueError, KeyError):
            continue  #pula linhas com formato inválido ou coluna ausente

        data_incidente = ts.date()

        #aqui ele vai ignorar se nao for do mes do filtro
        if not (data_inicio <= data_incidente <= data_fim):
            continue

        servidor = linha['servidor']
        componente = linha['componente'].lower() 
        data_str = data_incidente.strftime('%Y-%m-%d')

        if servidor not in incidentes:
            incidentes[servidor] = {
                "TotalIncidentes": {
                    "total_mes": 0,   
                    "por_dia":   {}   
                },
                "DataIncidente": [],  
                "Componentes": {
                    "cpu":   [],      
                    "ram":   [],
                    "disco": [],
                },
                "Detalhes": []
            }

        sv = incidentes[servidor]

        # junta os incidentes do mesmo dia
        sv["DataIncidente"].append(data_str)
        sv["TotalIncidentes"]["total_mes"] += 1
        sv["TotalIncidentes"]["por_dia"][data_str] = (
            sv["TotalIncidentes"]["por_dia"].get(data_str, 0) + 1
        )
        
        #descricao p matheus usar
        sv["detalhes"].append({
            "data": data_str,
            "servidor": servidor,
            "componente": componente,
            "descricao": linha.get('descricao', '')
         })


        #mostra o componente q deu b.o
        if componente in sv["Componentes"]:
            sv["Componentes"][componente].append(data_str)

#aqui é p coisar os graficos
def processar_metrica(reader, data_inicio, data_fim, metricas, servidor):

    for linha in reader:
        try:
            ts = datetime.strptime(linha[COL_TIMESTAMP], '%Y-%m-%d %H:%M:%S')
            cpu = float(linha[COL_CPU])
            ram = float(linha[COL_RAM])
            disco = float(linha[COL_DISCO])
        except (ValueError, KeyError):
            continue

        data_registro = ts.date()

        # se n for do mês ele pula
        if not (data_inicio <= data_registro <= data_fim):
            continue

        data_str = data_registro.strftime('%Y-%m-%d')

        # Inicializa a estrutura do servidor se for a primeira vez que aparece
        if servidor not in metricas:
            metricas[servidor] = {
                "pico_mes": {"cpu": 0, "ram": 0, "disco": 0},  # maior valor do mês inteiro
                "dias": {}                                   # maior valor de cada dia
            }

        sv = metricas[servidor]

        # Inicializa o dia se ainda não existe
        if data_str not in sv["dias"]:
            sv["dias"][data_str] = {
                "cpu_pico": 0,
                "ram_pico": 0,
                "disco_pico": 0
            }

        dia = sv["dias"][data_str]

        #atualiza o pico do dia
        if cpu > dia["cpu_pico"]: dia["cpu_pico"] = round(cpu, 2)
        if ram > dia["ram_pico"]: dia["ram_pico"] = round(ram, 2)
        if disco > dia["disco_pico"]: dia["disco_pico"] = round(disco, 2)

        #atualiza o pico do mês
        if cpu > sv["pico_mes"]["cpu"]: sv["pico_mes"]["cpu"] = round(cpu, 2)
        if ram > sv["pico_mes"]["ram"]: sv["pico_mes"]["ram"] = round(ram, 2)
        if disco > sv["pico_mes"]["disco"]: sv["pico_mes"]["disco"] = round(disco, 2)
