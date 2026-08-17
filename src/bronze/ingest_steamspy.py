import json
import os
import requests
import time
import logging
from typing import List, Dict, Any
import fastavro

RUTA_ESQUEMA_STEAMSPY = os.path.join(
    "data", "raw", "steamspy", "schema", "steamspy_schema.avsc"
)

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


def cargar_esquema_steamspy(
    ruta_esquema: str = RUTA_ESQUEMA_STEAMSPY,
) -> dict[Any, Any] | list[Any] | str:
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
                    logger.error(
                        f"Error de conexion (Status {response.status_code}). Deteniendo el proceso."
                    )
                    break

                try:
                    data = response.json()
                except Exception as json_error:
                    logger.error(
                        f"La respuesta de la pagina {pagina_actual} NO se pudo parsear a JSON. Error: {json_error}"
                    )
                    break

                registros = [
                    {k: str(v) if v is not None else None for k, v in record.items()}
                    for record in data.values()
                ]

                nombre_archivo = f"page_{pagina_actual}.avro"
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

                guardar_avro_steamspy(registros, ruta_completa, esquema=esquema_avro)

                logger.info(
                    f"Archivo Avro '{ruta_completa}' guardado exitosamente con {len(registros)} registros."
                )
                pagina_actual += 1

                logger.info(
                    "Esperando 5 segundos para cumplir con la politica de SteamSpy..."
                )
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error inesperado en el proceso: {e}")
                break
    except KeyboardInterrupt:
        logger.warning("Proceso de descarga cancelado por el usuario (Ctrl + C).")

    ingestar_top100_steamcharts()
    logger.info("Proceso de descarga Avro finalizado.")


def obtener_siguiente_pagina_avro(carpeta_destino: str) -> int:
    """Calcula dinámicamente el siguiente número de página disponible."""
    archivos_existentes = [
        int(f.replace("page_", "").replace(".avro", ""))
        for f in os.listdir(carpeta_destino)
        if f.startswith("page_")
        and f.endswith(".avro")
        and f.replace("page_", "").replace(".avro", "").isdigit()
    ]
    return max(archivos_existentes) + 1 if archivos_existentes else 0


def obtener_top100_appids_steamcharts() -> List[int]:
    url_steamcharts = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_steamcharts, headers=cabeceras, timeout=15)
        if response.status_code == 200:
            data = response.json()
            ranks = data.get("response", {}).get("ranks", [])
            appids = [r["appid"] for r in ranks if "appid" in r]
            logger.info(
                f"Obtenidos {len(appids)} AppIDs del Top 100 en vivo de SteamCharts."
            )
            return appids
        else:
            logger.warning(
                f"Error al consultar SteamCharts API (Status {response.status_code})."
            )
    except Exception as e:
        logger.error(f"Error al conectar con SteamCharts API: {e}")
    return []


def ingestar_top100_steamcharts() -> str | None:
    carpeta_destino = os.path.join("data", "raw", "steamspy", "data")
    os.makedirs(carpeta_destino, exist_ok=True)
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    esquema_avro = cargar_esquema_steamspy()

    appids = obtener_top100_appids_steamcharts()
    if not appids:
        logger.warning("No se pudieron obtener AppIDs desde SteamCharts.")
        return None

    logger.info(
        f"Iniciando consulta individual en SteamSpy para los {len(appids)} juegos del Top 100..."
    )

    campos_esquema = [
        "appid",
        "name",
        "developer",
        "publisher",
        "score_rank",
        "positive",
        "negative",
        "userscore",
        "owners",
        "average_forever",
        "average_2weeks",
        "median_forever",
        "median_2weeks",
        "price",
        "initialprice",
        "discount",
        "ccu",
    ]

    registros = []
    for i, appid in enumerate(appids, 1):
        try:
            url_spy = "https://steamspy.com/api.php"
            resp = requests.get(
                url_spy,
                headers=cabeceras,
                params={"request": "appdetails", "appid": str(appid)},
                timeout=10,
            )

            if resp.status_code == 200:
                data_game = resp.json()
                if isinstance(data_game, dict) and data_game.get("name"):
                    precio = data_game.get("price")
                    if (
                        precio is None
                        or str(precio).strip() == ""
                        or str(precio).strip().lower() == "none"
                    ):
                        logger.info(
                            f"[{i}/{len(appids)}] Omitiendo AppID {appid} - '{data_game.get('name')}' por precio nulo (sin precio fijado en Steam)."
                        )
                        continue

                    rec_norm = {
                        campo: (
                            str(data_game.get(campo))
                            if data_game.get(campo) is not None
                            else None
                        )
                        for campo in campos_esquema
                    }
                    registros.append(rec_norm)
                    logger.info(
                        f"[{i}/{len(appids)}] AppID {appid} - '{data_game.get('name')}' descargado correctamente."
                    )
            time.sleep(0.4)
        except Exception as e:
            logger.warning(f"[{i}/{len(appids)}] Error al consultar AppID {appid}: {e}")

    if not registros:
        logger.warning(
            "No se pudo obtener ningún registro para el Top 100 de SteamSpy."
        )
        return None

    siguiente_pagina = obtener_siguiente_pagina_avro(carpeta_destino)
    nombre_archivo = f"page_{siguiente_pagina}.avro"
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

    guardar_avro_steamspy(registros, ruta_completa, esquema=esquema_avro)
    logger.info(
        f"Archivo Avro Top 100 '{ruta_completa}' guardado exitosamente con {len(registros)} registros."
    )
    return ruta_completa


if __name__ == "__main__":
    ingesta_datos_steamspy()
