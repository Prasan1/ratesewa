"""
Migration script to add is_active columns to doctors and users.
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
                    'is_active',
                    "ALTER TABLE doctors ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"
                )
                add_column_sqlite(
                    conn,
                    'users',
                    'is_active',
                    "ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"
                )
            elif dialect == 'postgresql':
                add_column_postgres(
                    conn,
                    "ALTER TABLE doctors ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE"
                )
                add_column_postgres(
                    conn,
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE"
                )
                print("Migration completed successfully on PostgreSQL.")
            else:
                raise RuntimeError(f"Unsupported database dialect: {dialect}")


if __name__ == '__main__':
    migrate()
