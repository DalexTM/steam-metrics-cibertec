import os
import shutil
import logging
import kagglehub

carpeta_logs = "logs"
os.makedirs(carpeta_logs, exist_ok=True)
ruta_log = os.path.join(carpeta_logs, "ingest_metacritic.log")

logger = logging.getLogger("ingest_metacritic")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

DIRECTORIO_DESTINO = os.path.join("data", "raw", "metacritic")
NOMBRE_ARCHIVO = "metacritic.csv"
KAGGLE_DATASET_HANDLE = "diegoapazaalarcon/metacritic-steam"


def ingesta_datos_metacritic() -> str:
    """Verifica si existe metacritic.csv en data/raw/metacritic.

    Si no se encuentra, lo descarga automáticamente desde Kaggle.
    """
    ruta_csv_destino = os.path.join(DIRECTORIO_DESTINO, NOMBRE_ARCHIVO)

    if os.path.exists(ruta_csv_destino):
        logger.info(
            f"El archivo '{NOMBRE_ARCHIVO}' ya existe en '{DIRECTORIO_DESTINO}'. Se omite la descarga de Kaggle."
        )
        return ruta_csv_destino

    logger.info(
        f"Archivo '{NOMBRE_ARCHIVO}' no encontrado en '{DIRECTORIO_DESTINO}'. Descargando dataset desde Kaggle ({KAGGLE_DATASET_HANDLE})..."
    )

    try:
        ruta_descargada = kagglehub.dataset_download(KAGGLE_DATASET_HANDLE)

        archivo_csv_origen = None
        for root, _, files in os.walk(ruta_descargada):
            for file in files:
                if file.endswith(".csv"):
                    archivo_csv_origen = os.path.join(root, file)
                    break
            if archivo_csv_origen:
                break

        if not archivo_csv_origen:
            raise FileNotFoundError(
                f"No se encontró ningún archivo CSV en el dataset descargado de Kaggle en {ruta_descargada}"
            )

        shutil.copy(archivo_csv_origen, ruta_csv_destino)
        logger.info(
            f"Descarga e ingesta de Metacritic completada con éxito: {ruta_csv_destino}"
        )
        return ruta_csv_destino

    except Exception as e:
        logger.error(
            f"Error al descargar o copiar el dataset de Metacritic desde Kaggle: {e}"
        )
        raise


if __name__ == "__main__":
    ingesta_datos_metacritic()
