import tkinter as tk
from tkinter import ttk, messagebox
import data_base as db
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta
from math import floor
import threading


class PointerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Pointer')
        self.geometry('900x550')

        self.value = tk.IntVar(value=1000)
        self.sorting_order = {}
        self.total_tickers = 0
        self.processed_tickers = 0

        self.create_widgets()
        db.db_init()
        self.load_table()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, fill='both')

        # Campo de valor
        tk.Label(self, text='Valor:').pack(side='left', padx=5)
        entry = tk.Entry(self, textvariable=self.value, width=10)
        entry.pack(side='left')
        entry.bind('<Return>', self.load_table)

        # Treeview
        columns = ('Ativo', 'Preço', 'Med. Div.', 'N Cotas', 'Proventos')
        self.sorting_order = {col: True for col in columns}

        self.table = ttk.Treeview(main_frame, columns=columns, show='headings')
        for col in columns:
            self.table.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.table.column(col, width=100)

        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(expand=True, fill='both', side='left')
        scrollbar.pack(fill='y', side='left')

        # Bindings
        self.table.bind('<Double-1>', lambda e: self.load_table())
        self.table.bind('<Button-2>', self.on_click_2)

        # Barra de progresso
        progress_frame = tk.Frame(self)
        progress_frame.pack(fill='x', pady=5)

        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(side='left', padx=10)

        self.status_label = tk.Label(progress_frame, text="Pronto")
        self.status_label.pack(side='left')

    def sort_column(self, col):
        itens = [(self.table.set(k, col), k) for k in self.table.get_children('')]

        try:
            itens = [(float(v), k) for v, k in itens]
        except ValueError:
            pass

        reverse = not self.sorting_order[col]
        itens.sort(key=lambda t: t[0], reverse=reverse)

        for index, (_, k) in enumerate(itens):
            self.table.move(k, '', index)

        self.sorting_order[col] = not self.sorting_order[col]

    def on_click_2(self, event):
        if not self.table.identify_row(event.y):
            self.win_add()

    def win_add(self):
        add_win = tk.Toplevel(self)
        add_win.title("Adicionar Ativo")
        w, h = 300, 200

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        add_win.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(add_win, text="Ativo:").pack(pady=5)
        ativo_entry = tk.Entry(add_win)
        ativo_entry.pack(pady=5)

        def save():
            ativo = ativo_entry.get().strip().upper()
            if self.register_ticket(ativo):
                add_win.destroy()

        tk.Button(add_win, text="Salvar", command=save).pack(pady=10)

    def load_table(self, event=None):
        # Limpa tabela
        for item in self.table.get_children():
            self.table.delete(item)

        tickers = db.load_tickers()
        self.total_tickers = len(tickers)
        self.processed_tickers = 0

        # Configura barra de progresso
        self.progress['value'] = 0
        self.progress['maximum'] = self.total_tickers
        self.status_label.config(text=f"Processando 0/{self.total_tickers} tickers...")

        # Busca em threads
        for ticker in tickers:
            threading.Thread(target=self.search, args=(ticker,), daemon=True).start()

    def register_ticket(self, ticker: str) -> bool:
        if not ticker:
            messagebox.showwarning("Aviso", "Digite um Ativo.", icon="info")
            return False

        ticker = ticker if ticker.endswith(".SA") else f"{ticker}.SA"

        if ticker in db.load_tickers():
            messagebox.showinfo("Ativo já cadastrado", f"'{ticker}' já está cadastrado.", icon='warning')
            return False

        db.save_ticket(ticker)
        return True

    def search(self, ticker: str):
        try:
            active = yf.Ticker(ticker)
            info = active.info
            price = info.get('currentPrice')

            if price is None:
                raise ValueError("Preço não disponível")

            divs = active.dividends
            inicio = (date.today() - relativedelta(years=1)).replace(day=1)
            divs_ult12 = divs.loc[str(inicio):].tail(12).sum()

            cotas = floor(self.value.get() / price)
            proventos = round(cotas * divs_ult12, 2)

            # Decide cor com base no dividend yield
            if divs_ult12 > 5:      # arbitrário: dividendos altos
                tag = 'verde'
            elif divs_ult12 > 0:    # dividendos médios
                tag = 'amarelo'
            else:                   # sem dividendos
                tag = 'vermelho'

            self.table.after(0, lambda: self.insert_with_color(
                ticker.rstrip('.SA'), price, divs_ult12, cotas, proventos, tag
            ))

        except Exception as e:
            print(f"Erro ao buscar {ticker}: {e}")
            self.table.after(0, lambda: self.table.insert('', 'end', values=("Erro", ticker, "-", "-", "-")))
        finally:
            self.table.after(0, self.update_progress)

    def insert_with_color(self, ticker, price, divs_ult12, cotas, proventos, tag):
        self.table.insert('', 'end', values=(ticker, price, divs_ult12, cotas, proventos), tags=(tag,))
        # Configura cores
        self.table.tag_configure('verde', background='#d4fcdc')    # verde claro
        self.table.tag_configure('amarelo', background='#fffacd')  # amarelo claro
        self.table.tag_configure('vermelho', background='#fcdcdc') # vermelho claro

    def update_progress(self):
        self.processed_tickers += 1
        self.progress['value'] = self.processed_tickers
        self.status_label.config(text=f"Processando {self.processed_tickers}/{self.total_tickers} tickers...")
        if self.processed_tickers == self.total_tickers:
            self.status_label.config(text="Concluído!")


if __name__ == "__main__":
    app = PointerApp()
    app.mainloop()
