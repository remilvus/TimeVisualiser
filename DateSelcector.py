import tkinter as tk
import tkcalendar

class DateSelector(tk.Toplevel):
    def __init__(self, date_from, date_to):
        super().__init__()
        self._date_to = date_to
        self._date_from = date_from
        label = tk.Label(self, text="From")
        label.pack()
        self._cal_from = tkcalendar.DateEntry(self)
        self._cal_from.pack()
        label = tk.Label(self, text="To")
        label.pack()
        self._cal_to = tkcalendar.DateEntry(self)
        self._cal_to.pack()
        b = tk.Button(self, text="Confirm", command=self._confirm)
        b.pack()

    def _confirm(self):
        d_from = self._cal_from.get_date()
        d_to = self._cal_to.get_date()
        if d_from <= d_to:
            self._date_from.set(str(d_from))
            self._date_to.set(str(d_to))
            self.destroy()
        else:
            l = tk.Label(self, text="'date from' is after 'date to'")
            l.pack()