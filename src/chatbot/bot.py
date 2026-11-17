from src.utils.utils import connect
import ollama
import json
import re
from pathlib import Path
from src.utils.config import get_base_dir


BASE_DIR = get_base_dir()


def get_schema(conn):
    schema = {}

    with conn.cursor() as cur:
        cur.execute("SHOW TABLES IN SCHEMA CONTRATOS_MENORES_DB.MODELING")
        tables = [row[1] for row in cur.fetchall()]

        for table in tables:
            safe_table = table.replace('"', '""')
            cur.execute(
                f'DESCRIBE TABLE CONTRATOS_MENORES_DB.MODELING."{safe_table}"'
            )
            schema[table] = [
                {"name": row[0], "type": row[1]}
                for row in cur.fetchall()
            ]

    return schema



def generate_sql(question, schema):

    context = (BASE_DIR / 'src' / 'chatbot' / 'context.md').read_text(encoding='utf-8')

    system_prompt = f"""
        Convierte preguntas en SQL de Snowflake.
        Usa solo las tablas y columnas disponibles.
        Devuelve únicamente una consulta SELECT.

        Contexto del proyecto:
        {context}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Esquema: {json.dumps(schema, ensure_ascii=False)}\nPregunta: {question}",
        },
    ]

    """messages = [
        {
            "role": "system",
            "content": (
                "Convierte la pregunta del usuario en una consulta SQL para Snowflake. "
                "Usa solo las tablas y columnas del esquema proporcionado. "
                "Devuelve únicamente una sentencia SELECT, sin Markdown ni explicaciones. "
                "No inventes nombres de tablas o columnas."
                "Reglas de negocio: en DIM_TIPO_CONTRATO, UMBRAL está expresado sin IVA; "
                "en FACT_CONTRATOS, PRECIO incluye IVA. No compares ambos importes "
                "como si estuvieran en la misma base imponible."
                "Relaciones entre tablas:"
                "- FACT_CONTRATOS.FK_FECHA = DIM_FECHAS.PK_FECHA"
                "- FACT_CONTRATOS.FK_TIPO_CONTRATO = DIM_TIPO_CONTRATO.PK_TIPO_CONTRATO"
                "- FACT_CONTRATOS.FK_ADJUDICATARIO = DIM_ADJUDICATARIO.PK_ADJUDICATARIO"
                "- FACT_CONTRATOS.FK_NEGOCIADO = DIM_NEGOCIADO.PK_NEGOCIADO"

                "Para preguntas que necesiten varias tablas, usa esas relaciones en los JOIN."
                "PRECIO incluye IVA y UMBRAL no incluye IVA; no los compares como si fueran equivalentes."
                "Devuelve solo SQL válido para Snowflake."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Esquema disponible:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                f"Pregunta: {question}"
            ),
        },
    ]"""

    client = ollama.Client(timeout=120)

    response = client.chat(
        model='qwen2.5-coder:7b',
        messages=messages,
        keep_alive='10m'
    )

    return response['message']['content'].strip()



def validate_sql(sql):

    sql = sql.strip()

    # Quita bloques Markdown si el modelo los añade
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.IGNORECASE).strip()

    if sql.endswith(";"): # Elimina el punt y coma para que solo se haga una consulta
        sql = sql[:-1].strip()

    if ";" in sql: # Si quedan ; todavía rechaza la consulta
        raise ValueError("Solo se permite una consulta.")

    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE): # Si no es una consulta SELECT genera un error
        raise ValueError("Solo se permiten consultas SELECT.")

    return sql


def execute_sql(conn, sql):
    sql = validate_sql(sql)

    with conn.cursor() as cur:
        cur.execute(sql)
        columns = [description[0] for description in cur.description]
        rows = cur.fetchmany(20)

    return [dict(zip(columns, row)) for row in rows]



def explain_results(question, results):
    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Explica los resultados de una consulta en español claro. "
                    "Básate únicamente en los datos recibidos. "
                    "Si no hay resultados, dilo. No inventes cifras ni conclusiones."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Pregunta: {question}\n"
                    f"Resultados: {json.dumps(results, ensure_ascii=False, default=str)}"
                ),
            },
        ],
    )

    return response["message"]["content"].strip()


def chatbot(question, history):

    conn = None
    
    try:  
        conn = connect()          
        schema = get_schema(conn)
        sql = generate_sql(question, schema)
        sql = validate_sql(sql)
        print('Query generada: \n', sql)
        results = execute_sql(conn, sql)
        answer = explain_results(question, results)

        return answer

    except Exception as e:
        print('Error procesando la pregunta:', e)
        return f'No he podido responder a esa pregunta: {e}'

    finally:
        conn.close()

        




if __name__ == '__main__':
    chatbot()
    