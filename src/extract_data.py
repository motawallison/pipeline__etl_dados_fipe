import requests
import json
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import time

MARCAS_MODELOS = {
    "25": ["5149", "11726"],  # Honda: Civic, HRV
    "56": ["9985", "9987"],  # Toyota: Corolla, Corolla Cross
    "59": ["10376", "10110"] # VW: T-Cross, Polo
}
URL_BASE = "https://parallelum.com.br/fipe/api/v1/"

def fetch_api(url: str):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        logging.error(f"Erro {response.status_code} na URL: {url}")
    except Exception as e:
        logging.error(f"Falha na conexão: {e}")
    return None

def extract_all():
    all_data = []

    for marca_id, modelos_ids in MARCAS_MODELOS.items():
        logging.info(f"Iniciando extração da Marca ID: {marca_id}")

        for modelo_id in modelos_ids:
            # 1. Busca os anos disponíveis para este modelo específico
            url_anos = f"{URL_BASE}/carros/marcas/{marca_id}/modelos/{modelo_id}/anos"
            anos_list = fetch_api(url_anos)

            if not anos_list:
                continue

            for ano in anos_list:
                ano_id = ano['codigo']
                # 2. Busca o detalhe final (Preço) de cada ano
                url_final = f"{url_anos}/{ano_id}"
                detalhe = fetch_api(url_final)

                if detalhe:
                    all_data.append(detalhe)
                    logging.info(f"Sucesso: {detalhe['Modelo']} - {detalhe['AnoModelo']}")
                
                # Pausa curta para respeitar a API
                time.sleep(0.2)

    return all_data

def save_data(data, output_path='data/all_marcas.json'):
    if not data:
        logging.warning("Nenhum dado para salvar.")
        return

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    logging.info(f"Total de {len(data)} registros salvos em {output_path}")

if __name__ == "__main__":
    dados_extraidos = extract_all()
    save_data(dados_extraidos)