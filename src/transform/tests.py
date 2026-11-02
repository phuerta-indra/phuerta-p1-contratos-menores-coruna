import pandas as pd
from src.utils.config import get_base_dir


def set_headers_format_1(df):

    "Cambio de formato para archivos estandarizados"

    df.columns = df.iloc[0]  # Hacemos la segunda fila del .ods como header
    df = df.iloc[2:].reset_index(drop=True)  # Eliminamos las filas extras del encabezado del .ods
    return df

def set_headers_format_2(df):

    "Cambio de formato para Primer y Segundo Trimestre 2023"

    df.columns = df.iloc[3]  # Hacemos la quinta fila del .ods como header
    df = df.iloc[5:].reset_index(drop=True)  # Eliminamos las filas extras del encabezado del .ods
    return df

def set_headers_format_3(df):

    "Cambio de formato para Anexo 2023"

    df.columns = df.iloc[1]  # Hacemos la segunda fila del .ods como header
    df = df.iloc[3:].reset_index(drop=True)  # Eliminamos las filas extras del encabezado del .ods
    return df

def get_files():

    "Devuelve una lista con todos los archivos de la carpeta de datos originales"
    
    BASE_DIR = get_base_dir()
    RAW_PATH = BASE_DIR / "data" / "raw"

    archivos = list(RAW_PATH.rglob("*.ods"))

    return archivos

def process_file():

    BASE_DIR = get_base_dir()
    RAW_PATH = BASE_DIR / "data" / "raw"
    PROCESSED_PATH = BASE_DIR / "data" / "processed"

    file_dir = RAW_PATH / "2023" / "202300_Anexo_Contratos_Menores_2023.ods" # Cambia esto por la carpeta que contiene tus archivos .ods

    df = pd.read_excel(file_dir, engine="odf")  # Cambia esto por la ruta de tu archivo .ods

    df = set_headers_format_3(df)  # Cambia esto por la función de formato que necesites

    output_dir = PROCESSED_PATH / "2023"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear nombre del archivo CSV
    output_file = output_dir / "202300_Anexo_Contratos_Menores_2023.csv"
    
    # Exportar CSV
    df.to_csv(output_file.with_suffix(".csv"), index=False, encoding="utf-8-sig")
    
    print(f"Procesado: 202300_Anexo_Contratos_Menores_2023.ods -> {output_file}")

