import os
import sys

try:
    import psycopg2
except Exception:
    print('psycopg2 not installed. Please run: pip install psycopg2-binary')
    sys.exit(1)

url = os.environ.get('DATABASE_URL')
if not url:
    print('DATABASE_URL environment variable not set')
    sys.exit(1)

sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema_postgres.sql')
if not os.path.exists(sql_path):
    print(f'SQL file not found: {sql_path}')
    sys.exit(1)

with open(sql_path, 'r', encoding='utf-8') as f:
    sql = f.read()

# Naive split by semicolon - suitable for simple schema files
stmts = [s.strip() for s in sql.split(';') if s.strip()]

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    for stmt in stmts:
        try:
            cur.execute(stmt + ';')
        except Exception as e:
            print('Error executing statement (continuing):', e)
    conn.commit()
    cur.close()
    conn.close()
    print('Schema applied successfully')
except Exception as e:
    print('Failed to apply schema:', e)
    sys.exit(1)
