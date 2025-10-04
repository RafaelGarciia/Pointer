import sqlite3 as sql
import os

# Caminho e nome do banco
DB_FOLDER = "database"
DB_NAME = "tickers"
DB_PATH = os.path.join(DB_FOLDER, f"{DB_NAME}.db")


def connect() -> tuple[sql.Connection, sql.Cursor]:
    # Cria a pasta se não existir
    os.makedirs(DB_FOLDER, exist_ok=True)

    # Cria (ou abre) o banco de dados
    connection = sql.connect(f'{DB_PATH}')
    cursor = connection.cursor()

    return connection, cursor


def db_init():
    connection, cursor = connect()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickers (
            id TEXT UNIQUE
        )
    """
    )
    connection.commit()
    connection.close()


def save_ticket(id):
    connection, cursor = connect()
    try:
        cursor.execute('INSERT INTO tickers (id) VALUES (?)', (id,))
        connection.commit()
    except sql.IntegrityError:
        print('IntegrityError')
    connection.close()


def load_tickers():
    connection, cursor = connect()
    cursor.execute('SELECT id FROM tickers')
    data = [item[0] for item in cursor.fetchall()]
    connection.close()
    return data


def remove_ticker(id):
    connection, cursor = connect()
    cursor.execute(f'DELETE FROM tickers WHERE id = {id}')
    connection.commit()
    connection.close()
