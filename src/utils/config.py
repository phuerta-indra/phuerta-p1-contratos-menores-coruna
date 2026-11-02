from pathlib import Path

def get_base_dir():
    """
    Obtiene el directorio raíz del proyecto.
    """
    return Path(__file__).resolve().parents[2]


def files_format():
    """
    Devuelve un diccionario con los formatos de archivos y sus funciones correspondientes.
    """
    BASE_DIR = get_base_dir()
    RAW_PATH = BASE_DIR / "data" / "raw"

    FILES_FORMAT = {}
    
    archivos = list(RAW_PATH.rglob("*.ods"))

    for archivo in archivos:
        FILES_FORMAT[archivo.name] = None

    for archivo, formato in FILES_FORMAT.items():

        if ("Anexo" in archivo and "2023" in archivo):
            FILES_FORMAT[archivo] = "set_headers_format_3"

        elif ("Primer" in archivo and "2023" in archivo) or ("Segundo" in archivo and "2023" in archivo):
            FILES_FORMAT[archivo] = "set_headers_format_2"

        else:
            FILES_FORMAT[archivo] = "set_headers_format_1"

    return FILES_FORMAT





