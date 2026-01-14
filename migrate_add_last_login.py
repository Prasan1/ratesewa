"""
Migration script to add last_login_at column to users.
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
                    'users',
                    'last_login_at',
                    "ALTER TABLE users ADD COLUMN last_login_at DATETIME"
                )
            elif dialect == 'postgresql':
                add_column_postgres(
                    conn,
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP"
                )
                print("Migration completed successfully on PostgreSQL.")
            else:
                raise RuntimeError(f"Unsupported database dialect: {dialect}")


if __name__ == '__main__':
    migrate()
