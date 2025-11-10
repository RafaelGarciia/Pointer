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


def new_transaction(window: frame.Wallet):
    def save():
        try:
            date_iso = utl.parse_date_br(entry_date.get())
        except ValueError as error:
            messagebox.showerror('Data inválida', str(error))
            return
        
        inp_type = type_var.get()
        active = entry_active.get().strip()

        if not active:
            messagebox.showerror('Erro', 'Informe o ticker do ativo.')
            return
        
        try:
            qnt = float(entry_qnt.get().replace(',', '.'))
            price = float(entry_price.get().replace(',', '.'))
            fees = float(entry_fees.get().replace(',', '.'))
        except Exception:
            messagebox.showerror('Erro', "Quantidade, preço e taxa devem ser números (use ponto ou virgula).")
            return
        
        notes = entry_notes.get().strip()

        db.add_transaction(date_iso, inp_type, active, qnt, price, fees, notes)
        pop_up.destroy()
        window.load_table()
        messagebox.showinfo('ok', "Transação adicionada.")

    # Janela Top Level
    pop_up = utl.Pop_Up(window, 'New Transaction')
    pop_up.geometry('300x300')

    # Data entry
    ttk.Label(pop_up, text="Data:", anchor='center').grid(row=0, column=0, pady=4, padx=4)
    entry_date = ttk.Entry(pop_up, width=12)
    entry_date.grid(row=0, column=1, sticky="w", padx=(4,12), pady=4)

    # Tipo
    ttk.Label(pop_up, text="Tipo:", anchor='center').grid(row=0, column=2, pady=4, padx=4)
    type_var = tk.StringVar(value="Compra")
    cb_type = ttk.Combobox(pop_up, values=["Compra", "Venda"], textvariable=type_var, width=9, state="readonly")
    cb_type.grid(row=0, column=3, sticky="w", padx=(4,12), pady=4)

    # Ativo
    ttk.Label(pop_up, text="Ativo:", anchor='center').grid(row=1, column=0, pady=4, padx=4)
    entry_active = ttk.Entry(pop_up, width=12)
    entry_active.grid(row=1, column=1, sticky="w", padx=(4,12), pady=4)

    # Quantidade
    ttk.Label(pop_up, text="Quant.:", anchor='center').grid(row=1, column=2, pady=4, padx=4)
    entry_qnt = ttk.Entry(pop_up, width=12)
    entry_qnt.grid(row=1, column=3, sticky="w", padx=(4,12), pady=4)

    # Preço
    ttk.Label(pop_up, text="Preço/uni:", anchor='center').grid(row=2, column=0, pady=4, padx=4)
    entry_price = ttk.Entry(pop_up, width=12)
    entry_price.grid(row=2, column=1, sticky="w", padx=(4,12), pady=4)

    # Taxa
    ttk.Label(pop_up, text="Taxas:", anchor='center').grid(row=2, column=2, pady=4, padx=4)
    entry_fees = ttk.Entry(pop_up, width=12)
    entry_fees.grid(row=2, column=3, sticky="w", padx=(4,12), pady=4)

    # Notas
    ttk.Label(pop_up, text="Notas:", anchor='center').grid(row=3, column=0, pady=4, padx=4)
    entry_notes = ttk.Entry(pop_up, width=37)
    entry_notes.grid(row=3, column=1, columnspan=3, sticky="w", pady=4)

    # Botão de salvar
    ttk.Button(pop_up, text="Salvar", command=save).grid(row=4, column=0, columnspan=4)
