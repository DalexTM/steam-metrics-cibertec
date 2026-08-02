import json
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import fastavro
import logging

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "transform_steamspy_parquet.log")

logger = logging.getLogger("transform_steamspy_parquet")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

DIRECTORIO_ENTRADA = os.path.join("data", "raw", "steamspy", "data")
DIRECTORIO_SALIDA = os.path.join("data", "bronze")

def tamanio_kb(ruta: str) -> float:
    return os.path.getsize(ruta) / 1024

def leer_avro_steamspy(ruta_entrada: str):
    """Lee un archivo Avro y retorna la lista de registros."""
    records = []
    with open(ruta_entrada, "rb") as fo:
        reader = fastavro.reader(fo)
        for record in reader:
            records.append(record)
    return records

def guardar_parquet(df: pd.DataFrame, nombre: str) -> str:
    ruta = os.path.join(DIRECTORIO_SALIDA, f"{nombre}.parquet")

    logger.info("Convirtiendo DataFrame consolidado a tabla PyArrow...")
    tabla = pa.Table.from_pandas(df, preserve_index=False)
    
    logger.info("Escribiendo archivo Parquet en disco...")
    pq.write_table(tabla, ruta, compression="snappy")
    logger.info(f"Guardado exitoso: {ruta} ({tamanio_kb(ruta):.2f} KB)")
    return ruta

def procesar_raw_a_parquet():
    
    logger.info(f"Buscando archivos de entrada en la ruta: {DIRECTORIO_ENTRADA}")
    if not os.path.exists(DIRECTORIO_ENTRADA):
        logger.warning("El directorio de entrada no existe.")
        return

    archivos_avro = sorted(
        [f for f in os.listdir(DIRECTORIO_ENTRADA) if f.endswith(".avro")],
        key=lambda x: int(x.replace("page_", "").replace(".avro", "")) if x.replace("page_", "").replace(".avro", "").isdigit() else x
    )

    archivos_json = sorted(
        [f for f in os.listdir(DIRECTORIO_ENTRADA) if f.endswith(".json")],
        key=lambda x: int(x.replace("page_", "").replace(".json", "")) if x.replace("page_", "").replace(".json", "").isdigit() else x
    )

    archivos_a_procesar = archivos_avro if archivos_avro else archivos_json

    if not archivos_a_procesar:
        logger.warning("No se encontraron archivos .avro ni .json para procesar.")
        return

    tipo_archivo = "AVRO" if archivos_avro else "JSON"
    logger.info(f"Se encontraron {len(archivos_a_procesar)} archivos {tipo_archivo}. Iniciando lectura y unificacion...")
    dataframes_acumulados = []

    for archivo in archivos_a_procesar:
        ruta_archivo = os.path.join(DIRECTORIO_ENTRADA, archivo)
        try:
            logger.info(f"Procesando archivo ({tipo_archivo}): {archivo}")
            if archivo.endswith(".avro"):
                registros = leer_avro_steamspy(ruta_archivo)
                df_pagina = pd.DataFrame(registros)
            else:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    contenido_json = json.load(f)
                df_pagina = pd.DataFrame(contenido_json).T
                df_pagina = df_pagina.reset_index(drop=True)

            dataframes_acumulados.append(df_pagina)
        except Exception as e:
            logger.error(f"Error al procesar el archivo {archivo}: {e}")
            continue

    if dataframes_acumulados:
        logger.info("Concatenando estructuras en un solo DataFrame...")
        df_steamspy_total = pd.concat(dataframes_acumulados, ignore_index=True)
        logger.info(f"Consolidacion completa. Registros totales: {len(df_steamspy_total)}")
        guardar_parquet(df_steamspy_total, "bronze_steamspy")
        logger.info("Procesamiento de SteamSpy a Parquet finalizado con exito.")
    else:
        logger.warning("No se pudo estructurar ninguna informacion.")

if __name__ == "__main__":
    procesar_raw_a_parquet()