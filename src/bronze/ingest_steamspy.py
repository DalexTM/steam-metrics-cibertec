import json
import os
import requests
import time

carpeta_destino = os.path.join("data", "raw", "steamspy")

if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)
    print(f"Carpeta '{carpeta_destino}' creada con exito.")

pagina_actual = 0
cabeceras = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Iniciando descarga de archivos JSON unitarios desde SteamSpy...")

while True:
    url = "https://steamspy.com/api.php"
    parametros = {"request": "all", "page": str(pagina_actual)}

    print(f"Solicitando pagina {pagina_actual}...")
    try:
        response = requests.get(url, headers=cabeceras, params=parametros)

        if response.status_code != 200:
            print(
                f"Error de conexion (Status {response.status_code}). Deteniendo el proceso."
            )
            break

        try:
            data = response.json()
        except Exception as json_error:
            print(
                f"La respuesta de la pagina {pagina_actual} NO se pudo parsear a JSON."
            )
            print(f"Texto recibido (primeros 150 caracteres): {response.text[:150]}")
            break

        if not data or (isinstance(data, dict) and "error" in data):
            print(
                f"Se alcanzo el final de los datos en la pagina {pagina_actual}."
            )
            break

        nombre_archivo = f"page_{pagina_actual}.json"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Archivo '{ruta_completa}' guardado exitosamente.")

        pagina_actual += 1

        print("Esperando 60 segundos para cumplir con la politica de SteamSpy...")
        time.sleep(60)

    except Exception as e:
        print(f"Error inesperado en el proceso: {e}")
        break

print("Proceso de descarga finalizado.")