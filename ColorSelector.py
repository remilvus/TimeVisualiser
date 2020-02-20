from random import randint
import tkinter as tk
from tkinter import colorchooser
import json

def rand_color():
    return (randint(0,255),randint(0,255),randint(0,255))

class ColorSelector(tk.Toplevel):
    def __init__(self, result, activities):
        super().__init__()
      #  super().__init__(master, bg="green")
       # self.master = master
    #    self.pack()
        self.result = result
        self.activity_color = dict()
        self._activity_label = dict()
        for i, activity in enumerate(activities):
            b = tk.Button(self, text=activity, command=self._color_setter(activity))
            b.grid(row=i, column=0)
            col = rand_color() #(0, 0, 0)
            label = tk.Label(self, width=10, bg='#%02x%02x%02x' % col)
            label.grid(row=i, column=1)
            self._activity_label[activity] = label
            self.activity_color[activity] = col #(0, 0, 0)
        self.result.set(json.dumps(self.activity_color))


    def _color_setter(self, name):
        def f():
            color = colorchooser.askcolor()
            self.activity_color[name] = color[0]  # 0-rgb, 1-hex
            self._activity_label[name].config(bg=color[1])
            self.result.set(json.dumps(self.activity_color))
        return f
