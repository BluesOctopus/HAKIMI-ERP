"""Compare all ORM models against the live DB schema and report missing columns."""

import pymysql
from sqlalchemy.dialects.mysql import (
    BIGINT, BINARY, BIT, CHAR, DATE, DATETIME, DECIMAL, DOUBLE, FLOAT,
    INTEGER, LONGTEXT, MEDIUMTEXT, SMALLINT, TEXT, TIME, TIMESTAMP,
    TINYINT, VARBINARY, VARCHAR, YEAR,
)

from app.models.base import Base
import app.models  # noqa: F401  ensure models are registered

conn = pymysql.connect(
    host='localhost', port=3306, user='hakimi_app', password='Zhang1214',
    database='hakimi_erp',
)
cur = conn.cursor()

missing = []
for table in Base.metadata.sorted_tables:
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema=%s AND table_name=%s",
        ('hakimi_erp', table.name),
    )
    db_cols = {r[0] for r in cur.fetchall()}
    if not db_cols:
        missing.append((table.name, '<entire table missing>', ''))
        continue
    for col in table.columns:
        if col.name not in db_cols:
            missing.append((table.name, col.name, str(col.type)))

conn.close()

if not missing:
    print("ORM and DB are fully aligned.")
else:
    print(f"{len(missing)} missing columns:")
    for t, c, typ in missing:
        print(f"  {t}.{c}  {typ}")
