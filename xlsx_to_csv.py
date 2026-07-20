import os
import pandas as pd

ruta_excel = os.path.join("data", "raw", "metacritic", "metacritic.xlsx")
ruta_csv = os.path.join("data", "raw", "metacritic", "metacritic.csv")

print("Leyendo Excel...")
df = pd.read_excel(ruta_excel)

print("Guardando como CSV seguro con UTF-8 y entrecomillado estricto...")
df.to_csv(
    ruta_csv, 
    index=False, 
    encoding="utf-8", 
    sep=","
)

print("Conversión completada")