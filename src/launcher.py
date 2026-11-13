from src.transform.processed import process_file
from src.transform.consolidate import consolidate_files
from src.transform.clean import transform_files
from src.load.load import load_data


def launcher():

    "Función para ejecutar todo el programa"

    # Ejecuta la función para procesar los archivos (Bronze->Silver)
    process_file()

    # Ejecuta la función para unificar los archivos en un único csv
    consolidate_files()

    # Ejecuta la función que se encarga de la limpieza y normalización de los datos
    df = transform_files()

    # Ejecuta la función para cargar los datos en una tabla de Snowflake
    load_data(df)

