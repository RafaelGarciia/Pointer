import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Literal

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
    pop_up.geometry(f'{pop_w}x{pop_h}+{x}+{y}')


# String para a moeda Real br
class RealString(tk.StringVar):
    def __init__(self, master=None, value='0,0', *kwargs):
        super().__init__(master)

        self.integer, self.decimal = 0, 0

        self._set(str(value))

    def _set(self, value: int | float):
        if str(value).isdigit():
            value = int(value)
        else:
            value = str(value).replace('.', '')
            value = str(value).replace(',', '.')
            try:
                value = float(value)
            except:
                print('erro')

        self.integer, self.decimal = f'{value:.2f}'.split('.')
        f_value = f'{int(self.integer):,}'.replace(',', '.')
        self.set(f'{f_value},{self.decimal}')

    def _get(self):
        return float(f'{self.integer}.{self.decimal}')


class Window(tk.Tk):
    width: int   # Largura da janela principal
    height: int   # Autura da janela principal
    container: tk.Frame   # Frame exibido

    def __init__(
        self, width: int = 600, height: int = 600, title: str = 'Window'
    ):
        super().__init__()

        # Armazena um frame vazio para não dar bug
        self.container = tk.Frame(self)
        self.container.pack()

        # Armazena as dimenções da janela
        self.width = width
        self.height = height

        self.title(title)   # Titulo da janela
        self.geometry(
            f'{width}x{height}'
        )   # Defini o tamanho
        self.resizable(False, False)
        center_win_on_screen(self)   # Centraliza a janela na tela

    def show_frame(self, frame):
        self.container.pack_forget()
        self.container = frame
        self.container.pack(side='top', fill='both', expand=True)


class Pop_Up(tk.Toplevel):
    width: int   # Largura da janela pop up
    height: int   # Autura da janela pop up

    def __init__(self, window: tk.Tk, title='Pop UP', width: int = 200, height: int = 100):
        super().__init__(window)
        
        # Seta o titulo da janela pop up
        self.title(title)

        # Armazena as dimenções da janela pop up
        self.width = width
        self.height = height

        # Atualiza a janela
        window.update_idletasks()

        self.geometry(f'{width}x{height}')   # Defini o tamanho
        center_pop_up(self, window)
        self.transient(window)
        self.resizable(False, False)
        self.grab_set()


class Label_entry:
    top_label: bool  # variavel que define se a label sera exibina em cima da entry ou do lado

    def __init__(
        self,
        master: tk.Tk | tk.Frame | tk.Toplevel,
        label: str = 'label',
        width: int = 20,
        justify: Literal['left', 'center', 'right'] = "left",
        state: str = "normal",
        textvariable: tk.Variable | None = None,
        top_label: bool = False 
    ) -> None:
        
        self.top_label = top_label # Passa o argumento para a variavel do objeto

        # Instancia os widgets
        self.frame = ttk.Frame(master)
        self.label = ttk.Label(self.frame, text=label)
        self.entry = ttk.Entry(self.frame, width=width, justify=justify, state=state, textvariable=textvariable)

    def get(self) -> str|int|float:
        # Retorna o valor do widget entry
        return self.entry.get()
    
    def set(self, value: str | int | float) -> None:
        self.entry.delete(0, tk.END) # Deleta oque esta na entry
        self.entry.insert(0, value) # Inseri o novo valor na entry

    def pack(self,
        padx: int | float | str | tuple[float | str, float | str] = 0,
        pady: int | float | str | tuple[float | str, float | str] = 0,
        ipadx: float | str = 0,
        ipady: float | str = 0,
        anchor: Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw', 's', 'se'] = 'center',
        side: Literal['left', 'right', 'top', 'bottom'] = 'left',
        expand: bool | Literal[0, 1] = 0,
        fill: Literal['none', 'x', 'y', 'both'] = 'none',
    ) -> None:
        # Da pack na label, se o parametro top label for True, ele da pack em cima da entry, se não, da pack na esquerda da entry
        self.label.pack(side='top' if self.top_label else 'left')
        self.entry.pack(side='left')
        self.frame.pack(padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, anchor=anchor, side=side, expand=expand, fill=fill)

    def set_focus(self) -> None:
        # Seta o foco na entry
        self.entry.focus_set()
    
    def entry_bind(self, key: Literal['Button1','Double-Button-1', 'Button2','Double-Button-1', 'Any_key', 'Return', 'Motion']|str, func: object) -> None:
        self.entry.bind(f'<{key}>', func)


class Table(ttk.Treeview):
    def __init__(self, window: tk.Frame, columns: list):
        super().__init__(window)

        self.sorting_order = {col: True for col in columns}

        self.config(columns=columns, show='headings', height=18)
        for col in columns:
            self.heading(col, text=col, command=lambda: self.sort_column(col))
            self.column(col, width=100, anchor='center')

        # Color Tags
        self.tag_configure('azul', background="#b5dbff")
        self.tag_configure('verde', background='#d4fcdc')
        self.tag_configure('amarelo', background='#fffacd')
        self.tag_configure('vermelho', background='#fcdcdc')
        
        # Scrollbar
        v_scrollbar = ttk.Scrollbar(window, orient='vertical', command=self.yview)
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

    def clear_table(self) -> None:
        # Limpa a tabela
        for item in self.get_children():
            self.delete(item)


class ProgressBar(ttk.Frame):
    def __init__(self,
        master = None,
        length = 400,
        mode: Literal['determinate', 'indeterminate'] = 'determinate',
        status_label:str = 'Progress Bar'
    ):
        super().__init__(master)

        self.bar = ttk.Progressbar(self, length=length, mode=mode)
        self.bar.pack()

        self.status_label = ttk.Label(self, text=status_label)
        self.bar.pack(side='left', padx=5)
        self.status_label.pack(side='left', padx=5)

    def progress(self):
        self.bar['value'] = self.bar['value'] + 1
        
        if self.bar['value'] >= self.bar['maximum']:
            self.status_label.config(text='Concluido!')
        else:
            self.status_label.config(text=f'{self.bar['value']}/{self.bar['maximum']}')
        

def parse_date_br(date_str:str):
    """
    Recebe dd/mm/yyyy e retorna ISO yyyy-mm-dd.
    """
    try:
        dt = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        return dt.date().isoformat()
    except Exception as ex:
        raise ValueError('Data inválida. Use dd/mm/aaaa (ex: 25/10/2000).')
    
def iso_to_br(date_iso):
    try:
        dt = datetime.strptime(date_iso, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except:
        return date_iso
    