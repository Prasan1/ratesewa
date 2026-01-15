"""
Migration script to add created_at column to doctors table.
Used for ranking score calculation (account age bonus).
Works for SQLite and PostgreSQL.
"""
from sqlalchemy import inspect, text
from app import app, db


def column_exists(engine, table, column):
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table)]
    return column in columns


def migrate():
    with app.app_context():
        engine = db.engine
        dialect = engine.dialect.name

        with engine.begin() as conn:
            if dialect == 'sqlite':
                if column_exists(engine, 'doctors', 'created_at'):
                    print("Column 'created_at' already exists in doctors. Skipping.")
                else:
                    conn.execute(text("ALTER TABLE doctors ADD COLUMN created_at DATETIME"))
                    conn.execute(text("UPDATE doctors SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                    print("Added 'created_at' to doctors and set existing rows to current timestamp.")

            elif dialect == 'postgresql':
                conn.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS created_at TIMESTAMP"))
                conn.execute(text("UPDATE doctors SET created_at = NOW() WHERE created_at IS NULL"))
                print("Migration completed successfully on PostgreSQL.")

            else:
                raise RuntimeError(f"Unsupported database dialect: {dialect}")


if __name__ == '__main__':
    migrate()
