from tkinter import Menu
from source import (
    data_base as db, utils as utl
)
from source.ui import frame

def app():

    db.db_init()

    win = utl.Window()

    top_menu = Menu(win)

    config_cascade = Menu(top_menu, tearoff=False)
    top_menu.add_cascade(label='Sistema', menu=config_cascade)

    top_menu.add_command(
        label='Pointer',
        command=lambda: win.show_frame(frame.Pointer_consult(win)),
    )
    config_cascade.add_command(
        label='Configure', command=lambda: win.show_frame(frame.Config(win))
    )

    win.config(menu=top_menu)

    win.mainloop()
