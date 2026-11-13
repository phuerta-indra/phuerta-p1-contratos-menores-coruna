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

    schema = f'"{db}"."{SCHEMA}"'

    table_columns = ", ".join(
        f'"{col}" {type}' for col, type in types.items()
    )

    query = f'CREATE TABLE IF NOT EXISTS {table} ({table_columns})'

    cur = conn.cursor()

    try:
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS {schema};')
        cur.execute(f'TRUNCATE TABLE IF EXISTS {table}')
    finally:
        pass

    cur.execute(query)

    print('Tabla creada correctamente')

    cur.close()

    return



def load_data(df):

    conn = connect()

    types = data_types(df)

    create_table(conn, types, TABLE)

    return




if __name__ == '__main__':

    df = pd.read_csv(GOLD_DIR / 'cleaned' / 'contratos_menores_limpios.csv')
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    conn = connect()

    types = data_types(df)

    create_table(conn, types, TABLE)