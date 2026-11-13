import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
import pandas as pd
from dotenv import load_dotenv
from src.utils.config import get_base_dir, get_gold_path
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
)


BASE_DIR = get_base_dir()
GOLD_DIR = get_gold_path()


SCHEMA = 'STAR'
TABLE = 'CONTRATOS_MENORES_AUTO'




def connect():    

    load_dotenv(BASE_DIR / '.env')

    CONNEXION_PARAMS = {
        'user' : os.environ['SNOWFLAKE_USER'],
        'password' : os.environ['SNOWFLAKE_PASSWORD'],
        'account' : os.environ['SNOWFLAKE_ACCOUNT'],
        'role' : os.environ['SNOWFLAKE_ROLE'],
        'warehouse' : os.environ['SNOWFLAKE_WAREHOUSE'],
        'database' : os.environ['SNOWFLAKE_DATABASE'],
        #'schema' : os.environ['SNOWFLAKE_SCHEMA']
    }

    
    try:
        conn = snowflake.connector.connect(**CONNEXION_PARAMS)
        print('Se ha conectado a Snowflake')

    except snowflake.connector.errors.OperationalError as e:
        print(f"OperationalError: {e}")

    return conn



def data_types(df):
    data = {}

    for column, dtype in df.dtypes.items():
        if is_bool_dtype(dtype):
            type = "BOOLEAN"
        elif is_integer_dtype(dtype):
            type = "NUMBER"
        elif is_float_dtype(dtype):
            type = "FLOAT"
        elif is_datetime64_any_dtype(dtype):
            type = "TIMESTAMP_NTZ"
        else:
            type = "VARCHAR"

        data[column] = type

    return data



def create_table(conn, types, table):

    db = os.environ['SNOWFLAKE_DATABASE']

    qualified_schema = f'"{db}"."{SCHEMA}"'
    qualified_table = f'{qualified_schema}."{table}"'

    table_columns = ", ".join(
        f'"{col}" {snowflake_type}'
        for col, snowflake_type in types.items()
    )

    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {qualified_schema}")

        # Crea la tabla si todavía no existe.
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {qualified_table} ({table_columns})"
        )

        # Si quieres vaciarla en cada ejecución, conserva esta línea.
        cur.execute(f"TRUNCATE TABLE IF EXISTS {qualified_table}")

    print("Tabla creada correctamente")

    cur.close()

    return



def copy_data(conn):

    db = os.environ['SNOWFLAKE_DATABASE']

    csv_path = (GOLD_DIR / 'cleaned' / 'contratos_menores_limpios.csv').resolve()
    stage = f'"{db}"."{SCHEMA}"."CSV_STAGE"'
    target = f'"{db}"."{SCHEMA}"."{TABLE}"'

    with conn.cursor() as cur:
        cur.execute(f"CREATE STAGE IF NOT EXISTS {stage}")

        print('Stage creado')

        cur.execute(
            f"PUT 'file://{csv_path.as_posix()}' @{stage} "
            "AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
        )

        print('Fichero .csv subido correctamente')

        cur.execute(f"""
            COPY INTO {target}
            FROM {stage}
        """)

        print(f'Datos copiados en la tabla: {target}')

        print(cur.fetchall())



def load_data(df):

    conn = connect()

    types = data_types(df)

    create_table(conn, types, TABLE)

    # Error por inspección SSL o configuración del proxy (mismo error que al usar write_pandas)
    copy_data(conn)

    return




if __name__ == '__main__':

    df = pd.read_csv(GOLD_DIR / 'cleaned' / 'contratos_menores_limpios.csv')
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    load_data(df)

