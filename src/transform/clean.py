import pandas as pd
from src.utils.config import get_silver_path

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

    return df

if __name__ == "__main__":
    explore()