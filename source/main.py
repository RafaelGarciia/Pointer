from tkinter import Menu
from source.ui import utils as utl
from source.ui import frame
from source import data_base


def app():

    data_base.db_init()

    win = utl.Window()

    top_menu = Menu(win)

    config_cascade = Menu(top_menu, tearoff=False)
    top_menu.add_cascade(label='Sistema', menu=config_cascade)

    top_menu.add_command(
        label='Pointer',
        command=lambda: show_frame_if_not_current(win, frame.Pointer_consult), 
    )
    config_cascade.add_command(
        label='Configure', command=lambda: win.show_frame(frame.Config(win))
    )

    win.config(menu=top_menu)

    win.mainloop()


def show_frame_if_not_current(win:utl.Window, frame_class):
    if not isinstance(win.container, frame_class):
        win.show_frame(frame_class(win))