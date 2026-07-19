import os
import subprocess
import sys


def ejecutar_script(subcarpeta, nombre_script):
    ruta_script = os.path.join("src", subcarpeta, nombre_script)

    if not os.path.exists(ruta_script):
        print(f"\nError: El archivo '{ruta_script}' no existe.")
        return

    print(f"\nIniciando ejecucion de: {ruta_script}\n")
    try:
        subprocess.run([sys.executable, ruta_script], check=True)
        print(f"\nEjecucion de {nombre_script} finalizada con exito.")
    except subprocess.CalledProcessError:
        print(f"\nError: El script {nombre_script} termino con errores.")
    except Exception as e:
        print(f"\nError inesperado al ejecutar {nombre_script}: {e}")


def mostrar_menu():
    while True:
        print("\n============================================")
        print("    SISTEMA DE METRICAS STEAM - CIBERTEC")
        print("============================================")
        print("1. Descargar JSONs desde SteamSpy")
        print("2. Transformar JSONs de SteamSpy a formato Parquet")
        print("3. Transformar dataset de Metacritic a formato Parquet")
        print("4.")
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
            print("")
        elif opcion == "0":
            print("\nSaliendo del programa.")
            break
        else:
            print("\nOpcion no valida. Intente de nuevo.")

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    mostrar_menu()