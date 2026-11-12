import snowflake.connector
import os
from dotenv import load_dotenv
from src.utils.config import get_base_dir



connnectio_param = {
    'user' : os.environ['SNOWFLAKE_USER'],
    'password' : os.environ['SNOWFLAKE_PASSWORD'],
    'account' : os.environ['SNOWFLAKE_ACCOUNT'],
    'role' : os.environ['SNOWFLAKE_ROLE'],
    'warehouse' : os.environ['SNOWFLAKE_WAREHOUSE'],
    'database' : os.environ['SNOWFLAKE_DATABASE'],
    'schema' : os.environ['SNOWFLAKE_SCHEMA']
}

session = snowflake.connector.connect(**connnectio_param)
cur = session.cursor()
data = cur.execute('SELECT * FROM MODELING.DIM_TIPO_CONTRATO')
print(data.fetch_pandas_all().head())
cur.close()


def connect():
    BASE_DIR = get_base_dir()

    load_dotenv(BASE_DIR / '.env')

    connnection_param = {
    'user' : os.environ['SNOWFLAKE_USER'],
    'password' : os.environ['SNOWFLAKE_PASSWORD'],
    'account' : os.environ['SNOWFLAKE_ACCOUNT'],
    'role' : os.environ['SNOWFLAKE_ROLE'],
    'warehouse' : os.environ['SNOWFLAKE_WAREHOUSE'],
    'database' : os.environ['SNOWFLAKE_DATABASE'],
    'schema' : os.environ['SNOWFLAKE_SCHEMA']
    }

    try:
        session = snowflake.connector.connect(**connnectio_param)
        print('Se ha conectado a Snowflake')

    except snowflake.connector.errors.OperationalError as e:
        print(f"OperationalError: {e}")
