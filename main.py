import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
from PIL import ImageTk, Image, ImageDraw, ImageFont
from Grouper import Grouper
from ColorSelector import ColorSelector
import json
from DateSelcector import DateSelector
from datetime import datetime

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self._stage_number = 0
        self.create_widgets()
        self._data = None
        self._result_arr = None
        self._activities = None
        self._date_from = None
        self._date_to = None
        self._translator = dict()
        self._activity_color = dict()

    def create_widgets(self):
        self._stage = [[], [], []]

        load_button = tk.Button(self, text="load", command=self.load_data)
        self._stage[0].append(load_button)

        date_button = tk.Button(self, text="select dates",
                                command=self.select_dates)
        self._stage[1].append(date_button)

        group_button = tk.Button(self, text="group",
                                 command=self._group)
        self._stage[1].append(group_button)

        save_grouping_button = tk.Button(self, text="save grouping",
                                         command=self._save_grouping)
        self._stage[1].append(save_grouping_button)

        load_grouping_button = tk.Button(self, text="load grouping",
                                         command=self._load_grouping)
        self._stage[1].append(load_grouping_button)

        coloring_button = tk.Button(self, text="pick colors",
                                    command=self._create_color_selector)
        self._stage[2].append(coloring_button)

        save_coloring_button = tk.Button(self, text="save coloring",
                                         command=self._save_colors)
        self._stage[2].append(save_coloring_button)

        load_coloring_button = tk.Button(self, text="load coloring",
                                         command=self._load_colors)
        self._stage[2].append(load_coloring_button)

        show_button = tk.Button(self, text="show",
                                command=self._show)
        self._stage[2].append(show_button)

        for b in self._stage[0]:
            b.pack()

        frame = tk.Frame(self)

        previous_button = tk.Button(frame, text="Previous", command=self._prev_stage)
        previous_button.pack(side="left")

        next_button = tk.Button(frame, text="Next", command=self._next_stage)
        next_button.pack(side="right")

        quit_button = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        quit_button.pack(side="bottom")
        frame.pack(side="bottom")

    def select_dates(self):
        date_to = tk.StringVar()
        date_from = tk.StringVar()


        def set_to(*args):
            self._date_to = pd.Timestamp(date_to.get())
            self._date_to = self._date_to.replace(hour=23, minute=59, second=59)

        def set_from(*args):
            self._date_from = pd.Timestamp(date_from.get())

        date_to.trace("w", callback=set_to)
        date_from.trace("w", callback=set_from)

        DateSelector(date_to, date_from)

    def load_data(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select file",
                                     filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        data = pd.read_csv(filename, usecols=[0, 2, 3])
        data.dropna(axis=0, inplace=True)
        data["From"] = pd.to_datetime(data["From"])
        data["To"] = pd.to_datetime(data["To"])
        data.rename(columns={"Activity type": "Type"}, inplace=True)
        data = data[data["From"] != data["To"]]  # removing entries with no duration time
        data = data.iloc[::-1]  # reversing so last logs will be at the end
        self._date_from = pd.Timestamp(min(data["From"]).date())
        self._date_to = pd.Timestamp(max(data["To"]).date())
        self._data = self._prepare(data)
        self._activities = pd.unique(self._data["Type"])

    def _create_color_selector(self): #TODO autimatic color picking at stage 2
        result = tk.StringVar()
        def callback(*args):
            self._activity_color = json.loads(result.get())

        result.trace("w", callback=callback)
        master_activities = set(self._activities) - set(self._translator.keys())
        ColorSelector(result, master_activities)

    def _prepare(self, data):
        bad_idx = data.iloc[1:]["From"].values < data.iloc[:-1]["To"].values  # overlapping entries
        first = True
        while first or pd.unique(bad_idx).shape != (1,):
            first = False
            data.iloc[1:].loc[bad_idx, "From"] = data.iloc[bad_idx]["To"].values
            data = data[data["From"] < data["To"]]
            bad_idx = data.iloc[1:]["From"].values < data.iloc[:-1]["To"].values
        return data

    def _draw(self):
        activity_color = self._activity_color
        fr = self._data["From"].iloc[0]
        to = self._data["To"].iloc[-1]
        dif = to - fr
        days = dif.days + 1
        margin = 200  # 200 - space for color legend
        width = 24 * 60 + margin
        result = np.zeros(shape=(days, width, 3), dtype='uint8')
        first_day = self._data["From"].iloc[0].date()
        for idx, row in self._data.iterrows():
            day_idx = (row["From"].date() - first_day).days
            from_idx = row["From"].minute + row["From"].hour * 60
            to_idx = row["To"].minute + row["To"].hour * 60
            if row["Type"] in self._translator.keys():
                activity = self._translator[row["Type"]]
            else:
                activity = row["Type"]
            if to_idx < from_idx:
                result[day_idx, from_idx:width - margin, :] = activity_color[activity]
                day_idx += 1
                if (day_idx < result.shape[0]):
                    result[day_idx, 0:to_idx, :] = activity_color[activity]
            else:
                if (day_idx < result.shape[0]):
                    result[day_idx, from_idx:to_idx, :] = activity_color[activity]

        times = int((0.8 * result.shape[1]) // (result.shape[0]))
        print(times, result.shape)
        if times < 1:
            times = 1
        self._result_arr = self._lenghten(result, times)

    def _show(self): #TODO result should be scrollable
        idx1 = self._data["From"] >= self._date_from
        idx2 = self._data["To"] <= self._date_to
        self._data = self._data[np.logical_and(idx1, idx2)]
        self._activities = pd.unique(self._data["Type"])
        self._draw()
        if self._result_arr is not None:
          #  matImage.imsave("./dio.png", self._result_arr/256)
            img = Image.fromarray(self._result_arr, "RGB")
            img = self._add_legend(img)
            img.save("i like trains.jpg")
            self.photo = ImageTk.PhotoImage(image=img)
            w = self._result_arr.shape[1]
            h = self._result_arr.shape[0]
            canvas = tk.Canvas(self, width=w, height=h)
            canvas.pack()
            canvas.create_image(0, 0, image=self.photo, anchor="nw")

    def _add_legend(self, image):
        activity_color = self._activity_color
        draw = ImageDraw.Draw(image)
        for i, (activity, color) in enumerate(activity_color.items()):
            fnt = ImageFont.truetype("arial.ttf", size=10)
            w0 = 24*60
            yh = 15
            draw.text((w0+30, i*yh), activity, fint=fnt)
            rec_pos = ((w0+10, i*15), ((w0+20, i*15 + 10)))
            color = tuple(int(c) for c in color )
            draw.rectangle(rec_pos, fill=color)
        return image

    def _lenghten(self, array, times: int):
        assert type(times) is int
        shape = array.shape
        shape = (shape[0] * times,) + shape[1:]
        resized = np.zeros(shape, dtype="uint8")
        for idx, row in enumerate(array):
            idx *= times
            resized[idx:idx + times] = row
        return resized

    def _load_colors(self):
        with open('coloring.json', 'r') as f:
            jcolors = f.read()
        self._activity_color = json.loads(jcolors)

    def _save_colors(self):
        jcolors = json.dumps(self._activity_color)
        with open("coloring.json", "w") as f:
            f.write(jcolors)

    def _load_grouping(self):
        with open('grouping.json', 'r') as f:
            jtrans = f.read()
        self._translator = json.loads(jtrans)

    def _save_grouping(self):
        jtrans = json.dumps(self._translator)
        with open("grouping.json", "w") as f:
            f.write(jtrans)

    def _group(self):
        result = tk.Variable()
        def callback(*args):
            master_activity = result.get()[0]
            for sub_activity in result.get()[1]:
                self._translator[sub_activity] = master_activity
        result.trace("w", callback=callback)
        sub_activities = set(a for a in self._translator.keys())
        master_activities = set(a for a in self._translator.values())
        Grouper(self._activities , result, omit_master=sub_activities, omit_sub=master_activities)

    def _change_stage(self, diff):
        if 0 <= self._stage_number + diff < len(self._stage):
            for w in self._stage[self._stage_number]:
                w.pack_forget()
            self._stage_number = self._stage_number + diff
            for w in self._stage[self._stage_number]:
                w.pack()

    def _next_stage(self):
        self._change_stage(1)

    def _prev_stage(self):
        self._change_stage(-1)

    #TODO add last stage with result and saving


if __name__=="__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()