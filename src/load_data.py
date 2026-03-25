import os
import json
import pandas as pd
import pandas_gbq
import logging
from pathlib import Path
from google.oauth2 import service_account
from transform_data import create_data_frame, data_transformation, PATH_JSON

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PROJECT_ID = "pipeline-etl-fipe"
DATASET_ID = "etl_fipe_date"         
TABLE_ID = "tb_fipe_historico"     

def load_to_bigquery(df: pd.DataFrame):
    try:
        logging.info(f"Iniciando carga no BigQuery: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
        
        # Tenta ler a secret do ambiente (GitHub Actions)
        env_credentials = os.getenv("GCP_SA_KEY")
        
        if env_credentials:
            # Se estiver no GitHub, reconstrói as credenciais a partir da string
            logging.info("Usando credenciais da variável de ambiente (GitHub Actions)")
            info = json.loads(env_credentials)
            credentials = service_account.Credentials.from_service_account_info(info)
        else:
            # Se estiver local (VS Code), usa o arquivo físico
            logging.info("Usando credenciais do arquivo local")
            KEY_PATH = Path(__file__).parent.parent / 'config' / 'google_credentials.json'
            credentials = service_account.Credentials.from_service_account_file(str(KEY_PATH))
        
        pandas_gbq.to_gbq(
            df,
            destination_table=f"{DATASET_ID}.{TABLE_ID}",
            project_id=PROJECT_ID,
            if_exists='append',
            credentials=credentials
        )
        
        logging.info("Carga concluída com sucesso!")
        
    except Exception as e:
        logging.error(f"Erro ao carregar dados para o BigQuery: {e}")

if __name__ == "__main__":
    df_raw = create_data_frame(PATH_JSON)
    df_processed = data_transformation(df_raw)
    load_to_bigquery(df_processed)