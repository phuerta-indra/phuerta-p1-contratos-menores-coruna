import pandas as pd


def read_csv(path):
    return pd.read_csv(path, encoding="utf-8-sig")


def export_csv(df, output_dir):

    "Exporta un df a un archivo .csv"

    df.to_csv(output_dir, index=False, encoding="utf-8-sig")
    print("Archivo exportado con éxito.")
    return