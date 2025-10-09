# Como funciona o equal-logger
- O equal-logger é uma biblioteca que facilita o registro de logs em projetos na Azure e GCP. 
- Ele cria uma conexão com o storage da cloud e fica responsável por armazenar as mensagens de log em formato parquet, seguindo uma hierarquia de pastas.
- O usuário só precisa importar o módulo, criar uma instância do Logger, registrar as mensagens de log e salvar. Todos os meta-dados necessários são coletados automaticamente.

# Como instalar o equal-logger
Execute os comando abaixo para atualizar o repositório de bibliotecas e baixar a versão mais recente do equal-logger:
```
py -m pip install --upgrade pip
pip install equal-logger
```

# Como preparar o ambiente antes de utilizar
1. [Como configurar a biblioteca com Google Cloud Storage](https://app.clickup.com/9007027078/v/dc/8cdrmw6-15633/8cdrmw6-16233)
2. [Como configurar a biblioteca com Azure ADLS](https://app.clickup.com/9007027078/v/dc/8cdrmw6-15633/8cdrmw6-16213)

# Como incluir nos códigos

Comece importando o módulo:
```python
from equal_logger import Logger
```

Após importar o módulo, crie uma instância do Logger:
```python
logger = Logger(
    cloud="GCP",  # a cloud que está sendo utilizada ("GCP" ou "AZURE").
    project="evo-operacoes",  # nome do projeto, exatamente como no nome do bucket/container.
    script_name="wehelp_engaging_probability.py",  # nome do script que está rodando.
    data_source="WEHELP",  # nome da fonte de dados que está sendo extraída/transformada ou qualquer outro rótulo. (exemplo "META ADS").
    credentials="credentials.json",  # caminho para o arquivo de credenciais.
)
```

Agora você pode utilizar o logger para registrar mensagens de log:
```python
logger.success("titulo 1", "descricao 1") # use para registrar mensagens de sucesso.
logger.info("titulo 1", "descricao 1") # use para registrar mensagens de informação.
logger.error("titulo 1", "descricao 1") # use para registrar mensagens de erro.
```

Por fim, finalize o logger. Este comando grava no storage os logs registrados, use-o somente uma vez ao final do script:
```python
logger.save()
```

Exemplo de uso:
```python
from equal_logger import Logger

logger = Logger(
    cloud="GCP",  
    project="evo-operacoes", 
    script_name="wehelp_engaging_probability.py",  
    data_source="WEHELP", 
    credentials="credentials.json", 
)

# executando as requisições e salvando no GCS
for retentativa in range(QUANTIDADE_DE_RETENTATIVAS):

    try:
        data = request_from_wehelp(endpoint)
        save_to_gcs(json.dumps(data))
        logger.log_success('dim_clientes', 'Extraído com sucesso!')
        break

    except Exception as e:
        logger.log_info('dim_clientes', f'RETRY: {retentativa} \n {e}')
        time.sleep(5)

else:
    logger.log_error('dim_clientes', f'Tentativas esgotadas! \n {e}')


logger.log_save()
```