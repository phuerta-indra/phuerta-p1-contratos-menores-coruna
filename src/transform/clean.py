import pandas as pd
from src.utils.config import get_silver_path, get_gold_path
from src.utils.utils import read_csv, export_csv

def explore(df):

    print("\n--- PRIMERAS FILAS ---")
    pd.set_option("display.max_columns", None)
    print(df.head())

    print("\n--- DIMENSIONES ---")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")

    print("\n--- TIPOS DE DATOS ---")
    print(df.dtypes)

    print("\n--- VALORES NULOS ---")
    print(df.isnull().sum())

    print("\n--- PORCENTAJE DE NULOS ---")
    print((df.isnull().mean() * 100).round(2))

    print("\n--- REGISTROS DUPLICADOS ---")
    print(df.duplicated().sum())

    print("\n--- VALORES ÚNICOS ---")
    for column in df.columns:
        print(f"{column}: {df[column].nunique()} valores únicos")

    print("\n--- DISTRIBUCIONES ---")
    print(df.describe())

    print("---------------------------------------------")

    return df


def clean_text(df):

    # Limpiar espacios en blanco al inicio y al final de las cadenas de texto

    text_columns = df.columns

    for col in text_columns:
        df[col] = df[col].str.strip()

    return df


def clean_prices(df):

    "Convertir los precios a dato numérico"

    # Celda con dos anualidades: la sustituimos por la suma (22.209,07 + 31.882,29)
    df["precio"] = df["precio"].replace({
        "22.209,07€ (2023). 31.882,29 € (2024)": "54.091,36"
    })

    cleaned = (
        df["precio"]
        .str.replace("€", "", regex=False)
    )

    # Para cambiar los precios con formato 1.234,56
    eu_format = cleaned.str.contains(",", na=False)

    cleaned.loc[eu_format] = (
        cleaned.loc[eu_format]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    converted = pd.to_numeric(cleaned, errors="coerce")

    # Para identificar valores que pandas no ha podido convertir a número 
    # (valores tipo: 18.000,00 € y dos anualidades: 22.209,07€ (2023). 31.882,29 € (2024))

    fallidos = df.loc[converted.isna() & df["precio"].notna(), "precio"]
    print(f"Precios no convertibles: {len(fallidos)}")
    print(fallidos)

    df["precio"] = converted

    return df


def clean_dates(df):

    "Convertir las fechas a forma datetime"

    # Quitamos las horas de las fechas
    date = df["fecha"].str[:10]

    # Formato principal de las fechas en los datos obtenidos

    date_iso = pd.to_datetime(date, format="%Y-%m-%d", errors="coerce")

    # Formato secundario de las fechas en los datos obtenidos
    date_es = pd.to_datetime(date, format="%d/%m/%Y", errors="coerce")

    # Si una falla nos quedamos con la otra
    convertido = date_iso.fillna(date_es)

    # Hay una fecha con un año erroneo (2022 en vez de 2023), como las 
    # referencias más proximas son del 2023 voy a corregir el año de la fecha
    # en lugar de eliminar la fila. La referencia era: 237/2023/31

    # Para ver las referencias proximas se puede ejecutar:
    """fila = df[df["fecha"] < "2023-01-01"]
    print(fila[["referencia", "fecha"]])
    
    prefijo = fila["referencia"].iloc[0].split("/")[0]
    vecinos = df[df["referencia"].str.startswith(prefijo + "/2023/")].sort_values("referencia")
    print(vecinos[["referencia", "fecha"]])"""

    ref = "237/2023/31" 
    mask = df["referencia"] == ref
    convertido.loc[mask] = convertido.loc[mask] + pd.DateOffset(years=1)


    # Filas donde había un valor original pero ningún formato funcionó
    fallidos = df.loc[convertido.isna() & df["fecha"].notna(), "fecha"]
    print(f"Fechas no convertibles: {len(fallidos)}")
    print(fallidos)

    df["fecha"] = convertido

    return df



def clean_categories(df):

    "Convertir todos los tipos de dato str están en mayúsculas"

    df["tipo_contrato"] = df["tipo_contrato"].str.upper()
    df["objeto"] = df["objeto"].str.upper()
    df["adjudicatario"] = df["adjudicatario"].str.upper()
    df["negociado"] = df["negociado"].str.upper()

    return df


def clean_data(df):

    "Limpieza de datos"

    df = df.copy()

    df = clean_text(df)
    print("Espacios corregidos")
    df = clean_prices(df)
    print(f"Precios convertidos --> {df["precio"].dtype}")
    df = clean_dates(df)
    print(f"Fechas convertidas --> {df["fecha"].dtype}")
    df = clean_categories(df)
    print("Resto de columnas --> str mayusc.")
    print("---------------------------------------------")

    return df


def transform():

    "Aplica las transformaciones de las funciones anteriores"

    SILVER_PATH = get_silver_path()
    GOLD_PATH = get_gold_path()

    file_path = SILVER_PATH/"consolidated"/"contratos_menores_consolidados.csv"

    df = read_csv(file_path)
    
    df = clean_data(df)

    df = explore(df)

    output_dir = GOLD_PATH/"cleaned"/"contratos_menores_limpios.csv"
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    #export_csv(df, output_dir)

    return df


if __name__ == "__main__":

    df = transform()

    print(df.iloc[77])

   

