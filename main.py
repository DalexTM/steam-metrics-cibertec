import pandas as pd
import requests

# 1. Ingesta de SteamSpy (Capa Bronze)
# Obtienes la lista de juegos más populares o los específicos de estrategia
url_spy = "https://steamspy.com/api.php?request=all" 
data_spy = requests.get(url_spy).json()
df_spy = pd.DataFrame(data_spy).T # Transponer porque viene indexado por ID

df_spy.to_csv("bronze_steamspy.csv", index=False)


# 2. Ingesta de RAWG (Capa Bronze)
# Solicitas los detalles del juego en RAWG usando el id de Steam para traer Metacritic y Tags
# (Nota: RAWG te permite filtrar directamente por su endpoint de juegos)
url_rawg = "https://api.rawg.io/api/games?key=f5e423f2920b4ee396e250ddcf40ccce&platforms=4" # 4 es el ID de PC/Steam
data_rawg = requests.get(url_rawg).json()
df_rawg = pd.DataFrame(data_rawg['results'])

df_rawg.to_csv("bronze_rawg.csv", index=False)

# 3. Cruzar la información (Hacia la Capa Silver)
# Unes ambas tablas usando el ID de Steam para consolidar la base de datos
# df_final = pd.merge(df_spy, df_rawg, left_on='appid', right_on='id_or_external_id')