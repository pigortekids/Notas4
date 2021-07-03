from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from funcoes_enem import extract_all, Dataset, parse
import os

PATH_EDUCACAO = '/home/pigortekids/projects/educacao'
SCRAPERS_HOME = PATH_EDUCACAO + '/scrapers/inep'
DATA = PATH_EDUCACAO + '/data'
TMP_DATA = PATH_EDUCACAO + '/tmp'
METADATA = PATH_EDUCACAO + '/metadata'

args = {
    'owner': 'Igor Correa',
}

dag = DAG(
    dag_id='etl_microdados_inep_enem',
    start_date=datetime(2021,6,23,20,0,0),
    schedule_interval='@once',
    default_args=args
)

scrape_data = BashOperator(
    task_id='scrape_data',
    bash_command=f'cd {SCRAPERS_HOME} && scrapy crawl microdados_enem -a data_path={TMP_DATA}',
    dag=dag
)

# Descompactar
extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=extract_all,
    op_kwargs={
        'src': TMP_DATA,
        'dest': DATA,
        'metadata_dir': METADATA,
    },
    dag=dag
)

# Converter para parquet
parse_data = PythonOperator(
    task_id='parse_date',
    python_callable=parse,
    op_kwargs={
        'path': os.path.join(DATA, 'dados_1998.csv'),
        'catalog': os.path.join(METADATA, 'dicionario_dados_1998.xlsx#MICRODADOS_ENEM_1998'),
        'year': 1998,
        'dest': DATA
    },
    dag=dag
)

scrape_data >> extract_data >> parse_data