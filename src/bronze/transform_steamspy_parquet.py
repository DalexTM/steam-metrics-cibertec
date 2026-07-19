import json
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DIRECTORIO_ENTRADA = os.path.join("data", "raw", "steamspy")
DIRECTORIO_SALIDA = os.path.join("data", "bronze")

def tamano_kb(ruta: str) -> float:
    return os.path.getsize(ruta) / 1024

# Persistencia en formato optimizado Parquet aplicando tipado estricto
def guardar_parquet(df: pd.DataFrame, nombre: str) -> str:
    if not os.path.exists(DIRECTORIO_SALIDA):
        os.makedirs(DIRECTORIO_SALIDA)
        print(f"Carpeta creada automaticamente: {DIRECTORIO_SALIDA}")

    ruta = os.path.join(DIRECTORIO_SALIDA, f"{nombre}.parquet")

    # Definicion del esquema de datos estructurado para PyArrow
    esquema_steamspy = pa.schema(
        [
            ("appid", pa.int64()),
            ("name", pa.string()),
            ("developer", pa.string()),
            ("publisher", pa.string()),
            ("score_rank", pa.string()),
            ("positive", pa.int32()),
            ("negative", pa.int32()),
            ("userscore", pa.int32()),
            ("owners", pa.string()),
            ("average_forever", pa.int32()),
            ("average_2weeks", pa.int32()),
            ("median_forever", pa.int32()),
            ("median_2weeks", pa.int32()),
            ("price", pa.float32()),
            ("initialprice", pa.float32()),
            ("discount", pa.int32()),
            ("ccu", pa.int32()),
        ]
    )

    # Cast de columnas y manejo de valores nulos para acoplarse al esquema de PyArrow
    df["appid"] = pd.to_numeric(df["appid"], errors="coerce").fillna(0).astype("int64")
    df["name"] = df["name"].astype(str)
    df["developer"] = df["developer"].astype(str)
    df["publisher"] = df["publisher"].astype(str)
    df["score_rank"] = df["score_rank"].astype(str)
    df["positive"] = pd.to_numeric(df["positive"], errors="coerce").fillna(0).astype("int32")
    df["negative"] = pd.to_numeric(df["negative"], errors="coerce").fillna(0).astype("int32")
    df["userscore"] = pd.to_numeric(df["userscore"], errors="coerce").fillna(0).astype("int32")
    df["owners"] = df["owners"].astype(str)
    df["average_forever"] = pd.to_numeric(df["average_forever"], errors="coerce").fillna(0).astype("int32")
    df["average_2weeks"] = pd.to_numeric(df["average_2weeks"], errors="coerce").fillna(0).astype("int32")
    df["median_forever"] = pd.to_numeric(df["median_forever"], errors="coerce").fillna(0).astype("int32")
    df["median_2weeks"] = pd.to_numeric(df["median_2weeks"], errors="coerce").fillna(0).astype("int32")
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).astype("float32")
    df["initialprice"] = pd.to_numeric(df["initialprice"], errors="coerce").fillna(0.0).astype("float32")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0).astype("int32")
    df["ccu"] = pd.to_numeric(df["ccu"], errors="coerce").fillna(0).astype("int32")

    # Serializacion y escritura fisica del archivo con compresion Snappy
    tabla = pa.Table.from_pandas(df, schema=esquema_steamspy, preserve_index=False)
    pq.write_table(tabla, ruta, compression="snappy")
    print(f"  Guardado: {ruta}  ({tamano_kb(ruta):.2f} KB)")
    return ruta


# Proceso de lectura, extraccion y consolidacion de archivos planos locales
def consolidar_jsons_a_parquet():
    if not os.path.exists(DIRECTORIO_ENTRADA):
        print(f"Error: No existe la carpeta {DIRECTORIO_ENTRADA}")
        return

    archivos = [f for f in os.listdir(DIRECTORIO_ENTRADA) if f.endswith(".json")]

    if not archivos:
        print("No se encontraron archivos JSON para procesar.")
        return

    print(f"Se encontraron {len(archivos)} archivos JSON. Iniciando lectura...")

    dataframes_acumulados = []

    for archivo in archivos:
        ruta_archivo = os.path.join(DIRECTORIO_ENTRADA, archivo)

        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                contenido_json = json.load(f)

            # Conversion de la respuesta transpuesta para estructurar la tabla
            df_pagina = pd.DataFrame(contenido_json).T
            
            # Reestructuracion del indice de fila para transformarlo en columna de ID
            df_pagina = df_pagina.reset_index().rename(columns={"index": "appid_raw"})
            
            # Limpieza y prevencion de duplicidad en la clave primaria
            if "appid" in df_pagina.columns:
                df_pagina = df_pagina.drop(columns=["appid"])
            
            df_pagina = df_pagina.rename(columns={"appid_raw": "appid"})
            dataframes_acumulados.append(df_pagina)

        except Exception as e:
            print(f"Error al procesar el archivo {archivo}: {e}")
            continue

    if dataframes_acumulados:
        df_steamspy_total = pd.concat(dataframes_acumulados, ignore_index=True)
        print(f"Consolidacion completa. Registros totales: {len(df_steamspy_total)}")

        guardar_parquet(df_steamspy_total, "bronze_steamspy")
    else:
        print("No se pudo estructurar ninguna informacion.")


if __name__ == "__main__":
    consolidar_jsons_a_parquet()