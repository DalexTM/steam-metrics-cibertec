import os
import logging
from src.bronze.ingest_steamspy import ingesta_datos_steamspy
from src.bronze.transform_steamspy_parquet import procesar_raw_a_parquet
from src.bronze.transform_metacritic_parquet import procesar_csv_a_parquet
from src.silver.synthetic_ingest import main as procesar_bronze_a_silver

carpeta_logs = "logs"
os.makedirs(carpeta_logs, exist_ok=True)
ruta_log = os.path.join(carpeta_logs, "main.log")

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)


def mostrar_menu():
    logger.info("Iniciando APP Steam Metrics.")
    while True:
        print("\n============================================")
        print("    SISTEMA DE METRICAS STEAM - CIBERTEC")
        print("============================================")
        print("1. Descargar Avro desde SteamSpy")
        print("2. Transformar SteamSpy Avro a Parquet")
        print("3. Transformar Metacritic CSV a Parquet")
        print("4. Integración y Limpieza (Bronze -> Silver)")
        print("0. Salir")
        print("============================================")

        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                logger.info(
                    "Iniciando pipeline nativo: Descarga en Avro desde SteamSpy API..."
                )
                ingesta_datos_steamspy()
                logger.info(
                    "Pipeline finalizado: Descarga desde SteamSpy API completada."
                )

            elif opcion == "2":
                logger.info(
                    "Iniciando pipeline nativo: Transformación de SteamSpy Avro a Parquet..."
                )
                procesar_raw_a_parquet()
                logger.info(
                    "Pipeline finalizado: Transformación a Parquet completada con éxito."
                )

            elif opcion == "3":
                logger.info(
                    "Iniciando pipeline nativo: Transformación de Metacritic CSV a ParquetF..."
                )
                procesar_csv_a_parquet()
                logger.info(
                    "Pipeline finalizado: Transformación a Parquet completada con éxito."
                )

            elif opcion == "4":
                logger.info(
                    "Iniciando pipeline nativo: Integración y Limpieza (Bronze -> Silver)..."
                )
                procesar_bronze_a_silver()
                logger.info(
                    "Pipeline finalizado: Procesamiento Bronze a Silver completado con éxito."
                )

            elif opcion == "0":
                logger.info("Saliendo del APP Steam Metrics.")
                break

            else:
                logger.warning("Opcion no valida. Intente de nuevo.")

        except Exception as e:
            logger.error(
                f"Falla crítica detectada durante la ejecución de la opción {opcion}: {e}"
            )

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    mostrar_menu()
