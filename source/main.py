from tkinter import Menu
from source.ui import utils as utl
from source.ui import frame



def app():


    win = utl.Window()


    top_menu = Menu(win)
    top_menu.add_command(label='Pointer' ,command=lambda: win.show_frame(frame.Pointer_consult(win)))
    top_menu.add_command(label='Configure', command=lambda: win.show_frame(frame.Config(win)))


    win.config(menu=top_menu)



    win.mainloop()




