from pathlib import Path

def get_base_dir():
    """
    Obtiene el directorio raíz del proyecto.
    """
    return Path(__file__).resolve().parents[2]

def get_bronze_path():
    """
    Obtiene la ruta de la carpeta 'bronze' dentro del directorio de datos.
    """
    BASE_DIR = get_base_dir()
    return BASE_DIR / "data" / "bronze"

def get_silver_path():
    """
    Obtiene la ruta de la carpeta 'silver' dentro del directorio de datos.
    """
    BASE_DIR = get_base_dir()
    return BASE_DIR / "data" / "silver"

def get_gold_path():
    """
    Obtiene la ruta de la carpeta 'gold' dentro del directorio de datos.
    """
    BASE_DIR = get_base_dir()
    return BASE_DIR / "data" / "gold"


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




