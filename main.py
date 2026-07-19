import os
import subprocess
import sys
import logging

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

def ejecutar_script(subcarpeta, nombre_script):
    ruta_script = os.path.join("src", subcarpeta, nombre_script)
    logging.info(f"Iniciando ejecucion de: {ruta_script}")
    try:
        subprocess.run([sys.executable, ruta_script], check=True)
        logging.info(f"Ejecucion de {nombre_script} finalizada con exito.")
    except subprocess.CalledProcessError:
        logging.error(f"El script {nombre_script} termino con errores.")
    except Exception as e:
        logging.error(f"Error inesperado al ejecutar {nombre_script}: {e}")


def mostrar_menu():
    while True:
        print("\n============================================")
        print("    SISTEMA DE METRICAS STEAM - CIBERTEC")
        print("============================================")
        print("1. Descargar JSONs desde SteamSpy")
        print("2. Transformar SteamSpy JSONs a Parquet")
        print("3. Transformar Metacritic Excel a Parquet")
        print("4. ")
        print("0. Salir")
        print("============================================")

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            ejecutar_script("bronze", "ingest_steamspy.py")
        elif opcion == "2":
            ejecutar_script("bronze", "transform_steamspy_parquet.py")
        elif opcion == "3":
            ejecutar_script("bronze", "transform_metacritic_parquet.py")
        elif opcion == "4":
            logging.warning("")
        elif opcion == "0":
            logging.info("Saliendo del programa.")
            break
        else:
            logging.warning("Opcion no valida. Intente de nuevo.")

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    mostrar_menu()