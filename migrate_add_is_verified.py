"""
Migration script to add is_verified column to doctors.
Works for SQLite and PostgreSQL.
"""
from sqlalchemy import inspect, text
from app import app, db


def column_exists(engine, table, column):
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table)]
    return column in columns


def add_column_sqlite(conn, table, column, ddl):
    if column_exists(conn.engine, table, column):
        print(f"Column '{column}' already exists in {table}. Skipping.")
        return
    conn.execute(text(ddl))
    print(f"Added '{column}' to {table}.")


def add_column_postgres(conn, ddl):
    conn.execute(text(ddl))


def migrate():
    with app.app_context():
        engine = db.engine
        dialect = engine.dialect.name

        with engine.begin() as conn:
            if dialect == 'sqlite':
                add_column_sqlite(
                    conn,
                    'doctors',
                    'is_verified',
                    "ALTER TABLE doctors ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 0"
                )
            elif dialect == 'postgresql':
                add_column_postgres(
                    conn,
                    "ALTER TABLE doctors ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE"
                )
                print("Migration completed successfully on PostgreSQL.")
            else:
                raise RuntimeError(f"Unsupported database dialect: {dialect}")


if __name__ == '__main__':
    migrate()
