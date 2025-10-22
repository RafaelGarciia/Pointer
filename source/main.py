# Imports

# Tkinter UI
import tkinter as tk
from tkinter import ttk, messagebox
# Data manager
from datetime import date
from dateutil.relativedelta import relativedelta
# Functions
import yfinance as yf
from functools import partial
from math import floor
from concurrent.futures import ThreadPoolExecutor
# Modulos 
from source import (
    icons,
    data_base as db,
    ui_frame
)

# String para a moeda Real br
class RealString(tk.StringVar):
    def __init__(self, master=None, value='0,0', *kwargs):
        super().__init__(master)

        self.integer, self.decimal = 0,0

        self._set(str(value))

    def _set(self, value:int | float):
        if str(value).isdigit():
            value = int(value)
        else:
            value = str(value).replace('.', '')
            value = str(value).replace(',', '.')
            try:
                value = float(value)
            except:
                print('erro')
        
        self.integer, self.decimal = f"{value:.2f}".split(".")
        f_value = f"{int(self.integer):,}".replace(",", ".")
        self.set(f"{f_value},{self.decimal}")

    def _get(self):
        return float(f'{self.integer}.{self.decimal}')

# ----------------- Main ----------------- #
class App(tk.Tk):
    WINDOW_WIDTH = 600 # Largura da janela principal
    WINDOW_HEIGHT = 600 # Autura da janela principal
    MAX_WORKERS = 6  # limite de threads para consultas

    def __init__(self):
        super().__init__()
        self.title('Pointer') # Define o titulo da janela
        self.geometry(f'{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}')
        self.resizable(False, False)

        # Definindo variaveis
        self.budget = RealString(self, 1000)

        # Controle de Execução
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        self.total_tickers = 0
        self.processed_tickers = 0


        db.db_init() # Carrega o Banco de dados
        self.create_ui() # Carrega a Interfase grafica

    def sort_column(self, col: str):
        """ Ordena a coluna do Treeview.
            Tenta ordenar numericamente quando possivel.
        """
        children = self.table.get_children('')
        data = [(self.table.set(k, col), k) for k in children]
        try:
            # Tenta utilizar como float
            data.sort(key=lambda t: float(str(t[0]).replace(',', '.')),reverse=not self.sorting_order[col])
        except Exception:
            # Caso não utiliza str
            data.sort(key=lambda t: str(t[0]), reverse=not self.sorting_order[col])

        for index, (_, k) in enumerate(data):
            self.table.move(k, '', index)
        self.sorting_order[col] = not self.sorting_order[col]


    def create_ui(self):
        # Main Frame
        interact_frame = ttk.Frame(self, padding=10)
        interact_frame.pack(side='top', fill='x')

        # Campo de Orçamento
        ttk.Label(interact_frame, text='Orçamento:').pack(side='left', padx=5)
        budget_entry = ttk.Entry(
            interact_frame, textvariable=self.budget, width=15, justify='right'
        )
        budget_entry.pack(side='left')
        for ev in ('<FocusOut>', '<Return>'):
            budget_entry.bind(ev, lambda x: self.budget._set(budget_entry.get()))

        # Carrega ícones
        self.icon_search = tk.PhotoImage(data=icons.img_lupa)
        self.icon_new_ticker = tk.PhotoImage(data=icons.img_new_ticket)

        

        #------------------------------------------#
        # ---------------- Botões ---------------- #
        #------------------------------------------#

        # Botão de Busca
        bt = ttk.Button(interact_frame, command=self.load_table)
        bt.configure(image=self.icon_search) if self.icon_search else bt.configure(text='buscar')
        bt.pack(side='left', padx=5)

        # Botão de novo
        bt = ttk.Button(interact_frame, command=partial(ui_frame.pop_up_new_ticker, self))
        bt.configure(image=self.icon_new_ticker) if self.icon_new_ticker else bt.configure(text='Novo ticker')
        bt.pack(side='left', padx=5)

        #------------------------------------------#
        # ---------------- Tabela ---------------- #
        #------------------------------------------#

        # Treeview Frame
        treeview_frame = ttk.Frame(self)
        treeview_frame.pack(expand=True, fill='both', padx=8, pady=(4, 0))

        # Colunas
        columns = ('Ativo', 'Preço', 'Med. Div.', 'N Cotas', 'Proventos')
        self.sorting_order = {col: True for col in columns}

        # Tabela
        self.table = ttk.Treeview(treeview_frame, columns=columns, show='headings', height=18)
        for col in columns:
            self.table.heading(col, text=col, command=partial(self.sort_column, col))
            self.table.column(col, width=100, anchor='center')

        # Bind
        self.table.bind('<Double-1>', lambda x: ui_frame.pop_up_edit_ticker(self, self.table.item(self.table.focus(), 'values')))

        # Color Tags
        self.table.tag_configure('verde', background='#d4fcdc')
        self.table.tag_configure('amarelo', background='#fffacd')
        self.table.tag_configure('vermelho', background='#fcdcdc')

        # Scrollbar
        v_scrollbar = ttk.Scrollbar(treeview_frame, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=v_scrollbar.set)
        self.table.pack(expand=True, fill='both', side='left')
        v_scrollbar.pack(fill='y', side='left')

        #------------------------------------------#
        # ----- Barra de Progresso + Status ------ #
        #------------------------------------------#

        # PB frame
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill='x', pady=8, padx=8)

        # Barra de Progresso
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(side='left', padx=5)

        # Label de Status
        self.status_label = ttk.Label(progress_frame, text='Pronto')
        self.status_label.pack(side='left', padx=5)

        #------------------------------------------#
        # --------------- Protocol --------------- #
        #------------------------------------------#

        self.protocol('WM_DELETE_WINDOW', self.on_closing)

    # ---------- Finalizar a janela ---------- #
    def on_closing(self):
        "Finaliza o executor antes de fechar o programa."
        try: self.executor.shutdown(wait=False)
        except Exception: pass
        self.destroy()
    
    #------------------------------------------#
    # ----------- Load and search ------------ #
    #------------------------------------------#
    def load_table(self, event=None):
        """Limpa a tabela e busca os tickers salvos no DB."""

        # Limpa a tabela
        for item in self.table.get_children(): self.table.delete(item)

        # Carrega os ticker no banco de dados
        tickers = db.load_tickers()

        # Caso não tiver tickers no banco
        if not tickers:
            messagebox.showinfo('Sem tickers', 'Nenhum ticker cadastrado.')

            # Atualiza a barra de progresso
            self.progress['value'] = 0
            self.progress['maximum'] = 0
            self.status_label.config(text='Pronto')
            return
        
        # Caso haja tickers no banco, configura a barra de progresso
        self.total_tickers = len(tickers)
        self.processed_tickers = 0
        self.progress['value'] = 0
        self.progress['maximum'] = self.total_tickers
        self.status_label.config(text=f'Processando 0/{self.total_tickers} tickers...')

        # Faz o submit task para o executor
        for ticker in tickers:
            fut = self.executor.submit(self.search_worker, ticker)
            fut.add_done_callback(self._on_search_done)


    #------------------------------------------#
    # ---------- Busca em threads ------------ #
    #------------------------------------------#
    def search_worker(self, ticker: str) -> tuple[str, dict | str | None]:
        """ Executa uma busca em thread worker.
            Retorna uma tupla com status e dados:
             - ('ok', {...})
             - ('error', 'mensagem de erro')
        """
        try:
            tk_upper = ticker.upper() # Registra o ticker em maiusculo
            active = yf.Ticker(tk_upper) # Instancia o ticker
            info = active.info or {} # Arraw de info

            # Tenta obter o preço atual do ativo de forma segura
            price = (info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose'))

            # Se não houve preço, retorna isso
            if price is None: raise ValueError('Preço não disponível')

            # Ultimos Dividendos (Início definido pela UI data)
            start_date = (date.today() - relativedelta(years=1)).replace(day=1)
            divs = getattr(active, 'dividends', None)
            divs_year = 0.0

            # Filtra e soma os dividendos
            try:
                if divs is not None and not divs.empty:
                    s = divs.loc[str(start_date) :]
                    divs_year = float(s.tail(12).sum())
            except Exception:
                divs_year = 0.0

            # Iniciando as variaveis para o calculo
            budget_value:float = self.budget._get() # Orçamento
            quotas = 0      # Cotas
            earnings = 0.0  # Proventos

            # Calcula as cotas com base no orçamento
            if price and price > 0 and budget_value > 0:
                # Quantas cotas consegue comprar com o valor de orçãmento
                quotas = floor(budget_value / price) 
                # Quantos dividendos recebera com a quantidade de cotas compradas
                earnings = round(quotas * divs_year, 2)
            
            # Tag color categorize
            if divs_year > price * 0.15: tag = 'verde' # Yield > 15% do preço
            elif divs_year > price * 0.10: tag = 'amarelo' # Yield > 10% do preço
            elif divs_year > price * 0.01: tag = '' # Yield > 5% do preço
            else: tag = ''

            # Compilação das informações em um dict
            data = {
                'ticker': tk_upper.rstrip('.SA'),
                'price': price,
                'divs_year': round(divs_year, 4),
                'quotas': quotas,
                'earnings': earnings,
                'tag': tag,
            }
            return ('ok', data)
        except Exception as exc:
            data = {
                'ticker': tk_upper.rstrip('.SA'),
                'price': '--',
                'divs_year': '--',
                'quotas': '--',
                'earnings': '--',
                'tag': '--',
            }
            return ('error', data) #f'Erro buscando {ticker}: {exc}'

    def _on_search_done(self, fut):
        """Callback (executado em thread do executor). Agendamos o tratamento no thread principal."""
        try: result = fut.result()
        except Exception as erro: result = ('error', str(erro), None)

        # Schedule na main thread
        self.after(0, partial(self._process_result_on_main_thread, result))


    #------------------------------------------#
    # ---------- Processo thread ------------- #
    #------------------------------------------#
    def _process_result_on_main_thread(self, result):
        """ Insere os resultados na Treeview e atualiza a progressbar."""

        # Caso a consulta seja bem sucedida
        if result[0] == 'ok':
            data = result[1]
            self.table.insert('', 'end', values=(
                data['ticker'],
                data['price'],
                data['divs_year'],
                data['quotas'],
                data['earnings'],
            ),
            tags=(data['tag'],)
            )
        else:
            # Erro: adiciona uma linha com a mensagem
            data = result[1]
            self.table.insert('', 'end',
                values=(data['ticker'],'Erro', '-', '-', '-'), tags=('vermelho',)
            )

        # ---------- Progress bar ------------- #
        self.processed_tickers += 1
        self.progress['value'] = self.processed_tickers
        self.status_label.config(text=f'Processando {self.processed_tickers}/{self.total_tickers} tickers...')
        if self.processed_tickers >= self.total_tickers: self.status_label.config(text='Concluído!')
        