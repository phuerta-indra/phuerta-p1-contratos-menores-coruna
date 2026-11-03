import pandas as pd
from src.utils.config import get_bronze_path, get_silver_path
from src.utils.utils import files_format, export_csv


#--------------------------------------------
# Funciones de Estandarización de Formato
#--------------------------------------------

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


#--------------------------------------------
# Diccionario de Transformaciones de Formato
#--------------------------------------------

TRANSFORMATIONS = {
    "set_headers_format_1": set_headers_format_1,
    "set_headers_format_2": set_headers_format_2,
    "set_headers_format_3": set_headers_format_3,
}


#--------------------------------------------
# Función para Procesar Archivos
#--------------------------------------------


def process_file():

    BRONZE_PATH = get_bronze_path()
    SILVER_PATH = get_silver_path()

    # Obtenemos el diccionario de formatos de archivos
    formats = files_format()

    # Listamos todos los archivos con los datos originales
    archivos = list(BRONZE_PATH.rglob("*.ods"))

    for archivo in archivos:

        # Obtenemos el formato correspodiente del archivo a partir de su clave en el diccionario
        relative_path = archivo.relative_to(BRONZE_PATH) #'Año/Nombre archivo.ods'
        format_name = formats.get(relative_path) # 'set_headers_format_x'

        if format_name is None:
            print(f"Formato no definido para: {archivo.name}")
            continue

        # Obtenemos la transformación conrrespondiente
        transform_function = TRANSFORMATIONS.get(format_name) 

        # Leer el archivo .ods
        df = pd.read_excel(archivo, engine="odf")

        # Lista con los nombres de las columnas estandarizadas
        COLUMN_NAMES = [
            "referencia",
            "tipo_contrato",
            "objeto",
            "fecha",
            "nif",
            "adjudicatario",
            "precio",
            "negociado"
        ]

        # Aplicamos la transformación
        df = transform_function(df)

        df.columns = COLUMN_NAMES  # Estandarizamos los nombres de las columnas

        # Crear ruta de salida conservando la estructura de carpetas
        output_dir = (SILVER_PATH / relative_path).with_suffix('.csv')
        output_dir.parent.mkdir(parents=True, exist_ok=True) #Crea carpetas hasta el archivo

        # Exportar el CSV
        export_csv(df, output_dir)

        # Mensaje de procesamiento
        print(f"Procesado: {archivo.name} -> {output_dir}")


# --------------------------------------------
# Ejecución
#--------------------------------------------

if __name__ == "__main__":
    process_file()

    



