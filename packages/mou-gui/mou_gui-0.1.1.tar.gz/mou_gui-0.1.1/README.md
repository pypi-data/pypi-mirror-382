# MOU GUI Toolkit

**MOU (Modern UI)** is a lightweight, cross-platform Python GUI toolkit built on `tkinter`.
It provides easy-to-use widgets like labels, buttons, sliders, trees, lists, tabs, and more — perfect for building modern-looking Python applications quickly.

---

## ✨ Features

* Labels, Buttons, Checkboxes, Radio Buttons
* Sliders, Entry, Combobox
* Progress Bars, Lists, Trees
* Tabs / Notebook support
* Simple and consistent API for all widgets
* Works on **Windows, macOS, Linux**

---

## 🚀 Installation

Install using pip:

```bash
pip install mou-gui
```

Install directly from source:

```bash
git clone https://github.com/LightingDev/mou-gui.git
cd mou-gui
pip install .
```

For development (editable install):

```bash
pip install -e .
```

> Now you can `import mou` in your Python scripts!

---

## 📝 Quick Tutorial

```python
from mou import (
    MOUApp, MLabel, MButton, MSlider, MCheckbox,
    MRadioGroup, MEntry, MCombobox, MProgressBar,
    MList, MTree, MTabs
)

# Create the app
app = MOUApp(title="MOU Demo", width=800, height=600)

# Tabs for better organization
tabs = MTabs(app.root)
pack_tab = tabs.add_tab("Pack Layout")
place_tab = tabs.add_tab("Place Layout")

# ------------------------
# Pack-based widgets
# ------------------------
label1 = MLabel(pack_tab, "Pack Widgets Example")
button1 = MButton(pack_tab, "Click Me", lambda: label1.set_text("Clicked!"))
slider1 = MSlider(pack_tab)
checkbox1 = MCheckbox(pack_tab, "Check me!")
radios1 = MRadioGroup(pack_tab, ["Option 1", "Option 2"])
entry1 = MEntry(pack_tab)
combo1 = MCombobox(pack_tab, ["Choice A", "Choice B"])
progress1 = MProgressBar(pack_tab)
progress1.set_value(30)
listbox1 = MList(pack_tab, ["Item 1", "Item 2"])
tree1 = MTree(pack_tab, columns=["Name", "Age"], data=[("Alice", 25), ("Bob", 30)])

# ------------------------
# Place-based widgets
# ------------------------
label2 = MLabel(place_tab, "Place Widgets Example", x=20, y=20)
button2 = MButton(place_tab, "Click Me Too", lambda: label2.set_text("Clicked!"), x=20, y=50)
slider2 = MSlider(place_tab, x=20, y=90)
checkbox2 = MCheckbox(place_tab, "Check me too!", x=20, y=130)
radios2 = MRadioGroup(place_tab, ["A", "B", "C"], x=20, y=170)
entry2 = MEntry(place_tab, x=20, y=250)
combo2 = MCombobox(place_tab, ["X", "Y", "Z"], x=20, y=280)
progress2 = MProgressBar(place_tab, x=20, y=320)
progress2.set_value(70)
listbox2 = MList(place_tab, ["Item A", "Item B"], x=250, y=20)
tree2 = MTree(place_tab, columns=["Item", "Qty"], data=[("Apple", 10), ("Banana", 20)], x=250, y=200)

# ------------------------
# Run the app
# ------------------------
app.run()
```

* Create an `MOUApp` instance
* Add widgets like `MLabel`, `MButton`, `MSlider`
* Call `app.run()` to start the GUI

---

## 🛠️ Templates

You can quickly create apps using these templates:

```python
# templates/simple_app.py
from mou import MOUApp, MLabel, MButton

app = MOUApp(title="Simple Template")
MLabel(app.root, "Hello Template!")
MButton(app.root, "Click Me", lambda: print("Clicked!"))
app.run()
```

---

## 🤝 Contributing

1. Fork the repository
2. Install MOU from source (`pip install -e .`)
3. Add your widgets, templates, or improvements
4. Open a Pull Request

---

## 📜 License

apache-2.0 License — free to use, modify, and distribute.

---
