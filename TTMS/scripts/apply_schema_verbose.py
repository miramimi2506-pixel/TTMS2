import os
import sys
import traceback

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

# Split statements by semicolon while preserving dollar-quoted blocks
def split_sql_statements(sql_text):
    stmts = []
    cur = []
    in_dollar = False
    dollar_tag = None
    i = 0
    while i < len(sql_text):
        ch = sql_text[i]
        if ch == '$':
            # potential start of dollar-quote
            j = i+1
            while j < len(sql_text) and sql_text[j].isalnum():
                j += 1
            if j > i+1 and j < len(sql_text) and sql_text[j] == '$':
                tag = sql_text[i:j+1]
                if not in_dollar:
                    in_dollar = True
                    dollar_tag = tag
                    cur.append(tag)
                    i = j
                    i += 1
                    continue
                else:
                    if tag == dollar_tag:
                        in_dollar = False
                        dollar_tag = None
                        cur.append(tag)
                        i = j
                        i += 1
                        continue
        if ch == ';' and not in_dollar:
            cur.append(ch)
            stmts.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    trailing = ''.join(cur).strip()
    if trailing:
        stmts.append(trailing)
    # remove final semicolons from statements
    return [s if not s.endswith(';') else s[:-1].strip() for s in stmts if s.strip()]

stmts = split_sql_statements(sql)

print('Connecting to database...')
try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    print('Connected. Executing', len(stmts), 'statements...')
    for idx, stmt in enumerate(stmts, start=1):
        short = stmt.strip().splitlines()[0][:120]
        print(f'[{idx}/{len(stmts)}] Executing: {short}...')
        try:
            cur.execute(stmt)
            print('  -> OK')
        except Exception as e:
            print('  -> ERROR:', e)
            traceback.print_exc()
    conn.commit()
    cur.close()
    conn.close()
    print('Schema applied successfully')
except Exception as e:
    print('Failed to apply schema:')
    traceback.print_exc()
    sys.exit(1)
