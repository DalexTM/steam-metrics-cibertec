import os
import logging
from src.bronze.ingest_steamspy import ingesta_datos_steamspy
from src.bronze.ingest_metacritic import ingesta_datos_metacritic
from src.bronze.transform_steamspy_parquet import procesar_raw_a_parquet
from src.bronze.transform_metacritic_parquet import procesar_csv_a_parquet
from src.silver.transform_bronze_to_silver import procesar_bronze_a_silver
from src.gold.transform_silver_to_gold import procesar_silver_a_gold

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


def ejecutar_pipeline_completo():
    """Ejecuta todo el flujo de datos de manera secuencial desde la ingesta Raw hasta la capa Gold."""
    logger.info("============================================================")
    logger.info("INICIANDO EJECUCIÓN DEL PIPELINE COMPLETO: RAW -> GOLD")
    logger.info("============================================================")

    logger.info("\n--- [1/6] Ingesta Metacritic CSV ---")
    try:
        ingesta_datos_metacritic()
    except Exception as err:
        logger.error(f"Error en ingesta de Metacritic: {err}")
        raise

    logger.info("\n--- [2/6] Ingesta SteamSpy (Descarga Raw Avro) ---")
    try:
        ingesta_datos_steamspy()
    except Exception as err:
        logger.error(f"Error en ingesta de SteamSpy: {err}")
        raise

    logger.info("\n--- [3/6] Transformación SteamSpy Avro -> Bronze Parquet ---")
    procesar_raw_a_parquet()

    logger.info("\n--- [4/6] Transformación Metacritic CSV -> Bronze Parquet ---")
    procesar_csv_a_parquet()

    logger.info("\n--- [5/6] Pipeline de Calidad e Integración (Bronze -> Silver) ---")
    procesar_bronze_a_silver()

    logger.info("\n--- [6/6] Consolidación de Datamart (Silver -> Gold) ---")
    procesar_silver_a_gold()

    logger.info("\n============================================================")
    logger.info("PIPELINE COMPLETO FINALIZADO CON ÉXITO (RAW -> GOLD)")
    logger.info("============================================================")


def mostrar_menu():
    logger.info("Iniciando menú interactivo de Steam Metrics.")
    try:
        ingesta_datos_metacritic()
    except Exception as err:
        logger.error(f"No se pudo verificar o descargar el CSV de Metacritic: {err}")

    while True:
        print("\n============================================")
        print("    SISTEMA DE METRICAS STEAM - CIBERTEC")
        print("============================================")
        print("1. Descargar Avro desde SteamSpy")
        print("2. Transformar SteamSpy Avro a Parquet")
        print("3. Transformar Metacritic CSV a Parquet")
        print("4. Integración y Limpieza (Bronze -> Silver)")
        print("5. Consolidación de Datamart (Silver -> Gold)")
        print("6. Ejecutar Pipeline Completo (Raw -> Gold)")
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
                    "Iniciando pipeline nativo: Transformación de Metacritic CSV a Parquet..."
                )
                ingesta_datos_metacritic()
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

            elif opcion == "5":
                logger.info(
                    "Iniciando pipeline nativo: Consolidación de Datamart (Silver -> Gold)..."
                )
                procesar_silver_a_gold()
                logger.info(
                    "Pipeline finalizado: Procesamiento Silver a Gold completado con éxito."
                )

            elif opcion == "6":
                ejecutar_pipeline_completo()

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


def inicio():
    print("\n============================================================")
    print("           SISTEMA DE METRICAS STEAM - CIBERTEC             ")
    print("============================================================")
    print("¿Desea ejecutar todo el pipeline completo (Raw -> Gold)?")
    print("  [S] Sí, ejecutar pipeline completo en secuencia")
    print("  [N] No, abrir menú interactivo para ejecución manual")
    print("  [0] Salir")
    print("============================================================")

    modo = input("Seleccione una opción [S/N/0]: ").strip().lower()

    if modo in ["s", "si", "sí", "y", "yes", "1"]:
        try:
            ejecutar_pipeline_completo()
        except Exception as e:
            logger.error(f"Falla durante la ejecución del pipeline completo: {e}")
        input("\nPresione Enter para continuar...")
        mostrar_menu()
    elif modo in ["0", "exit", "salir", "q"]:
        logger.info("Saliendo del APP Steam Metrics.")
    else:
        mostrar_menu()


if __name__ == "__main__":
    inicio()
