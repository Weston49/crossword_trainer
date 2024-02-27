import tkinter as tk

class CrosswordSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Crossword Simulator")

        self.current_box_index = 0
        self.entry_boxes = []
        self.clue = "CROSSWORD"  # Change the clue word as needed

        self.create_entry_boxes()
        self.create_enter_button()
        self.create_result_textbox()
        self.root.bind("<Key>", self.handle_key_press)
        self.root.bind("<BackSpace>", self.handle_backspace)
        self.root.bind("<Return>", self.handle_enter)

    def create_entry_boxes(self):
        for i in range(len(self.clue)):
            box = tk.Entry(self.root, width=3, justify='center', font=('Arial', 14, 'bold'))
            box.grid(row=0, column=i, padx=2, pady=2)
            box.config(state='readonly')  # Set boxes to read-only by default
            self.entry_boxes.append(box)

    def create_enter_button(self):
        enter_button = tk.Button(self.root, text="Enter", command=self.check_answer)
        enter_button.grid(row=1, column=0, columnspan=len(self.clue), pady=10)

    def create_result_textbox(self):
        self.result_textbox = tk.Text(self.root, height=2, width=30, state='disabled', font=('Arial', 12))
        self.result_textbox.grid(row=2, column=0, columnspan=len(self.clue), pady=10)

    def handle_key_press(self, event):
        key = event.char.upper()

        if key.isalpha() and self.current_box_index < len(self.entry_boxes):
            self.entry_boxes[self.current_box_index].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index].insert(0, key)
            self.current_box_index += 1

            if self.current_box_index < len(self.entry_boxes):
                self.entry_boxes[self.current_box_index].focus()

            self.entry_boxes[self.current_box_index - 1].config(state='readonly')  # Change back to read-only

    def handle_backspace(self, event):
        if self.current_box_index > 0:
            self.current_box_index -= 1
            self.entry_boxes[self.current_box_index].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index].delete(0, tk.END)
            self.entry_boxes[self.current_box_index].focus()
            self.entry_boxes[self.current_box_index].config(state='readonly')  # Change back to read-only

    def handle_enter(self, event):
        self.check_answer()

    def check_answer(self):
        entered_string = ''.join(entry.get() for entry in self.entry_boxes)
        if entered_string == self.clue:
            result_message = "Congratulations! You solved the puzzle!"
        else:
            result_message = "Sorry, try again."

        self.result_textbox.config(state='normal')
        self.result_textbox.delete(1.0, tk.END)
        self.result_textbox.insert(tk.END, result_message)
        self.result_textbox.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = CrosswordSimulator(root)
    root.mainloop()
