import tkinter as tk
from tkinter import ttk, messagebox

from source import data_base as db, icons, search
from source.ui import utils as utl
from source.ui import pop_up
from concurrent.futures import ThreadPoolExecutor


class Pointer_consult(ttk.Frame):
    MAX_WORKERS = 6  # limite de threads para consultas

    def __init__(self, window: tk.Tk = None):
        super().__init__(window)

        self.budget_var = utl.RealString(self, value=1000)

        # Controle de Execução
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        self.total_tickers = 0
        self.processed_tickers = 0

        # Top frame
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', pady=8)

        # Campo de Orçamento
        ttk.Label(top_frame, text='Orçamento:').pack(side='left', padx=5)
        budget_entry = ttk.Entry(
            top_frame, textvariable=self.budget_var, width=15, justify='right'
        )
        budget_entry.pack(side='left')
        for event in ('<FocusOut>', '<Return>'):
            budget_entry.bind(
                event, lambda x: self.budget_var._set(budget_entry.get())
            )

        # Carrega ícones
        self.icon_search = tk.PhotoImage(data=icons.img_lupa)
        self.icon_new_ticker = tk.PhotoImage(data=icons.img_new_ticket)

        # ---------------- Botões ---------------- #

        # Botão de Busca
        bt = ttk.Button(top_frame, command=self.load_table)
        bt.configure(
            image=self.icon_search
        ) if self.icon_search else bt.configure(text='buscar')
        bt.pack(side='left', padx=5)

        # Botão de novo
        bt = ttk.Button(top_frame, command=lambda: pop_up.new_ticker(self))
        bt.configure(
            image=self.icon_new_ticker
        ) if self.icon_new_ticker else bt.configure(text='Novo ticker')
        bt.pack(side='left', padx=5)

        # ---------------- Tabela ---------------- #

        # Treeview Frame
        treeview_frame = ttk.Frame(self)
        treeview_frame.pack(expand=True, fill='both', padx=8, pady=(4, 0))

        self.table = utl.Table(
            treeview_frame,
            ('Ativo', 'Preço', 'Med. Div.', 'N Cotas', 'Proventos'),
        )

        # Bind
        self.table.bind(
            '<Double-1>',
            lambda x: pop_up.edit_ticker(
                self, self.table.item(self.table.focus(), 'values')
            ),
        )

        # ----- Barra de Progresso + Status ------ #

        # PB frame
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill='x', pady=8, padx=8)

        # Barra de Progresso
        self.progress = ttk.Progressbar(
            progress_frame, orient='horizontal', length=400, mode='determinate'
        )
        self.progress.pack(side='left', padx=5)

        # Label de Status
        self.status_label = ttk.Label(progress_frame, text='Pronto')
        self.status_label.pack(side='left', padx=5)

        # --------------- Protocol --------------- #
        window.protocol('WM_DELETE_WINDOW', lambda: self.on_closing(window))

    # ---------- Finalizar a janela ---------- #
    def on_closing(self, window: tk.Tk):
        """Finaliza o executor antes de fechar o programa."""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass

        window.destroy()

    def load_table(self):

        # Limpa a tabela
        for item in self.table.get_children():
            self.table.delete(item)

        # Carrega os tickers do banco de dados
        tickers = db.load_tickers()

        # caso não houver tickers no banco de dados
        if not tickers:
            messagebox.showinfo('Sem tickers', 'Nenhum ticker cadastrado.')

            # Atualiza a barra de progresso
            self.progress['value'] = 0
            self.progress['maximum'] = 0
            self.status_label.config(text='Pronto')
            return

        # Caso haja tickers no banco de dados, configura a barra de progresso
        self.total_tickers = len(tickers)
        self.progressed_tickers = 0
        self.progress['value'] = 0
        self.progress['maximum'] = self.total_tickers
        self.status_label.config(
            text=f'Processando 0/{self.total_tickers} tickers...'
        )

        # Faz o submit task para o executor
        for ticker in tickers:
            fut = self.executor.submit(
                search.search_worker, ticker, self.budget_var
            )
            fut.add_done_callback(self._on_search_done)

    def _on_search_done(self, fut):
        """Callback (executado em thread do executor). Agendamos o tratamento no thread principal."""
        try:
            result = fut.result()
        except Exception as erro:
            result = ('error', str(erro), None)

        # Schedule na main thread
        self.after(0, lambda: self._process_result_on_main_thread(result))

    def _process_result_on_main_thread(self, result):
        """Insere os resultados na Treeview e atualiza a progressbar."""

        # Caso a consulta seja bem sucedida
        if result[0] == 'ok':
            data = result[1]
            self.table.insert(
                '',
                'end',
                values=(
                    data['ticker'],
                    data['price'],
                    data['divs_year'],
                    data['quotas'],
                    data['earnings'],
                ),
                tags=(data['tag'],),
            )
        else:
            # Erro: adiciona uma linha com a mensagem
            data = result[1]
            self.table.insert(
                '',
                'end',
                values=(data['ticker'], 'Erro', '-', '-', '-'),
                tags=('vermelho',),
            )

        # ---------- Progress bar ------------- #
        self.processed_tickers += 1
        self.progress['value'] = self.processed_tickers
        self.status_label.config(
            text=f'Processando {self.processed_tickers}/{self.total_tickers} tickers...'
        )
        if self.processed_tickers >= self.total_tickers:
            self.status_label.config(text='Concluído!')

