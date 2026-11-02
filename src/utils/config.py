from pathlib import Path

def get_base_dir():
    """
    Obtiene el directorio raíz del proyecto.
    """
    return Path(__file__).resolve().parents[2]

def get_raw_path():
    """
    Obtiene la ruta de la carpeta 'raw' dentro del directorio de datos.
    """
    BASE_DIR = get_base_dir()
    return BASE_DIR / "data" / "raw"

def get_processed_path():
    """
    Obtiene la ruta de la carpeta 'processed' dentro del directorio de datos.
    """
    BASE_DIR = get_base_dir()
    return BASE_DIR / "data" / "processed"

def files_format():
    """
    Devuelve un diccionario con los formatos de archivos y sus funciones correspondientes.
    """

    RAW_PATH = get_raw_path()

    format = {}
    
    archivos = list(RAW_PATH.rglob("*.ods"))

    for archivo in archivos:
        relative_path = archivo.relative_to(RAW_PATH)

        if ("Anexo" in archivo.name and "2023" in archivo.name):
            format[relative_path] = "set_headers_format_3"

        elif ("Primer" in archivo.name and "2023" in archivo.name) or ("Segundo" in archivo.name and "2023" in archivo.name):
            format[relative_path] = "set_headers_format_2"

        else:
            format[relative_path] = "set_headers_format_1"

    return format




