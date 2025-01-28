import psycopg2
from dotenv import load_dotenv
import os

# Carica le configurazioni dal file .env
load_dotenv()

# Configurazione del database
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")

# Funzione per normalizzare i tipi di dati
def normalize_data_type(data_type, character_maximum_length, numeric_precision, numeric_scale):
    if data_type == "character varying":
        return f"VARCHAR({character_maximum_length})" if character_maximum_length else "TEXT"
    elif data_type == "timestamp without time zone":
        return "TIMESTAMP"
    elif data_type == "timestamp with time zone":
        return "TIMESTAMPTZ"
    elif data_type == "numeric":
        return f"NUMERIC({numeric_precision},{numeric_scale})" if numeric_precision else "NUMERIC"
    else:
        return data_type.upper()

# Connessione al database
conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# Inizia il file di dump
with open("data_dump.sql", "w") as dump_file:
    # Crea lo schema
    dump_file.write(f"-- Creazione dello schema {SCHEMA_NAME}\n")
    dump_file.write(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};\n\n")

    # Ottieni tutte le tabelle dello schema
    cursor.execute(f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA_NAME}' AND table_type = 'BASE TABLE';
    """)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Dumping table: {table_name}")

        # Genera la definizione della tabella
        cursor.execute(f"""
            SELECT column_name, data_type, character_maximum_length,
                   numeric_precision, numeric_scale
            FROM information_schema.columns
            WHERE table_schema = '{SCHEMA_NAME}' AND table_name = '{table_name}';
        """)
        columns = cursor.fetchall()

        create_table_sql = f"CREATE TABLE {SCHEMA_NAME}.{table_name} (\n"
        column_definitions = []
        for column in columns:
            column_name, data_type, char_max_length, num_precision, num_scale = column
            normalized_type = normalize_data_type(data_type, char_max_length, num_precision, num_scale)
            column_definitions.append(f"    {column_name} {normalized_type}")
        create_table_sql += ",\n".join(column_definitions)
        create_table_sql += "\n);\n"

        dump_file.write(f"-- Schema for table {SCHEMA_NAME}.{table_name}\n")
        dump_file.write(create_table_sql + "\n\n")

        # Estrai le prime 10 righe e genera le `INSERT INTO`
        cursor.execute(f"SELECT * FROM {SCHEMA_NAME}.{table_name} LIMIT 10")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        if rows:
            dump_file.write(f"-- Data for table {SCHEMA_NAME}.{table_name}\n")
            for row in rows:
                values = []
                for value in row:
                    if value is None:
                        values.append("NULL")
                    elif isinstance(value, str):
                        values.append(f"'{value.replace('\'', '\'\'')}'")  # Escape singole virgolette
                    else:
                        values.append(str(value))
                values_list = ", ".join(values)
                insert_sql = f"INSERT INTO {SCHEMA_NAME}.{table_name} ({', '.join(column_names)}) VALUES ({values_list});\n"
                dump_file.write(insert_sql)
            dump_file.write("\n")

# Chiudi la connessione
cursor.close()
conn.close()

print("Data dump completato!")
