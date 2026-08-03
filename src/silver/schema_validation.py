from pandera.pandas import Column, Check, DataFrameSchema


schema_games = DataFrameSchema(
    columns={
        # Llave
        "appid": Column(int, checks=[Check(lambda s: s.is_unique)], nullable=False),
        # Nombre
        "name": Column(str, nullable=False),
        # Fecha
        "Release_date": Column("datetime64[ns]", nullable=True),
        # Precio
        "price": Column(float, checks=[Check.greater_than_or_equal_to(0)]),
        # Precio inicial
        "initialprice": Column(float, checks=[Check.greater_than_or_equal_to(0)]),
        # Descuento
        "discount": Column(float, checks=[Check.greater_than_or_equal_to(0)]),
        # Edad requerida
        "Required_age": Column(float, checks=[Check.greater_than_or_equal_to(0)]),
        # Metacritic
        "Metacritic_score": Column(float, checks=[Check.in_range(0, 100)]),
        # User Score
        "userscore": Column(float, checks=[Check.in_range(0, 100)]),
        # Reviews
        "positive": Column(float, checks=Check.greater_than_or_equal_to(0)),
        "negative": Column(float, checks=Check.greater_than_or_equal_to(0)),
        # Sistemas Operativos
        "Windows": Column(bool),
        "Mac": Column(bool),
        "Linux": Column(bool),
    },
    coerce=True,
    strict=False,
)


def validate_schema(df):
    """
    Valida el DataFrame usando Pandera.
    """
    print("Duplicados appid:", df["appid"].duplicated().sum())
    print("\n--- Validación con Pandera ---")

    validated_df = schema_games.validate(df)

    print("Esquema validado correctamente.")

    return validated_df
