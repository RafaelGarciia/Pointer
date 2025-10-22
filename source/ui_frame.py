# Imports

# Tkinter UI
import tkinter as tk
from tkinter import ttk, messagebox
# Modulos 
from source import (data_base as db)


class Center_pop_up(tk.Toplevel):
    def __init__(self, master:tk.Tk, title = 'Pop UP'):
        super().__init__(master)
        self.title(title)

        # Tamanho da janela
        w, h = 200, 100

        # Atualiza a janela
        master.update_idletasks()
        # Centraliza o TopLevel na janela principal
        x = master.winfo_x() + (master.winfo_width()//2) - (w//2)
        y = master.winfo_y() + (master.winfo_height()//2) - (h//2)
        self.geometry(f'{w}x{h}+{x}+{y}')
        self.transient(master)
        self.resizable(False, False)
        self.grab_set()




def pop_up_edit_ticker(master:tk.Tk, item):
    if not item:
        return
    
    # Janela Top Level
    pop_up_win = Center_pop_up(master, 'Edit Ticker')

    # Label indicativa
    ttk.Label(pop_up_win, text='Ativo: ').pack(pady=(12, 5))

    # Entrada do ativo
    ticker_entry = ttk.Entry(pop_up_win, justify='center')
    ticker_entry.focus_set()
    ticker_entry.insert('end', item[0])
    ticker_entry.pack(pady=2)

    def edit():
        ticker = ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning('Aviso', 'Digite um Ativo.')
            return
        
        # Formata o ticker. Ex: 'PETR4.SA'
        ticker = (ticker if ticker.upper().endswith('.SA') else f'{ticker.upper()}.SA')

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Verifica se o ticket ja esta no banco de dados
        if ticker in tickers:
            messagebox.showinfo('Ativo já cadastrado', f"'{ticker}' já está cadastrado.")
            return
        
        # Registra o ticker no banco de dados
        db.edit_ticker(f'{item[0]}.SA', ticker)
        pop_up_win.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} cadastrado com sucesso.')

    def delete():
        ticker = f'{item[0]}.SA'
        if not ticker:
            messagebox.showwarning('Aviso', 'Digite um Ativo.')
            return
        
        # Formata o ticker. Ex: 'PETR4.SA'
        ticker = (ticker if ticker.upper().endswith('.SA') else f'{ticker.upper()}.SA')

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Verifica se o ticket ja esta no banco de dados
        if not ticker in tickers:
            messagebox.showinfo('Ativo não cadastrado', f"'{ticker}' não está cadastrado.")
            return
        
        # Registra o ticker no banco de dados
        db.remove_ticker(ticker)
        pop_up_win.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} deletado com sucesso.')


    # Botão de save
    ttk.Button(pop_up_win, text='Salvar', command=edit).pack(pady=5, padx=10, side='left')

    # Botão de delete
    ttk.Button(pop_up_win, text='Excluir', command=delete).pack(pady=5, padx=10, side='right')

    # Binds
    ticker_entry.bind('<Return>', edit)





def pop_up_new_ticker(master:tk.Tk):
    # Janela Top Level
    pop_up_win = tk.Toplevel(master)
    pop_up_win.title('Novo ticker')

    # Tamanho da janela
    w, h = 200, 100

    # Atualiza a janela
    master.update_idletasks()
    # Centraliza o TopLevel na janela principal
    x = master.winfo_x() + (master.winfo_width()//2) - (w//2)
    y = master.winfo_y() + (master.winfo_height()//2) - (h//2)
    pop_up_win.geometry(f'{w}x{h}+{x}+{y}')
    pop_up_win.transient(master)
    pop_up_win.grab_set()

    # Label indicativa
    ttk.Label(pop_up_win, text='Ativo: ').pack(pady=(12, 5))

    # Entrada do ativo
    ticker_entry = ttk.Entry(pop_up_win, justify='center')
    ticker_entry.focus_set()
    ticker_entry.pack(pady=2)

    # -------------- Função Save ------------- #
    def save():
        ticker = ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning('Aviso', 'Digite um Ativo.')
            return
        
        # Formata o ticker. Ex: 'PETR4.SA'
        ticker = (ticker if ticker.upper().endswith('.SA') else f'{ticker.upper()}.SA')

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Verifica se o ticket ja esta no banco de dados
        if ticker in tickers:
            messagebox.showinfo('Ativo já cadastrado', f"'{ticker}' já está cadastrado.")
            return
        
        # Registra o ticker no banco de dados
        db.save_ticket(ticker)
        pop_up_win.destroy()
        messagebox.showinfo('Sucesso', f'{ticker} cadastrado com sucesso.')


    # Botão de save
    ttk.Button(pop_up_win, text='Salvar', command=save).pack(pady=2)

    # Binds
    ticker_entry.bind('<Return>', save)