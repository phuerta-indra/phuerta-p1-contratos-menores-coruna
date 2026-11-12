import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

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