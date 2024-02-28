import tkinter as tk

class CrosswordSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Crossword Simulator")

        self.current_box_index = 0
        self.entry_boxes = []
        self.clue = "PYTHON"  # Change the clue word as needed

        self.create_entry_boxes()
        self.create_enter_button()
        self.create_result_textbox()
        self.root.bind("<Key>", self.handle_key_press)
        self.root.bind("<BackSpace>", self.handle_backspace)
        self.root.bind("<Delete>", self.handle_delete)
        self.root.bind("<Return>", self.handle_enter)
        self.root.bind("<Left>", self.shift_left)
        self.root.bind("<Right>", self.shift_right)

    def create_entry_boxes(self):
        for i in range(len(self.clue)):
            box_frame = tk.Frame(self.root, bg='black', borderwidth=0, relief='solid', highlightbackground='black', highlightthickness=4)
            box_frame.grid(row=0, column=i, padx=1, pady=2)

            box = tk.Entry(box_frame, width=2, justify='center', font=('Arial', 24, 'bold'))
            box.pack(side='top', fill='both', expand=True)
            box.config(state='readonly')  # Set boxes to read-only by default

            self.entry_boxes.append({"frame": box_frame, "entry": box})

    def create_enter_button(self):
        enter_button = tk.Button(self.root, text="Enter", command=self.check_answer)
        enter_button.grid(row=1, column=0, columnspan=len(self.clue), pady=10)

    def create_result_textbox(self):
        self.result_textbox = tk.Text(self.root, height=2, width=30, state='disabled', font=('Arial', 12))
        self.result_textbox.grid(row=2, column=0, columnspan=len(self.clue), pady=10)

    def handle_key_press(self, event):
        key = event.char.upper()

        if key.isalpha() and self.current_box_index < len(self.entry_boxes):
            self.reset_background_color()  # Reset background color for all boxes
            self.entry_boxes[self.current_box_index]["entry"].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index]["entry"].delete(0, tk.END)  # Clear existing text
            self.entry_boxes[self.current_box_index]["entry"].insert(0, key)
            self.current_box_index += 1

            if self.current_box_index < len(self.entry_boxes):
                self.entry_boxes[self.current_box_index]["entry"].focus()
                self.set_background_color()  # Set background color for the currently selected box

            self.entry_boxes[self.current_box_index - 1]["entry"].config(state='readonly')  # Change back to read-only

    def handle_backspace(self, event):
        if self.current_box_index > 0:
            self.current_box_index -= 1
            self.reset_background_color()  # Reset background color for all boxes
            self.entry_boxes[self.current_box_index]["entry"].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index]["entry"].delete(0, tk.END)
            self.entry_boxes[self.current_box_index]["entry"].focus()
            self.set_background_color()  # Set background color for the currently selected box
            self.entry_boxes[self.current_box_index]["entry"].config(state='readonly')  # Change back to read-only

    def handle_delete(self, event):
        # Handle the Delete key separately
        if self.current_box_index < len(self.entry_boxes):
            self.reset_background_color()  # Reset background color for all boxes
            self.entry_boxes[self.current_box_index]["entry"].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index]["entry"].delete(0, tk.END)
            self.set_background_color()  # Set background color for the currently selected box
            self.entry_boxes[self.current_box_index]["entry"].config(state='readonly')  # Change back to read-only

    def handle_enter(self, event):
        self.check_answer()

    def check_answer(self):
        entered_string = ''.join(entry["entry"].get() for entry in self.entry_boxes)
        if entered_string == self.clue:
            result_message = "Congratulations! You solved the puzzle!"
        else:
            result_message = "Sorry, try again."

        self.result_textbox.config(state='normal')
        self.result_textbox.delete(1.0, tk.END)
        self.result_textbox.insert(tk.END, result_message)
        self.result_textbox.config(state='disabled')

    def shift_left(self, event):
        if self.current_box_index > 0:
            self.reset_background_color()  # Reset background color for all boxes
            self.current_box_index -= 1
            self.set_background_color()  # Set background color for the currently selected box
            self.entry_boxes[self.current_box_index]["entry"].focus()

    def shift_right(self, event):
        if self.current_box_index < len(self.entry_boxes) - 1:
            self.reset_background_color()  # Reset background color for all boxes
            self.current_box_index += 1
            self.set_background_color()  # Set background color for the currently selected box
            self.entry_boxes[self.current_box_index]["entry"].focus()

    def reset_background_color(self):
        for entry_box in self.entry_boxes:
            entry_box["frame"].config(highlightbackground='black')

    def set_background_color(self):
        self.entry_boxes[self.current_box_index]["frame"].config(highlightbackground='white')

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x300+{}+{}".format((root.winfo_screenwidth() - 500) // 2, (root.winfo_screenheight() - 300) // 2))
    app = CrosswordSimulator(root)
    root.mainloop()
