import pandas as pd
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]

# Directorio de los datos en bruto, y el directorio de los datos procesados
RAW_PATH = BASE_DIR / "data" / "raw"

PROCESSED_PATH = BASE_DIR / "data" / "processed"


def set_headers():

    archivos = list(RAW_PATH.rglob("*.ods"))

    for archivo in archivos:
        df = pd.read_excel(archivo, engine="odf")

        # Para mostrar todas las columnas del DataFrame
        pd.set_option("display.max_columns", None)

        # Para este formato hay que dropear la primera y tercera fila, y hacer header la segunda
        df.columns = df.iloc[0] # Hacemos la segunda fila del .ods como header
        df = df.drop([0, 1]).reset_index(drop=True) # Eliminamos las filas extras del encabezado del .ods

        # Crear carpeta de destino conservando el año
        output_dir = PROCESSED_PATH / archivo.parent.name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Crear nombre del archivo CSV
        output_file = output_dir / archivo.name

        # Exportar CSV
        df.to_csv(output_file.with_suffix(".csv"), index=False, encoding="utf-8-sig")

        print(f"Procesado: {archivo.name} -> {output_file}")

set_headers()