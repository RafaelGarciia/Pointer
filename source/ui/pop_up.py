import tkinter as tk
from tkinter import ttk, messagebox

from source import utils, data_base


class New_ticket(utils.Pop_Up):
    def __init__(self, window):
        super().__init__(window, title='Novo Ticket')

        # Ticker entry
        self.ticker_entry = utils.Label_entry(self, 'Ativo', top_label=True)
        self.ticker_entry.set_focus()
        self.ticker_entry.pack(pady=2, side='top')

        # Botão de save
        ttk.Button(self, text='Salvar', command=self.save).pack(pady=2)
        
        # Binding Entry
        self.ticker_entry.entry_bind('Return', lambda x: self.save())

    def save(self):
        
        # Coleta o que foi digitado
        ticker = self.ticker_entry.get().strip().upper()
        
        if not check_ticker(ticker):
            return

        # Registra o ticker no banco de dados
        data_base.save_ticket(ticker)
        self.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} cadastrado com sucesso.')
        
        # Finaliza a função
        return


class Edit_ticker(utils.Pop_Up):
    def __init__(self, window, item):
        super().__init__(window, title='Editar Ticket')

        self.item = item

        # Ticker entry
        self.ticker_entry = utils.Label_entry(self, 'Ativo', top_label=True)
        self.ticker_entry.set(item[0])
        self.ticker_entry.set_focus()
        self.ticker_entry.pack(pady=2, side='top')

        # Botão de save
        ttk.Button(self, text='Salvar', command= self.edit).pack(
            pady=5, padx=10, side='left'
        )

        # Botão de delete
        ttk.Button(self, text='Excluir', command=self.delete).pack(
            pady=5, padx=10, side='right'
        )

        # Binds
        self.ticker_entry.entry_bind('Return', lambda x: self.edit())

    def edit(self, event=None):
        # Coleta o que foi digitado
        ticker = self.ticker_entry.get().strip().upper()

        if not check_ticker(ticker):
            return
    
        # Registra o ticker no banco de dados
        data_base.edit_ticker(f'{self.item[0]}', ticker)
        self.destroy()
        messagebox.showinfo('Sucesso', f'{self.item[0]} alterado com sucesso para {ticker}.')

    def delete(self, event=None):
        
        if not check_ticker(self.item[0], True):
            return
        
        # Registra o ticker no banco de dados
        data_base.remove_ticker(self.item[0])
        self.destroy()
        messagebox.showinfo('Sucesso', f'{self.item[0]} deletado com sucesso.')


def format_ticker(ticker) -> str:
    # Formata o ticker colocando .SA no final, para utilizar na busca
    ticker = ticker if ticker.upper().endswith('.SA') else f'{ticker.upper()}.SA'
    return ticker

def check_ticker(ticker:str, not_register:bool = False):
    # Verifica se esta vazio
    if not ticker:
        messagebox.showwarning('Aviso', 'Digite um ativo.')
        return False

    # Carrega os ticker salvos no banco de dados
    tickers_db = data_base.load_tickers()

    # Verifica se o ticker já esta registrado
    if not_register:
        if not ticker in tickers_db:
            messagebox.showinfo('Ativo não cadastrado', f"'{ticker}' não está cadastrado.")
            return False
        else:
            return True
    else:
        if ticker in tickers_db:
            messagebox.showinfo('Ativo já cadastrado', f"'{ticker}' já cadastrado.") 
            return False
        else:
            return True


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
