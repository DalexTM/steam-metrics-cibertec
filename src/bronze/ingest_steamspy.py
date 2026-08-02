import json
import os
import requests
import time
import logging
from typing import List, Dict, Any
import fastavro

RUTA_ESQUEMA_STEAMSPY = os.path.join("data", "raw", "steamspy", "schema", "steamspy_schema.avsc")

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "ingest_steamspy.log")

logger = logging.getLogger("ingest_steamspy")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

def cargar_esquema_steamspy(ruta_esquema: str = RUTA_ESQUEMA_STEAMSPY) -> dict[Any, Any] | list[Any] | str:
    """Carga y parsea el esquema Avro desde el archivo .avsc separado."""
    with open(ruta_esquema, "r", encoding="utf-8") as f:
        schema_json = json.load(f)
    return fastavro.parse_schema(schema_json)

def guardar_avro_steamspy(
    registros: List[Dict[str, Any]],
    ruta_salida: str,
    esquema: dict[Any, Any] | list[Any] | str | None = None,
) -> str:
    """Escribe una lista de registros en formato Avro."""
    if esquema is None:
        esquema = cargar_esquema_steamspy()

    with open(ruta_salida, "wb") as out:
        fastavro.writer(out, esquema, registros)
    return ruta_salida


def ingesta_datos_steamspy():

    carpeta_destino = os.path.join("data", "raw", "steamspy", "data")
    pagina_actual = 0
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    esquema_avro = cargar_esquema_steamspy()
    logger.info("Iniciando descarga de archivos AVRO desde SteamSpy...")

    try:
        while True:
            url = "https://steamspy.com/api.php"
            parametros = {"request": "all", "page": str(pagina_actual)}

            logger.info(f"Solicitando pagina {pagina_actual}...")
            try:
                response = requests.get(url, headers=cabeceras, params=parametros)

                if response.status_code != 200:
                    logger.error(f"Error de conexion (Status {response.status_code}). Deteniendo el proceso.")
                    break

                try:
                    data = response.json()
                except Exception as json_error:
                    logger.error(f"La respuesta de la pagina {pagina_actual} NO se pudo parsear a JSON. Error: {json_error}")
                    break

                registros = [
                    {k: str(v) if v is not None else None for k, v in record.items()}
                    for record in data.values()
                ]

                nombre_archivo = f"page_{pagina_actual}.avro"
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

                guardar_avro_steamspy(registros, ruta_completa, esquema=esquema_avro)

                logger.info(f"Archivo Avro '{ruta_completa}' guardado exitosamente con {len(registros)} registros.")
                pagina_actual += 1

                logger.info("Esperando 5 segundos para cumplir con la politica de SteamSpy...")
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error inesperado en el proceso: {e}")
                break
    except KeyboardInterrupt:
        logger.warning("Proceso de descarga cancelado por el usuario (Ctrl + C).")

    logger.info("Proceso de descarga Avro finalizado.")

if __name__ == "__main__":
    ingesta_datos_steamspy()