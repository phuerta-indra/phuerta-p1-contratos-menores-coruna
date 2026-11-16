from src.utils.utils import connect
import ollama
import json
import re

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

    messages = [
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
            ),
        },
        {
            "role": "user",
            "content": (
                f"Esquema disponible:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                f"Pregunta: {question}"
            ),
        },
    ]

    response = ollama.chat(
        model='qwen2.5-coder:7b',
        messages=messages
    )

    return response['message']['content'].strip()



def validate_sql(sql):

    sql = sql.strip()

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
        rows = cur.fetchmany(500)

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
    conn = connect()
    if conn:
        try:
            schema = get_schema(conn)
            sql = generate_sql(question, schema)
            sql = validate_sql(sql)
            results = execute_sql(conn, sql)
            answer = explain_results(question, results)
    
        finally:
            conn.close()

    return answer


if __name__ == '__main__':
    chatbot()
    