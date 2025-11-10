import sqlite3 as sql
import os

# Caminho e nome do banco
DB_FOLDER = 'database'
DB_NAME = 'Pointer_database'
DB_PATH = os.path.join(DB_FOLDER, f'{DB_NAME}.db')

TICKER_TABLE_NAME = 'search_ticker'
WALLET_TABLE_NAME = 'transactions'


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
        f"""
        CREATE TABLE IF NOT EXISTS {TICKER_TABLE_NAME} (
            id TEXT UNIQUE
        )
    """
    )
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {WALLET_TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Compra','Venda')),
            active TEXT NOT NULL,
            qnt REAL NOT NULL,
            price REAL NOT NULL,
            fees REAL DEFAULT 0,
            notes TEXT
        )
    """
    )
    connection.commit()
    connection.close()


def save_ticket(id):
    connection, cursor = connect()
    try:
        cursor.execute(f'INSERT INTO {TICKER_TABLE_NAME}(id) VALUES (?)', (id,))
        connection.commit()
    except sql.IntegrityError:
        print('IntegrityError')
    connection.close()


def load_tickers():
    connection, cursor = connect()
    cursor.execute(f'SELECT id FROM {TICKER_TABLE_NAME}')
    data = [item[0] for item in cursor.fetchall()]
    connection.close()
    return data


def remove_ticker(id):
    """Deleta um ticker do banco de dados."""
    connection, cursor = connect()
    try:
        cursor.execute(f'DELETE FROM {TICKER_TABLE_NAME} WHERE id = (?)', (id,))
        connection.commit()
    except Exception as ex:
        print(f'Erro {ex}')
    finally:
        connection.close()


def edit_ticker(old_id, new_id):
    """Renomeia um ticker existente no banco de dados."""
    connection, cursor = connect()
    try:
        cursor.execute(
            f'UPDATE {TICKER_TABLE_NAME} SET id = ? WHERE id = ?', (new_id, old_id)
        )
        connection.commit()
    except sql.IntegrityError:
        print(f"Já existe um ticker com o nome '{new_id}'.")
    except sql.OperationalError as e:
        print(f'Erro ao editar ticker: {e}')
    finally:
        connection.close()


def add_transaction(date_iso, inp_type, active, qnt, price, fees, notes):
    connection, cursor = connect()

    cursor.execute(f"""
        INSERT INTO {WALLET_TABLE_NAME} (date, type, active, qnt, price, fees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)    
    """, (date_iso, inp_type, active.upper().strip(), qnt, price, fees, notes))
    connection.commit()
    connection.close()

def get_all_transactions(order_by='date DESC'):
    connection, cursor = connect()

    cursor.execute(f"SELECT id, date, type, active, qnt, price, fees, notes FROM {WALLET_TABLE_NAME} ORDER BY {order_by}")
    rows = cursor.fetchall()
    connection.close()
    return rows