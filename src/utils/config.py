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







