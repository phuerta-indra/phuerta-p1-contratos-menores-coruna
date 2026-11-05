import pandas as pd
from src.utils.config import get_silver_path, get_gold_path
from src.utils.utils import read_csv, export_csv
import re



#-------------------------------------------------------------
# Función para explorar datos (antes o después de la limpieza)
#-------------------------------------------------------------



def explore(df):

    print("---------------------------------------------")

    print("\n--- PRIMERAS FILAS ---")
    pd.set_option("display.max_columns", None)
    print(df.head())

    print("\n--- DIMENSIONES ---")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")

    print("\n--- TIPOS DE DATOS ---")
    print(df.dtypes)

    print("\n--- VALORES NULOS ---")
    print(df.isnull().sum())

    print("\n--- PORCENTAJE DE NULOS ---")
    print((df.isnull().mean() * 100).round(2))

    print("\n--- REGISTROS DUPLICADOS ---")
    print(df.duplicated().sum())

    print("\n--- VALORES ÚNICOS ---")
    for column in df.columns:
        print(f"{column}: {df[column].nunique()} valores únicos")

    print("\n--- DISTRIBUCIONES ---")
    print(df.describe())

    print("---------------------------------------------")

    return df



#-------------------------------------------------------------
# Funciones para limpiar datos 
#-------------------------------------------------------------



def clean_text(df):

    # Limpiar espacios en blanco al inicio y al final de las cadenas de texto

    text_columns = df.columns

    for col in text_columns:
        df[col] = df[col].str.strip()

    # Para examinar columna por columna si hay algún nulo oculto
    """for col in text_columns:
        print(f"\n--- {col} ---")
        print(df[col].str.len().describe()[["min", "max"]])
        print(df[col].value_counts().head(5))"""

    return df



def clean_categories(df):

    "Convertir todos los tipos de dato str están en mayúsculas"

    df["tipo_contrato"] = df["tipo_contrato"].str.upper()
    df["objeto"] = df["objeto"].str.upper()
    df["adjudicatario"] = df["adjudicatario"].str.upper()
    df["negociado"] = df["negociado"].str.upper()

    return df



def clean_prices(df):

    "Convertir los precios a dato numérico"

    # Celda con dos anualidades: la sustituimos por la suma (22.209,07 + 31.882,29)
    df["precio"] = df["precio"].replace({
        "22.209,07€ (2023). 31.882,29 € (2024)": "54.091,36"
    })

    cleaned = (
        df["precio"]
        .str.replace("€", "", regex=False)
    )

    # Para cambiar los precios con formato 1.234,56
    eu_format = cleaned.str.contains(",", na=False)

    cleaned.loc[eu_format] = (
        cleaned.loc[eu_format]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    converted = pd.to_numeric(cleaned, errors="coerce")

    # Para identificar valores que pandas no ha podido convertir a número 
    # (valores tipo: 18.000,00 € y dos anualidades: 22.209,07€ (2023). 31.882,29 € (2024))

    fallidos = df.loc[converted.isna() & df["precio"].notna(), "precio"]
    print(f"Precios no convertibles: {len(fallidos)}")
    print(fallidos)

    df["precio"] = converted

    return df



def clean_dates(df):

    "Convertir las fechas a forma datetime"

    # Quitamos las horas de las fechas
    date = df["fecha"].str[:10]

    # Formato principal de las fechas en los datos obtenidos

    date_iso = pd.to_datetime(date, format="%Y-%m-%d", errors="coerce")

    # Formato secundario de las fechas en los datos obtenidos
    date_es = pd.to_datetime(date, format="%d/%m/%Y", errors="coerce")

    # Si una falla nos quedamos con la otra
    convertido = date_iso.fillna(date_es)

    # Hay una fecha con un año erroneo (2022 en vez de 2023), como las 
    # referencias más proximas son del 2023 voy a corregir el año de la fecha
    # en lugar de eliminar la fila. La referencia era: 237/2023/31

    # Para ver las referencias proximas se puede ejecutar:
    """fila = df[df["fecha"] < "2023-01-01"]
    print(fila[["referencia", "fecha"]])
    
    prefijo = fila["referencia"].iloc[0].split("/")[0]
    vecinos = df[df["referencia"].str.startswith(prefijo + "/2023/")].sort_values("referencia")
    print(vecinos[["referencia", "fecha"]])"""

    ref = "237/2023/31" 
    mask = df["referencia"] == ref
    convertido.loc[mask] = convertido.loc[mask] + pd.DateOffset(years=1)


    # Filas donde había un valor original pero ningún formato funcionó
    fallidos = df.loc[convertido.isna() & df["fecha"].notna(), "fecha"]
    print(f"Fechas no convertibles: {len(fallidos)}")
    print(fallidos)

    df["fecha"] = convertido

    return df



def clean_duplicates(df):

    "Función para gestionar valores duplicados"

    # Para ver los duplicados
    """dup = df[df["referencia"].duplicated(keep=False)].sort_values("referencia")
    print(len(dup))
    print(dup[["referencia", "fecha", "adjudicatario", "precio", "objeto", "negociado"]])"""

    """
    Se obtienen 3 casos de duplicados (total 12 parejas):
        1) Misma referencia con texto distinto en objeto o adjudicatario --> duplicados
        2) Misma referencia e importe en diferente fecha --> duda
        3) Misma referencia con importes y fechas distintos --> no duplicado
    En este caso solo se van a eliminar los duplicados del tipo 1
    """

    duplicate = df[df.duplicated(subset=["referencia", "fecha", "precio"], keep="first")]
    print(f"Duplicados eliminados: {len(duplicate)}")
    print(duplicate[["referencia", "fecha", "precio"]])

    # Eliminamos los duplicados del tipo 1 quedandonos con el primer registro
    df = df.drop_duplicates(subset=["referencia", "fecha", "precio"], keep="first")

    return df.sort_index()



def clean_nif(df):

    "Corregir NIF mal escritos, comprobados contra el mismo adjudicatario"
    # Para ver los NIF que están mal o que tienen otro formato al español:
    """
    print(df["nif"].str.len().value_counts())
    print(df.loc[df["nif"].str.len() != 9, ["nif", "adjudicatario"]])
    print(df.loc[df["adjudicatario"].str.len() <= 6, "adjudicatario"].unique())
    
    print(df[df["adjudicatario"].str.contains("TRANVÍAS|PORTALES DE GALICIA|ORONA|RALLYE|SENSO", na=False)]
      .groupby(["adjudicatario", "nif"]).size())
    """
    # Hay empresas extranjeras por lo que hay NIF que tiene formato internacional

    # Modificamos solo los que estamos seguros de que están mal escritos
    nif_dic = {
        "A1500227": "A15000227",    # Compañía de tranvias coruña
        "F200253318": "F20025318",  # Orona S.COOP.
        "ESB70250055": "B70250055", #Senso ingeniería e instalaciones
    }

    df["nif"] = df["nif"].replace(nif_dic)

    return df



def clean_adjudicatario(df):

    "Unificar los nombres de los adjudicatarios según el NIF"

    # Ignorar los NIF enmascarados ya que pueden no identificar a una única persona
    masked = df["nif"].str.contains("*", regex=False)

    # Nombre más frecuente de cada NIF
    nombre_comun = df.groupby("nif")["adjudicatario"].transform(lambda x: x.mode().iloc[0])

    # Cambiamos los nombre en el df
    df.loc[~masked, "adjudicatario"] = nombre_comun[~masked]

    return df



def clean_negociado(df):

    """
    Separa el nombre del negociado y los unifica por código 
    (los nombres de los negociados acaban con un codigo, si es que tienen)
    """

    # Vamos a codificar los nombres de la forma AA9999 con una letra mayuscula opcional
    code = r"([A-Z]{2}\d{4}[A-Z]?)$"

    # Limpiamos espacios
    text = df["negociado"].str.replace(r"\s+", " ", regex=True).str.strip()

    # Codificamos los negociados
    df["negociado_cod"] = text.str.extract(code)[0]
    name = text.str.replace(code, "", regex=True).str.strip() # Nombre del negociado sin espacios y sin codigo

    # Nombre más frecuente de cada código los que no tienen codigo quedan NaN
    common = name.groupby(df["negociado_cod"]).transform(lambda x: x.mode().iloc[0])
    df["negociado"] = common.fillna(name) # Rellenamos los NaN con su nombre, ya que no hay codigo

    # Unificación de los nogociados sin codigo, solo hay dos que se repiten con nombres diferentes
    no_code = {
        "ALCALDIA" : "ALCALDÍA",
        "XESTIÓN ECONÓMICA URBANISMO" : "GESTION ECONOMICA URBANISMO"
    }

    df["negociado"] = df["negociado"].replace(no_code)

    # Creamos una nueva columna clave_negociado para poder identificar a los 
    # negociados según su codigo o nombre, si no tienen

    df["clave_negociado"] = df["negociado_cod"].fillna(df["negociado"])

    # Comprobaciones
    print(f"Negociados sin código: {df['negociado_cod'].isna().sum()}")
    print(f"Claves distintas: {df['clave_negociado'].nunique()}")
    assert df.groupby("clave_negociado")["negociado"].nunique().max() == 1, "Una clave tiene más de un nombre"

    return df



def clean_data(df):

    "Función principal para aplicar todas las limpiezas individuales"

    df = df.copy()

    df = clean_text(df)
    print("Espacios corregidos")

    df = clean_nif(df)
    print("NIF corregidos")

    df = clean_prices(df)
    print(f"Precios convertidos --> {df["precio"].dtype}")

    df = clean_dates(df)
    print(f"Fechas convertidas --> {df["fecha"].dtype}")

    df = clean_categories(df)
    print("Resto de columnas --> str mayusc.")

    df = clean_adjudicatario(df)
    print("Nombres de los adjudicatarios actualizados")

    df = clean_negociado(df)
    print("Negociados actualizados")

    print("---------------------------------------------")

    df = clean_duplicates(df)

    return df



#---------------------------------------------------------------------
# Función para ejecutar la limpieza y exportación de los datos limpios
#---------------------------------------------------------------------



def transform_files():

    "Aplica las transformaciones de las funciones anteriores"

    SILVER_PATH = get_silver_path()
    GOLD_PATH = get_gold_path()

    file_path = SILVER_PATH/"consolidated"/"contratos_menores_consolidados.csv"

    df = read_csv(file_path)

    print ("ANTES DE LIMPIEZA DE DATOS")

    df = explore(df)
    
    df = clean_data(df)

    df = explore(df)

    output_dir = GOLD_PATH/"cleaned"/"contratos_menores_limpios.csv"
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    export_csv(df, output_dir)

    return df



if __name__ == "__main__":

    transform_files()
    

    

   

