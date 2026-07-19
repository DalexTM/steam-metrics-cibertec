import os
import logging
from src.bronze.ingest_steamspy import ingesta_datos_steamspy
from src.bronze.transform_steamspy_parquet import procesar_json_a_parquet
from src.bronze.transform_metacritic_parquet import procesar_excel_a_parquet

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "main.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(ruta_log, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def mostrar_menu():
    while True:
        print("\n============================================")
        print("    SISTEMA DE METRICAS STEAM - CIBERTEC")
        print("============================================")
        print("1. Descargar JSONs desde SteamSpy")
        print("2. Transformar SteamSpy JSONs a Parquet")
        print("3. Transformar Metacritic Excel a Parquet")
        print("0. Salir")
        print("============================================")

        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                logging.info("Iniciando pipeline nativo: Descarga desde SteamSpy API...")
                ingesta_datos_steamspy()
                logging.info("Pipeline finalizado: Descarga desde SteamSpy API completada.")
                
            elif opcion == "2":
                logging.info("Iniciando pipeline nativo: Consolidación de JSONs a Parquet...")
                procesar_json_a_parquet()
                logging.info("Pipeline finalizado: Consolidación a Parquet completada con éxito.")
                
            elif opcion == "3":
                logging.info("Iniciando pipeline nativo: Transformación de Metacritic Excel a Parquet...")
                procesar_excel_a_parquet()
                logging.info("Pipeline finalizado: Transformación de dataset Metacritic completada con éxito.")
                
            elif opcion == "0":
                logging.info("Saliendo del orquestador principal del programa.")
                break
                
            else:
                logging.warning("Opcion no valida. Intente de nuevo.")
                
        except Exception as e:
            logging.error(f"Falla crítica detectada durante la ejecución de la opción {opcion}: {e}")

        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    mostrar_menu()