import tkinter as tk
from tkinter import ttk, messagebox

from source import utils, data_base

def new_ticker(window: tk.Tk) -> None:

    # Janela Top Level
    pop_up = utl.Pop_Up(window, 'New Ticket')

    # Label indicativa
    ttk.Label(pop_up, text='Ativo: ').pack(pady=(12, 5))

    # Entrada do ativo
    ticker_entry = ttk.Entry(pop_up, justify='center')
    ticker_entry.focus_set()
    ticker_entry.pack(pady=2)

    # -------------- Função Save ------------- #
    def save(event=None):
        ticker = ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning('Aviso', 'Digite um Ativo.')
            return

        # Formata o ticker. Ex: 'PETR4.SA'
        ticker = (
            ticker
            if ticker.upper().endswith('.SA')
            else f'{ticker.upper()}.SA'
        )

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Verifica se o ticket ja esta no banco de dados
        if ticker in tickers:
            messagebox.showinfo(
                'Ativo já cadastrado', f"'{ticker}' já está cadastrado."
            )
            return

        # Registra o ticker no banco de dados
        db.save_ticket(ticker)
        pop_up.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} cadastrado com sucesso.')

    # Botão de save
    ttk.Button(pop_up, text='Salvar', command=save).pack(pady=2)

    # Binds
    ticker_entry.bind('<Return>', save)


def edit_ticker(window: tk.Tk, item) -> None:
    if not item:
        return

    # Janela Top Level
    pop_up = utl.Pop_Up(window, 'Edit Ticket')

    # Label indicativa
    ttk.Label(pop_up, text='Ativo: ').pack(pady=(12, 5))

    # Entrada do ativo
    ticker_entry = ttk.Entry(pop_up, justify='center')
    ticker_entry.focus_set()
    ticker_entry.insert('end', item[0])
    ticker_entry.pack(pady=2)

    # -------------- Função Edit ------------- #
    def edit(event=None):
        ticker = ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning('Aviso', 'Digite um Ativo.')
            return

        # Formata o ticker. Ex: 'PETR4.SA'
        ticker = (
            ticker
            if ticker.upper().endswith('.SA')
            else f'{ticker.upper()}.SA'
        )

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Verifica se o ticket ja esta no banco de dados
        if ticker in tickers:
            messagebox.showinfo(
                'Ativo já cadastrado', f"'{ticker}' já está cadastrado."
            )
            return

        # Registra o ticker no banco de dados
        db.edit_ticker(f'{item[0]}.SA', ticker)
        pop_up.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} cadastrado com sucesso.')

    # ------------- Função Delete ------------ #
    def delete(event=None):
        ticker = f'{item[0]}.SA'
        if not ticker:
            messagebox.showwarning('Aviso', 'Digite um Ativo.')
            return

        # Formata o ticker. Ex: 'PETR4.SA'
        ticker = (
            ticker
            if ticker.upper().endswith('.SA')
            else f'{ticker.upper()}.SA'
        )

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Verifica se o ticket ja esta no banco de dados
        if not ticker in tickers:
            messagebox.showinfo(
                'Ativo não cadastrado', f"'{ticker}' não está cadastrado."
            )
            return

        # Registra o ticker no banco de dados
        db.remove_ticker(ticker)
        pop_up.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} deletado com sucesso.')

    # Botão de save
    ttk.Button(pop_up, text='Salvar', command=edit).pack(
        pady=5, padx=10, side='left'
    )

    # Botão de delete
    ttk.Button(pop_up, text='Excluir', command=delete).pack(
        pady=5, padx=10, side='right'
    )

    # Binds
    ticker_entry.bind('<Return>', edit)
