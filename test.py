"""from tkinter import *

LEFT = 37
UP = 38
RIGHT= 39
DOWN = 40

w = Tk()
c = Canvas(w, width=400, height=300)
c.pack(fill=BOTH, expand=True)

img = PhotoImage(file="assets/mage_bleu_droite.png")
mage = c.create_image(50, 50, image=img)

def move(evt: Event):
    if evt.keycode == RIGHT:
        c.move(mage, 10, 0)

w.bind("<KeyRelease>", move)

w.mainloop()
"""

from tkinter import ttk
import tkinter as tk

window = tk.Tk()
style = ttk.Style(window)
style.theme_use('vista')

btn = ttk.Button(window, text="Hello")
btn.pack()

window.mainloop()