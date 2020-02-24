import tkinter as tk

class Grouper():
    def __init__(self, activities, result_var, omit_sub, omit_master):
        self.result = result_var
        self.window = tk.Toplevel()
        self.button_holder = tk.Frame(self.window)
        self.button_holder.pack()
        self.master_activity = None
        self.slaves = []
        self.activities = activities
        self.omit = omit_sub | omit_master
        for activity in activities:
            if activity in omit_master: continue
            b = tk.Button(self.button_holder, text=activity, command=self.select_creator(activity))
            b.pack()

    def select_creator(self, name):
        def f():
            self.master_activity = name
            self.button_holder.destroy()
            self.second_stage()
        return f

    def second_stage(self):
        self.vars = []

        def create_callback(name):
            def f(*args):
                if name in self.slaves:
                    self.slaves.remove(name)
                else:
                    self.slaves.append(name)
            return f

        for activity in self.activities:
            if activity == self.master_activity or activity in self.omit: continue
            v = tk.BooleanVar()
            v.trace("w", create_callback(activity))
            self.vars.append(v)
            c = tk.Checkbutton(self.window, text=activity, variable=v)
            c.pack()
        b = tk.Button(self.window, text="end", command=self.end)
        b.pack()

    def end(self):
        self.result.set((self.master_activity, self.slaves))
        self.window.destroy()
