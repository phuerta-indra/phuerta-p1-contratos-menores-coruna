import pandas as pd
from src.utils.config import get_silver_path
from src.utils.utils import export_csv


#--------------------------------------------
# Función para Unificar los CSV
#--------------------------------------------

def consolidate_files():

    SILVER_PATH = get_silver_path()

    # Definimos la ruta donde se van a guardar los archivos consolidados
    output_dir = SILVER_PATH / "consolidated" / "contratos_menores_consolidados.csv"
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    # Obtenemos los archivos csv procesados
    archivos = list(SILVER_PATH.rglob("*.csv"))

    # Evitar leer el csv consolidado (si existe)
    archivos = [archivo for archivo in archivos if archivo != output_dir]

    df_list = []

    for archivo in archivos:

        # Mostramos un mensaje del archivo que se está procesando
        print(f"Leyendo: {archivo.name}")

        df = pd.read_csv(archivo, encoding="utf-8-sig")

        df_list.append(df) #Añadimos todos los csv a una lista

    # Comprobamos que hay df para unir

    if not df_list:
        print("No se encontraron archivos CSV para consolidar.")
        return

    # Comprobar que los archivos tienen las mismas columnas

    cols = list(df_list[0].columns)

    for df in df_list:
        if list(df.columns) != cols:
            raise ValueError(f"Los archivos no tienen las mismas columnas.")

    # Concatenar los df en uno unico
    df_consolidated = pd.concat(df_list, ignore_index=True)

    # Exportar el df consolidado
    export_csv(df_consolidated, output_dir)

    # Mensajes de confirmación
    print(f"\nConsolidación completada.")
    print(f"Archivos unidos: {len(df_list)}")
    print(f"Registros totales: {len(df_consolidated)}")
    print(f"Archivo generado: {output_dir}")


if __name__ == "__main__":
    consolidate_files()