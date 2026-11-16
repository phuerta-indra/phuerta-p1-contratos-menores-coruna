import pandas as pd
from src.utils.config import get_bronze_path, get_base_dir
import snowflake.connector
from dotenv import load_dotenv
import os


def read_csv(path):
    return pd.read_csv(path, encoding="utf-8-sig")


def export_csv(df, output_dir):

    "Exporta un df a un archivo .csv"

    df.to_csv(output_dir, index=False, encoding="utf-8-sig")
    print("Archivo exportado con éxito.")
    return


def files_format():
    """
    Devuelve un diccionario con los formatos de archivos y sus funciones correspondientes.
    """

    BRONZE_PATH = get_bronze_path()

    format = {}
    
    archivos = list(BRONZE_PATH.rglob("*.ods"))

    for archivo in archivos:
        relative_path = archivo.relative_to(BRONZE_PATH)

        if ("Anexo" in archivo.name and "2023" in archivo.name):
            format[relative_path] = "set_headers_format_3"

        elif ("Primer" in archivo.name and "2023" in archivo.name) or ("Segundo" in archivo.name and "2023" in archivo.name):
            format[relative_path] = "set_headers_format_2"

        else:
            format[relative_path] = "set_headers_format_1"

    return format

def connect():

    BASE_DIR = get_base_dir() 

    load_dotenv(BASE_DIR / '.env')

    CONNEXION_PARAMS = {
        'user' : os.environ['SNOWFLAKE_USER'],
        'password' : os.environ['SNOWFLAKE_PASSWORD'],
        'account' : os.environ['SNOWFLAKE_ACCOUNT'],
        'role' : os.environ['SNOWFLAKE_ROLE'],
        'warehouse' : os.environ['SNOWFLAKE_WAREHOUSE'],
        'database' : os.environ['SNOWFLAKE_DATABASE'],
        'schema' : os.environ['SNOWFLAKE_SCHEMA']
    }

    
    try:
        conn = snowflake.connector.connect(**CONNEXION_PARAMS)
        print("Se ha conectado a Snowflake")
        return conn
    except snowflake.connector.errors.Error as e:
        print(f"No se pudo conectar a Snowflake: {e}")
        return None