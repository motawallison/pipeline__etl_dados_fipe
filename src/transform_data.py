import pandas as pd
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


PATH_JSON = Path(__file__).parent.parent / 'data' / 'all_marcas.json'

COLUMNS_TO_DROP = ["SiglaCombustivel"]
COLUMNS_TO_RENAME = {"Combustivel": "TipoCombustivel"}
MESES_REF = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }

def create_data_frame(path_file: Path) -> pd.DataFrame:
    logging.info(f"Lendo arquivo JSON em: {path_file}")
    
    if not path_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path_file}")
    
    with open(path_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logging.info(f"DataFrame criado com {len(df)} linha(s)")
    return df

def drop_columns(df: pd.DataFrame, columns_names: list[str]) -> pd.DataFrame:
    # Verificando se as colunas existem antes de tentar deletar para evitar erros
    cols_presentes = [c for c in columns_names if c in df.columns]
    logging.info(f"Removendo colunas: {cols_presentes}")
    df = df.drop(columns=cols_presentes)
    return df

def rename_columns(df: pd.DataFrame, columns_dict: dict[str, str]) -> pd.DataFrame: 
    logging.info(f"Renomeando colunas conforme dicionário fornecido")
    df = df.rename(columns=columns_dict)
    return df

def normalize_datetime_columns(df: pd.DataFrame, columns_names: list[str]) -> pd.DataFrame:
    for col in columns_names:
        if col in df.columns:
            logging.info(f"Normalizando coluna de data: {col}")
            
            def parse_fipe_date(text):
                try:
                    parts = text.lower().split() 
                    mes = MESES_REF.get(parts[0], '01')
                    ano = parts[2]
                    return f"{ano}-{mes}-01"
                except:
                    return None

            df[col] = pd.to_datetime(df[col].apply(parse_fipe_date))
    return df

def normalize_currency_columns(df: pd.DataFrame, columns_names: list[str]) -> pd.DataFrame:
    for col in columns_names:
        if col in df.columns:
            logging.info(f"Convertendo coluna {col} para float")
            df[col] = (
                df[col]
                .str.replace('R$ ', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )
    return df

def data_transformation(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Limpando registros com AnoModelo inválido (32000)...")
    df['AnoModelo'] = pd.to_numeric(df['AnoModelo'], errors='coerce')
    df = df[df['AnoModelo'] != 32000].copy()
    logging.info(f"Filtro aplicado. Linhas restantes: {len(df)}")

    df = drop_columns(df, COLUMNS_TO_DROP)
    df = rename_columns(df, COLUMNS_TO_RENAME)
    df = normalize_datetime_columns(df, ['MesReferencia'])
    df = normalize_currency_columns(df, ['Valor'])
    
    logging.info("Convertendo AnoModelo para o tipo Date...")
    df['AnoModelo'] = pd.to_datetime(df['AnoModelo'].astype(str) + '-01-01')

    logging.info("Transformações concluídas")

    return df