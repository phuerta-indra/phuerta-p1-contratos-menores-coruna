import pandas as pd
import pytest 
from src.utils.config import get_gold_path
import pandas.api.types as ptypes



PATH = get_gold_path() / 'cleaned' / 'contratos_menores_limpios.csv'

VERIFICADORES = {
    "referencia": ptypes.is_string_dtype,
    "tipo_contrato": ptypes.is_string_dtype,
    "objeto": ptypes.is_string_dtype,
    "fecha": ptypes.is_datetime64_any_dtype,
    "nif": ptypes.is_string_dtype,
    "adjudicatario": ptypes.is_string_dtype,
    "precio": ptypes.is_numeric_dtype,
    "negociado": ptypes.is_string_dtype,
    "negociado_cod": ptypes.is_string_dtype,
    "clave_negociado": ptypes.is_string_dtype,
}



@pytest.fixture(scope='module')
def df():
    return pd.read_csv(PATH, 
            parse_dates=["fecha"],
            dtype={
            "referencia": str,
            "nif": str,
            "negociado_cod": str,
            "clave_negociado": str,
        },)

def test_nulls_in_important_cols(df):

    'Test para comprobar si existe algún valor nulo en columnas importantes para el análisis'

    cols = ["referencia", "fecha", "precio", "adjudicatario", "nif"]
    assert df[cols].isna().sum().sum() == 0

def test_possitive_price(df):

    'Test para comprobar si hay precios incorrectos'

    assert (df['precio'] > 0).all()

def test_correct_dates(df):

    'Test para comprobar si hay fechas fuera del periodo que se está analizando'

    assert df["fecha"].between("2023-01-01", "2026-03-31").all()

def test_contract_types(df):

    'Test para comprobar si solo existen los tipo de contrato definidos'

    assert set(df["tipo_contrato"].unique()) <= {"A", "C", "E", "Z"}

def test_duplicated(df):

    'Test para comprobar si hay filas idénticas repetidas'

    assert not df.duplicated().any()

def test_data_type(df):

    'Test para comprobar si los tipos de datos de cada columna es el correcto'

    assert ptypes.is_numeric_dtype(df["precio"]), "precio no es numérico"
    assert ptypes.is_datetime64_any_dtype(df["fecha"]), "fecha no es datetime"

    remain = [c for c in df.columns if c not in ("precio", "fecha")]
    no_text = [c for c in remain if not ptypes.is_string_dtype(df[c].dropna())]
    assert not no_text, f"Columnas que no son texto: {no_text}"
    