import json
import os
import requests
import time
import logging

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "ingest_steamspy.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(ruta_log, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

carpeta_destino = os.path.join("data", "raw", "steamspy")
pagina_actual = 0
cabeceras = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

logging.info("Iniciando descarga de archivos JSON unitarios desde SteamSpy...")

while True:
    url = "https://steamspy.com/api.php"
    parametros = {"request": "all", "page": str(pagina_actual)}

    logging.info(f"Solicitando pagina {pagina_actual}...")
    try:
        response = requests.get(url, headers=cabeceras, params=parametros)

        if response.status_code != 200:
            logging.error(f"Error de conexion (Status {response.status_code}). Deteniendo el proceso.")
            break

        try:
            data = response.json()
        except Exception as json_error:
            logging.error(f"La respuesta de la pagina {pagina_actual} NO se pudo parsear a JSON.")
            break

        if not data or (isinstance(data, dict) and "error" in data):
            logging.info(f"Se alcanzo el final de los datos en la pagina {pagina_actual}.")
            break

        nombre_archivo = f"page_{pagina_actual}.json"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logging.info(f"Archivo '{ruta_completa}' guardado exitosamente.")
        pagina_actual += 1

        logging.info("Esperando 60 segundos para cumplir con la politica de SteamSpy...")
        time.sleep(60)

    except Exception as e:
        logging.error(f"Error inesperado en el proceso: {e}")
        break

logging.info("Proceso de descarga finalizado.")