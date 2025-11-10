import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor

from source import utils, icons, data_base, search
from source.ui import pop_up
from math import floor


class Pointer_consult(ttk.Frame):
    MAX_WORKERS:int = 6 # Maximo de threds utilizados na consulta

    def __init__(self, window: tk.Tk):
        super().__init__(window)

        self.window = window

        # Variavel para controlar o orçamento
        self.budget_var = utils.RealString(self, 1000)

        # --------- Controle de Execução --------- #
        self.executor = ThreadPoolExecutor(self.MAX_WORKERS)
        self.total_tickers = 0
        self.processed_tickers = 0

        # -------------- Frame Entry ------------- #
        frame_entry = ttk.Frame(self)
        frame_entry.pack(side='top', anchor='w', padx=8)

        # ------------- Budget Entry ------------- #
        self.budget_entry = utils.Label_entry(frame_entry, 'Orçamento:', 15, 'right', textvariable=self.budget_var)
        self.budget_entry.pack(fill='x', pady=8, side='left')

        # Binding budget entry
        for event in ('<FocusOut>', '<Return>'):
            self.budget_entry.entry.bind(event, lambda x: self.budget_var._set(self.budget_entry.get()))

        # ---------------- Botões ---------------- #
        # Carrega ícones
        self.icon_search = tk.PhotoImage(data=icons.img_lupa)
        self.icon_new_ticker = tk.PhotoImage(data=icons.img_new_ticket)

        # Botão de Busca
        bt = ttk.Button(frame_entry, command=self.load_table)
        bt.configure(
            image=self.icon_search
        ) if self.icon_search else bt.configure(text='buscar')
        bt.pack(side='left', padx=5)

        # Botão de novo
        bt = ttk.Button(frame_entry, command=lambda: pop_up.New_ticket(self))
        bt.configure(
            image=self.icon_new_ticker
        ) if self.icon_new_ticker else bt.configure(text='Novo ticker')
        bt.pack(side='left', padx=5)

        # ---------------- Tabela ---------------- #
        # Table Frame
        table_frame = ttk.Frame(self)
        table_frame.pack(expand=True, fill='both', padx=8, pady=(4, 0))

        # Table
        self.table = utils.Table(table_frame,
            ('Ativo', 'Preço', 'Med. Div.', 'N Cotas', 'Proventos'),
        )

        # Bind
        self.table.bind('<Double-1>',
            lambda x: pop_up.Edit_ticker(self, self.table.item(self.table.focus(), 'values'))
        )

        # ----- Barra de Progresso + Status ------ #
        self.progress_bar = utils.ProgressBar(self, 400, status_label='...')
        self.progress_bar.pack(fill='x', pady=8, padx=8)

        # --------------- Protocol --------------- #
        window.protocol('WM_DELETE_WINDOW', self._on_closing)

    def _on_closing(self):
        """Finaliza o executor antes de fechar o programa."""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass

        self.window.destroy()

    def load_table(self):

        # Carrega os tickers do banco de dados
        tickers = data_base.load_tickers()

        # caso não houver tickers no banco de dados
        if not tickers:
            messagebox.showinfo('Sem tickers', 'Nenhum ticker cadastrado.')

            # Atualiza a barra de progresso
            self.progress_bar.bar['value'] = 0
            self.progress_bar.bar['maximum'] = 0
            self.progress_bar.status_label.config(text='Pronto')
            return

        # Caso haja tickers no banco de dados, configura a barra de progresso
        self.progress_bar.bar['value'] = 0
        self.progress_bar.bar['maximum'] = len(tickers)
        self.progress_bar.status_label.config(text=f'0/{len(tickers)}')

        # Limpa todos os itens da tabla
        self.table.clear_table()

        # Faz o submit task para o executor
        for ticker in tickers:
            fut = self.executor.submit(search.search_worker, ticker)
            fut.add_done_callback(self._on_search_done)

    def _on_search_done(self, fut):
        try:
            result = fut.result()
        except Exception as erro:
            result = ('error', str(erro), None)

        # Schedule na main thread
        self.after(0, lambda: self._process_result_on_main_thread(result))

    def _process_result_on_main_thread(self, result):
    
        data = result[1]

        if result[0]:
            # Iniciando as variaveis para o calculo
            budget_value: float = self.budget_var._get()   # Orçamento
            quotas = 0      # Cotas
            earnings = 0.0  # Proventos
            price = data['price']
            divs_year = data ['divs_year']

            # Calcula as cotas com base no orçamento
            if price and price > 0 and budget_value > 0:
                # Quantas cotas consegue comprar com o valor de orçãmento
                quotas = floor(budget_value / price)
                # Quantos dividendos recebera com a quantidade de cotas compradas
                earnings = round(quotas * divs_year, 2)

                # Tag color categorize
                if divs_year > price * 0.15:
                    tag = 'verde'     # Yield > 15% do preço
                elif divs_year > price * 0.10:
                    tag = 'amarelo'   # Yield > 10% do preço
                elif divs_year > price * 0.01:
                    tag = ''          # Yield > 5% do preço
                else:
                    tag = ''

            self.table.insert('', 'end', values=(data['ticker'], price, divs_year, quotas, earnings), tags=(tag,))

        else:
            # Caso a consulta não seja bem sucedida
            self.table.insert('', 'end', values=(data['ticker'], 'Erro', '-', '-', '-'), tags=('vermelho',))

        # ---------- Progress bar ------------- #
        self.progress_bar.progress()



class Wallet(ttk.Frame):
    def __init__(self, window: tk.Tk = None):
        super().__init__(window)

        ttk.Button(self, text='Adicionar', command=self.new_transaction).pack()
        ttk.Button(self, text='Atualziar', command=self.load_table).pack()

        self.table = ttk.Treeview(self, columns=('Ativo', 'Quantidade', 'Valor medio'), show='headings', height=6)
        for c, w in [('Ativo', 80), ('Quantidade', 100), ('Valor medio', 120)]:
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=w, anchor='center')
        self.table.pack(fill='both', expand=True)

        self.load_table()

    def new_transaction(self):
        pop_up.new_transaction(self)
        self.load_table()

    def load_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        pos = self.compute_positions()
        for a, v in pos.items():
            self.table.insert("", "end", values=(a, f"{v['qnt']:.4f}", f"{v['avg_cost']:.4f}"))

    def compute_positions(self):

        rows = data_base.get_all_transactions(order_by="date ASC, id ASC")
        pos = {}
        for row in rows:
            _, date_iso, inp_type, active, qnt, price, fees, notes = row
            active:str = active.upper()
            qnt = float(qnt)
            price = float(price)
            fees = float(fees)
            total = price * qnt if inp_type == 'Compra' else -(price * qnt)

            if active not in pos:
                pos[active] = {'qnt': 0.0, 'invested': 0.0}
            
            if inp_type == 'Compra':
                pos[active]['qnt'] += qnt
                pos[active]['invested'] += price * qnt
            else: # Venda
                pos[active]['qnt'] -= qnt
                if pos[active]['qnt'] <= 0:
                    pos[active]['invested'] = max(0.0, pos[active]['invested'] - price * qnt)
                
        for acti, v in list(pos.items()):
            qnt = v['qnt']
            invested = v['invested']
            if qnt != 0:
                v['avg_cost'] = invested / qnt
            else:
                v['avg_cost'] = 0.0

        return {a: v for a, v in pos.items() if abs(v['qnt']) > 1e-9}