import tkinter as tk
from tkSliderWidget import Slider

root = tk.Tk()

slider = Slider(root, width = 400, height = 60, min_val = 1, max_val = 96, init_lis = [1,96], show_value = True)
slider.pack()

# optionally add a callback on value change
slider.setValueChangeCallback(lambda vals: print(vals))

root.title("Slider Widget")
root.mainloop()

print(slider.getValues())
