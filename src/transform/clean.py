import pandas as pd
from src.utils.config import get_silver_path
import re

def explore():
    file_path = get_silver_path()/"consolidated"/"contratos_menores_consolidados.csv"

    df = pd.read_csv(file_path, encoding="utf-8-sig")

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

    limpio = (
        df["precio"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("€", "", regex=False)
    )
    convertido = pd.to_numeric(limpio, errors="coerce")

    # Para identificar valores que pandas no ha podido convertir a número 
    # (dos valore: 18.000,00 € y dos anualidades: 22.209,07€ (2023). 31.882,29 € (2024))

    fallidos = df.loc[convertido.isna() & df["precio"].notna(), "precio"]
    print(f"Precios no convertibles: {len(fallidos)}")
    print(fallidos)

    df["precio"] = convertido

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
    print("Precios convertidos --> float64")
    df = clean_dates(df)
    print("Fechas convertidas --> datetime")
    df = clean_categories(df)
    print("Resto de columnas --> str mayusc.")

    return df




if __name__ == "__main__":


    df = clean_data(explore())


    print("--------------------------------------")
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