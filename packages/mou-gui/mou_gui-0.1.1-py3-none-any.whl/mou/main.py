import tkinter as tk
from tkinter import ttk

# ------------------------
# Base Widget
# ------------------------
class Widget:
    def __init__(self, master, x=None, y=None):
        self.master = master
        self.x = x
        self.y = y

    def _place_or_pack(self, widget):
        if self.x is not None and self.y is not None:
            widget.place(x=self.x, y=self.y)
        else:
            widget.pack(pady=5)

# ------------------------
# Labels
# ------------------------
class MLabel(Widget):
    def __init__(self, master, text, x=None, y=None):
        super().__init__(master, x, y)
        self.label = ttk.Label(master, text=text)
        self._place_or_pack(self.label)

    def set_text(self, text):
        self.label.config(text=text)

# ------------------------
# Buttons
# ------------------------
class MButton(Widget):
    def __init__(self, master, text, command, x=None, y=None):
        super().__init__(master, x, y)
        self.button = ttk.Button(master, text=text, command=command)
        self._place_or_pack(self.button)

# ------------------------
# Checkboxes
# ------------------------
class MCheckbox(Widget):
    def __init__(self, master, text, x=None, y=None):
        super().__init__(master, x, y)
        self.var = tk.IntVar()
        self.checkbox = ttk.Checkbutton(master, text=text, variable=self.var)
        self._place_or_pack(self.checkbox)

    def is_checked(self):
        return self.var.get() == 1

# ------------------------
# Radio Buttons
# ------------------------
class MRadioGroup(Widget):
    def __init__(self, master, options, x=None, y=None):
        super().__init__(master, x, y)
        self.var = tk.StringVar()
        self.buttons = []
        for opt in options:
            rb = ttk.Radiobutton(master, text=opt, value=opt, variable=self.var)
            if x is not None and y is not None:
                rb.place(x=x, y=y)
                y += 25  # stack vertically when using place
            else:
                rb.pack(anchor="w")
            self.buttons.append(rb)

    def get_value(self):
        return self.var.get()

# ------------------------
# Slider
# ------------------------
class MSlider(Widget):
    def __init__(self, master, from_=0, to=100, orient='horizontal', command=None, x=None, y=None):
        super().__init__(master, x, y)
        self.scale = ttk.Scale(master, from_=from_, to=to, orient=orient, command=command)
        self._place_or_pack(self.scale)

    def get_value(self):
        return self.scale.get()

# ------------------------
# Entry
# ------------------------
class MEntry(Widget):
    def __init__(self, master, x=None, y=None):
        super().__init__(master, x, y)
        self.entry = ttk.Entry(master)
        self._place_or_pack(self.entry)

    def get_text(self):
        return self.entry.get()

# ------------------------
# Combobox
# ------------------------
class MCombobox(Widget):
    def __init__(self, master, values, x=None, y=None):
        super().__init__(master, x, y)
        self.combobox = ttk.Combobox(master, values=values)
        self._place_or_pack(self.combobox)

    def get_value(self):
        return self.combobox.get()

# ------------------------
# Progress Bar
# ------------------------
class MProgressBar(Widget):
    def __init__(self, master, length=200, mode='determinate', x=None, y=None):
        super().__init__(master, x, y)
        self.progress = ttk.Progressbar(master, length=length, mode=mode)
        self._place_or_pack(self.progress)

    def set_value(self, value):
        self.progress['value'] = value

# ------------------------
# Listbox
# ------------------------
class MList(Widget):
    def __init__(self, master, items, x=None, y=None):
        super().__init__(master, x, y)
        self.listbox = tk.Listbox(master)
        for item in items:
            self.listbox.insert(tk.END, item)
        self._place_or_pack(self.listbox)

    def get_selected(self):
        return [self.listbox.get(i) for i in self.listbox.curselection()]

# ------------------------
# Tree
# ------------------------
class MTree(Widget):
    def __init__(self, master, columns, data, x=None, y=None):
        super().__init__(master, x, y)
        self.tree = ttk.Treeview(master, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
        for row in data:
            self.tree.insert("", tk.END, values=row)
        self._place_or_pack(self.tree)

    def get_selected(self):
        return self.tree.selection()

# ------------------------
# Tabs
# ------------------------
class MTabs(Widget):
    def __init__(self, master, x=None, y=None):
        super().__init__(master, x, y)
        self.notebook = ttk.Notebook(master)
        if x is not None and y is not None:
            self.notebook.place(x=x, y=y, width=400, height=300)
        else:
            self.notebook.pack(expand=True, fill='both')
        self.tabs = {}

    def add_tab(self, name):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        self.tabs[name] = frame
        return frame

# ------------------------
# App Class
# ------------------------
class MOUApp:
    def __init__(self, width=600, height=400, title="MOU App"):
        self.root = tk.Tk()
        self.root.geometry(f"{width}x{height}")
        self.root.title(title)
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def run(self):
        self.root.mainloop()
