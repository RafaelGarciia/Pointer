import tkinter as tk
from tkinter import ttk

def center_win_on_screen(win: tk.Tk) -> None:
    """Centraliza a janela na tela"""

    win.update_idletasks()   # Atualiza a janela

    w = win.winfo_width()  # Placeholder para a largura da janela
    h = win.winfo_height()   # Placeholder para a altura da janela

    screen_w = win.winfo_screenwidth()  # Placeholder para a largura da tela
    screen_h = win.winfo_screenheight()   # Placeholder para a altura da tela

    # Calcula o centro da tela no eixo X
    x = (screen_w // 2) - (w // 2)

    # Calcula o centro da tela no eixo y
    y = (screen_h // 2) - (h // 2)

    # Seta a posição e o tamanho da janela
    win.geometry(f'{w}x{h}+{x}+{y}')


def center_pop_up(pop_up: tk.Toplevel, win: tk.Tk) -> None:
    """Centraliza a janela pop up (Toplevel) na janela principal"""

    win.update_idletasks()   # Atualiza a janela

    pop_w = pop_up.winfo_width()   # Placeholder para a largura do toplevel
    pop_h = pop_up.winfo_height()   # Placeholder para a altura do toplevel

    win_w = win.winfo_width()  # Placeholder para a largura da janela principal
    win_h = win.winfo_height()  # Placeholder para a altura da jenela principal

    # Calcula o centro da janela no eixo X
    x = win.winfo_x() + (win_w // 2) - (pop_w // 2)

    # Calcula o centro da janela no eixo Y
    y = win.winfo_y() + (win_h // 2) - (pop_h // 2)

    # Seta a posição e o tamanho do toplevel
    win.geometry(f'{pop_w}x{pop_h}+{x}+{y}')

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


class Window(tk.Tk):
    win_width: int   # Largura da janela principal
    win_height: int   # Autura da janela principal
    container:tk.Frame # Frame exibido

    def __init__(
        self,
        width: int = 600,
        height: int = 600,
        title: str = 'Window'
    ):
        super().__init__()

        # Armazena um frame vazio para não dar bug
        self.container = tk.Frame(self)
        self.container.pack()

        # Armazena as dimenções da janela
        self.win_width = width
        self.win_height = height

        self.title(title) # Titulo da janela
        self.geometry(f'{self.win_width}x{self.win_height}') # Defini o tamanho
        center_win_on_screen(self) # Centraliza a janela na tela

    def show_frame(self, frame):
        self.container.pack_forget()
        self.container = frame
        self.container.pack(side="top", fill="both", expand=True)


class Pop_Up(tk.Toplevel):
    width:int = 200
    height:int = 100

    def __init__(self, window:tk.Tk, title = 'Pop UP'):
        super().__init__(window)
        self.title(title)

        # Atualiza a janela
        window.update_idletasks()

        self.geometry(f'{self.width}x{self.height}') # Defini o tamanho
        center_pop_up(self, window)
        self.transient(window)
        self.resizable(False, False)
        self.grab_set()


class Label_entry(ttk.Frame):
    def __init__(self, window:tk.Tk = None, label:str = 'label', text_var:tk.Variable = None, entry_width:int = 5, justify = 'left'):
        super().__init__(window)

        self.label = ttk.Label(self, text=label)
        self.entry = ttk.Entry(self, textvariable=text_var, width=entry_width, justify=justify)


        self.label.pack(side='left')
        self.entry.pack(side='left')


class Table(ttk.Treeview):
    def __init__(self, window: tk.Frame, columns: list):
        super().__init__(window)

        self.sorting_order = {col: True for col in columns}

        self.config(columns=columns, show='headings', height=18)
        for col in columns:
            self.heading(col, text=col, command=lambda: self.sort_column(col))
            self.column(col, width=100, anchor='center')

        # Color Tags
        self.tag_configure('verde', background='#d4fcdc')
        self.tag_configure('amarelo', background='#fffacd')
        self.tag_configure('vermelho', background='#fcdcdc')

        # Scrollbar
        v_scrollbar = ttk.Scrollbar(
            window, orient='vertical', command=self.yview
        )
        self.configure(yscrollcommand=v_scrollbar.set)
        self.pack(expand=True, fill='both', side='left')
        v_scrollbar.pack(fill='y', side='left')

    def sort_column(self, col: str):
        """Ordena a coluna do Treeview.
        Tenta ordenar numericamente quando possivel.
        """
        children = self.get_children('')
        data = [(self.set(k, col), k) for k in children]
        try:
            # Tenta utilizar como float
            data.sort(
                key=lambda t: float(str(t[0]).replace(',', '.')),
                reverse=not self.sorting_order[col],
            )
        except Exception:
            # Caso não utiliza str
            data.sort(
                key=lambda t: str(t[0]), reverse=not self.sorting_order[col]
            )

        for index, (_, k) in enumerate(data):
            self.move(k, '', index)
        self.sorting_order[col] = not self.sorting_order[col]
