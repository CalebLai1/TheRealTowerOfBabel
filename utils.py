# utils.py
def show_progress_bar(gui):
    gui.progress_bar.grid()
    gui.progress_var.set(0)
    gui.root.update_idletasks()

def hide_progress_bar(gui):
    gui.progress_bar.grid_remove()
    gui.progress_var.set(0)
    gui.root.update_idletasks()

def update_progress_bar(gui, percent):
    gui.progress_var.set(percent)
    gui.root.update_idletasks()
