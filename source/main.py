import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import locale
import os
import source.data_base as db
from functools import partial
from math import floor
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple

# -------------------------
# Configurações iniciais
# -------------------------
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except locale.Error:
    # fallback caso o SO não tenha suporte
    locale.setlocale(locale.LC_ALL, "")


# -------------------------
# Funções auxiliares
# -------------------------
def reverse_date(date_obj: date | datetime) -> str:
    """Converte objeto date/datetime para string dd/mm/yyyy."""
    return date_obj.strftime("%d/%m/%Y")


def validate_date(date_str: str) -> bool:
    """Valida string no formato dd/mm/yyyy."""
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def format_date(var: tk.StringVar) -> str:
    """Formata e valida a data digitada (ddmmyyyy -> dd/mm/yyyy)."""
    raw = "".join(c for c in var.get() if c.isdigit())

    if len(raw) == 8:
        formatted = f"{raw[:2]}/{raw[2:4]}/{raw[4:8]}"
        if validate_date(formatted):
            return formatted

    # Default → ano anterior, mesmo mês, dia 01
    return reverse_date((date.today() - relativedelta(years=1)).replace(day=1))


def format_currency(value: str) -> str:
    """Formata valor em estilo brasileiro (1.000,00). Aceita entradas com '.' ou ','. """
    if value is None:
        return ""
    v = str(value).strip().replace(".", "").replace(",", ".")
    try:
        num = float(v)
        return locale.format_string("%.2f", num, grouping=True)
    except (ValueError, TypeError):
        return ""


def parse_currency(value: str, default: float = 0.0) -> float:
    """Converte string no formato local para float (p.ex. '1.234,56' -> 1234.56)."""
    if value is None:
        return default
    s = str(value).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return default


def load_icon(path: str) -> Optional[tk.PhotoImage]:
    """Tenta carregar um PhotoImage. Retorna None se não existir/der erro."""
    if not os.path.exists(path):
        return None
    try:
        img = tk.PhotoImage(file=path)
        return img
    except Exception:
        return None


# -------------------------
# Classe Principal
# -------------------------
class PointerApp(tk.Tk):
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 650
    MAX_WORKERS = 6  # limite de threads para consultas

    def __init__(self):
        super().__init__()
        self.title("Pointer")
        self.center_window()

        # Vars
        self.budget = tk.StringVar(value="1000,00")
        self.search_date = tk.StringVar(
            value=reverse_date((date.today() - relativedelta(years=1)).replace(day=1))
        )

        # Controle de execução
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        self.total_tickers = 0
        self.processed_tickers = 0

        # Carrega DB e UI
        db.db_init()
        self.create_widgets()

    def on_closing(self):
        """Finaliza executor antes de fechar."""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass
        self.destroy()

    def center_window(self):
        """Centraliza janela na tela."""
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        pos_x = (screen_w // 2) - (self.WINDOW_WIDTH // 2)
        pos_y = (screen_h // 2) - (self.WINDOW_HEIGHT // 2)
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{pos_x}+{pos_y}")

    def format_budget(self, *_):
        """Formata orçamento para padrão brasileiro (mostra em self.budget)."""
        self.budget.set(format_currency(self.budget.get()))

    def on_date_entry(self, *_):
        """Valida e formata campo de data."""
        self.search_date.set(format_date(self.search_date))

    def sort_column(self, col: str):
        """Ordena coluna do Treeview. Tenta ordenar numericamente quando possível."""
        children = self.table.get_children("")
        data = [(self.table.set(k, col), k) for k in children]
        try:
            # tenta interpretar como float
            data.sort(key=lambda t: float(str(t[0]).replace(",", ".")), reverse=not self.sorting_order[col])
        except Exception:
            data.sort(key=lambda t: str(t[0]), reverse=not self.sorting_order[col])

        for index, (_, k) in enumerate(data):
            self.table.move(k, "", index)
        self.sorting_order[col] = not self.sorting_order[col]

    # -------------------------
    # Widgets
    # -------------------------
    def create_widgets(self):
        # Menu simples
        menubar = tk.Menu(self)
        app_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_command(label="Carregar tickers", command=self.load_table)
        app_menu.add_command(label="Novo ticket", command=self.pop_up_new_ticket)
        app_menu.add_separator()
        app_menu.add_command(label="Sair", command=self.on_closing)
        menubar.add_cascade(label="Arquivo", menu=app_menu)
        self.config(menu=menubar)

        # Frame de entrada
        entry_frame = ttk.Frame(self, padding=10)
        entry_frame.pack(side="top", fill="x")

        # Campo de Data
        ttk.Label(entry_frame, text="Data:").pack(side="left", padx=5)
        date_entry = ttk.Entry(entry_frame, textvariable=self.search_date, width=12, justify="center")
        date_entry.pack(side="left")
        for ev in ("<FocusOut>", "<Return>"):
            date_entry.bind(ev, self.on_date_entry)

        ttk.Label(entry_frame, text=" ").pack(side="left", padx=10)  # espaçador

        # Campo de Orçamento
        ttk.Label(entry_frame, text="Orçamento:").pack(side="left", padx=5)
        budget_entry = ttk.Entry(entry_frame, textvariable=self.budget, width=15, justify="right")
        budget_entry.pack(side="left")
        for ev in ("<FocusOut>", "<Return>"):
            budget_entry.bind(ev, self.format_budget)

        # Carrega ícones (mantém referência em self para evitar GC)
        self.icon_search = load_icon("source/images/lupa.png")
        self.icon_new_ticket = load_icon("source/images/new_ticket.png")
        self.icon_add_ticket = load_icon("source/images/add_ticket.png")

        # Botões
        if self.icon_search:
            ttk.Button(entry_frame, image=self.icon_search, command=self.load_table).pack(side="left", padx=5)
        else:
            ttk.Button(entry_frame, text="Buscar", command=self.load_table).pack(side="left", padx=5)

        if self.icon_new_ticket:
            ttk.Button(entry_frame, image=self.icon_new_ticket, command=self.pop_up_new_ticket).pack(side="left", padx=5)
        else:
            ttk.Button(entry_frame, text="Novo ticket", command=self.pop_up_new_ticket).pack(side="left", padx=5)

        # Botão de atualizar (texto + possível ícone add_ticket)
        if self.icon_add_ticket:
            ttk.Button(entry_frame, image=self.icon_add_ticket, command=self.pop_up_new_ticket).pack(side="left", padx=5)
        else:
            ttk.Button(entry_frame, text="+", command=self.pop_up_new_ticket).pack(side="left", padx=5)

        # Treeview frame
        treeview_frame = ttk.Frame(self)
        treeview_frame.pack(expand=True, fill="both", padx=8, pady=(4, 0))

        columns = ("Ativo", "Preço", "Med. Div.", "N Cotas", "Proventos")
        self.sorting_order = {col: True for col in columns}

        self.table = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=18)
        for col in columns:
            self.table.heading(col, text=col, command=partial(self.sort_column, col))
            anchor = "center"
            width = 110 if col != "Ativo" else 140
            self.table.column(col, width=width, anchor=anchor)

        # Configure tags once
        self.table.tag_configure('verde', background='#d4fcdc')
        self.table.tag_configure('amarelo', background='#fffacd')
        self.table.tag_configure('vermelho', background='#fcdcdc')

        vsb = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vsb.set)
        self.table.pack(expand=True, fill="both", side="left")
        vsb.pack(fill="y", side="left")

        # Barra de progresso + status
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill="x", pady=8, padx=8)

        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(side="left", padx=10)

        self.status_label = ttk.Label(progress_frame, text="Pronto")
        self.status_label.pack(side="left", padx=5)

        # Bind janela fechar para encerrar executor
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # -------------------------
    # Cadastro e popup
    # -------------------------
    def pop_up_new_ticket(self):
        pop_up_win = tk.Toplevel(self)
        pop_up_win.title('Novo Ticket')
        w, h = 320, 170

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        pop_up_win.geometry(f"{w}x{h}+{x}+{y}")
        pop_up_win.transient(self)
        pop_up_win.grab_set()

        ttk.Label(pop_up_win, text="Ativo (ex: PETR4):").pack(pady=(12, 5))
        ativo_entry = ttk.Entry(pop_up_win, justify="center")
        ativo_entry.pack(pady=2)

        def save():
            ativo = ativo_entry.get().strip().upper()
            if self.register_ticket(ativo):
                pop_up_win.destroy()
                messagebox.showinfo("Sucesso", f"{ativo} cadastrado com sucesso.")

        btn_frame = ttk.Frame(pop_up_win)
        btn_frame.pack(pady=12)
        ttk.Button(btn_frame, text="Salvar", command=save).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=pop_up_win.destroy).pack(side="left")

    def register_ticket(self, ticker: str) -> bool:
        if not ticker:
            messagebox.showwarning("Aviso", "Digite um Ativo.")
            return False

        ticker = ticker if ticker.upper().endswith(".SA") else f"{ticker.upper()}.SA"

        tickers = db.load_tickers()
        if ticker in tickers:
            messagebox.showinfo("Ativo já cadastrado", f"'{ticker}' já está cadastrado.")
            return False

        db.save_ticket(ticker)
        return True

    # -------------------------
    # Carregamento e busca
    # -------------------------
    def load_table(self, event=None):
        """Limpa tabela e dispara buscas concorrentes por cada ticker salvo no DB."""
        # limpa tabela
        for item in self.table.get_children():
            self.table.delete(item)

        tickers = db.load_tickers()
        if not tickers:
            messagebox.showinfo("Sem tickers", "Nenhum ticker cadastrado.")
            self.progress['value'] = 0
            self.progress['maximum'] = 0
            self.status_label.config(text="Pronto")
            return

        self.total_tickers = len(tickers)
        self.processed_tickers = 0
        self.progress['value'] = 0
        self.progress['maximum'] = self.total_tickers
        self.status_label.config(text=f"Processando 0/{self.total_tickers} tickers...")

        # submit tasks para executor
        for ticker in tickers:
            fut = self.executor.submit(self.search_worker, ticker)
            fut.add_done_callback(self._on_search_done)

    def _on_search_done(self, fut):
        """Callback (executado em thread do executor). Agendamos o tratamento no thread principal."""
        try:
            result = fut.result()
        except Exception as e:
            result = ("error", str(e), None)
        # schedule on main thread
        self.after(0, partial(self._process_result_on_main_thread, result))

    def search_worker(self, ticker: str) -> Tuple[str, dict | str | None]:
        """
        Executado em thread worker.
        Retorna uma tupla com status e dados:
         - ('ok', {...})
         - ('error', 'mensagem de erro')
        """
        try:
            tk_upper = ticker.upper()
            active = yf.Ticker(tk_upper)
            info = active.info or {}
            # tentativa de obter preço atual de forma segura
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            if price is None:
                raise ValueError("Preço não disponível")

            # dividendos do último ano (início definido pela UI)
            inicio = (date.today() - relativedelta(years=1)).replace(day=1)
            divs = getattr(active, "dividends", None)
            divs_ult12 = 0.0
            try:
                if divs is not None and not divs.empty:
                    # divs index may be DatetimeIndex; select by string slice
                    s = divs.loc[str(inicio):]
                    # se for Series, soma; se DataFrame, tenta coluna 0
                    divs_ult12 = float(s.tail(12).sum())
            except Exception:
                divs_ult12 = 0.0

            # calcula cotas com base no orçamento atual
            budget_value = parse_currency(self.budget.get(), default=0.0)
            cotas = 0
            proventos = 0.0
            if price and price > 0 and budget_value > 0:
                cotas = floor(budget_value / price)
                proventos = round(cotas * divs_ult12, 2)

            # decide tag
            if divs_ult12 > price * 0.05:  # exemplo: yield > 5% do preço (ajustável)
                tag = 'verde'
            elif divs_ult12 > 0:
                tag = 'amarelo'
            else:
                tag = 'vermelho'

            data = {
                "ticker": tk_upper.rstrip('.SA'),
                "price": price,
                "divs_ult12": round(divs_ult12, 4),
                "cotas": cotas,
                "proventos": proventos,
                "tag": tag,
            }
            return ("ok", data)
        except Exception as exc:
            return ("error", f"Erro buscando {ticker}: {exc}")

    def _process_result_on_main_thread(self, result):
        """Insere resultado na Treeview e atualiza progresso — executado no thread principal."""
        status = result[0]
        if status == "ok":
            data = result[1]
            self.table.insert('', 'end',
                              values=(
                                  data["ticker"],
                                  format_currency(data["price"]),
                                  format_currency(data["divs_ult12"]),
                                  data["cotas"],
                                  format_currency(data["proventos"])
                              ),
                              tags=(data["tag"],))
        else:
            # erro: adiciona linha com mensagem
            msg = result[1]
            self.table.insert('', 'end', values=("Erro", msg, "-", "-", "-"), tags=('vermelho',))

        # atualiza progresso
        self.processed_tickers += 1
        self.progress['value'] = self.processed_tickers
        self.status_label.config(text=f"Processando {self.processed_tickers}/{self.total_tickers} tickers...")
        if self.processed_tickers >= self.total_tickers:
            self.status_label.config(text="Concluído!")

# -------------------------
# Execução
# -------------------------
if __name__ == "__main__":
    app = PointerApp()
    app.mainloop()
