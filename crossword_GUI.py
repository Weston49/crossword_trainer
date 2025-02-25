import pandas as pd
import random
import re
import tkinter as tk
from tkSliderWidget import Slider
import sys
import os
from tkinter import ttk, messagebox, scrolledtext


class CrosswordGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crossword Game")
        self.root.geometry("1440x900")  # Adjusted the window size

        self.total_correct = 0
        self.current_streak = 0
        self.total_tried = 0

        self.load_data()

        self.create_widgets()
        self.on_fire_size = 5

        self.hint_length = 1  # Initialize hint length to 1
        self.revealed_indices = set()
        self.used_hint = False

        self.clue_length = 3
        self.current_box_index = 0
        self.entry_boxes = []

        self.submit_enabled = True

        # Automatically start the game by pressing the "Next Clue" button
        self.play_game()

    def load_data(self):
        if getattr(sys, 'frozen', False):
            spreadsheet = os.path.join(sys._MEIPASS, "CrosswordData.xlsx")
        else:
            spreadsheet = "./CrosswordData.xlsx"
        self.df = pd.read_excel(spreadsheet)

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, pady=50)
        self.frame = frame

        # Label for weekday dropdown
        weekday_label = tk.Label(frame, text="Weekday:", font=("Arial", 24))
        weekday_label.grid(row=0, column=0, pady=(0, 5), columnspan=1, sticky=tk.E)

        # Slider for filtering by how common the clue is
        self.slider = Slider(frame, width = 300, height = 60, min_val = 1, max_val = 96, init_lis = [1,96], show_value = True, step_size=1)
        self.slider.grid(row=0, column=7, pady=(0, 5), columnspan=1, sticky=tk.W)
        self.frequency_start_var = tk.StringVar(value="1")  # Default value is "1"
        self.frequency_end_var = tk.StringVar(value="96")  # Default value is "96"

        #Update these two values when the slider is moved
        self.slider.setValueChangeCallback(lambda vals: [self.frequency_start_var.set(str(vals[0])), self.frequency_end_var.set(str(vals[1]))])

        #slider for filtering by how long the clue word is
        self.length_slider = Slider(frame, width = 200, height = 60, min_val = 3, max_val = 21, init_lis = [3,21], show_value = True, step_size=1)
        self.length_slider.grid(row=0, column=9, pady=(0, 5), columnspan=1, sticky=tk.W)
        self.length_start_var = tk.StringVar(value="3")  # Default value is "3"
        self.length_end_var = tk.StringVar(value="21")  # Default value is "21"

        #update these two values when the slider is moved
        self.length_slider.setValueChangeCallback(lambda vals: [self.length_start_var.set(str(vals[0])), self.length_end_var.set(str(vals[1]))])

        # Dropdown for filtering by weekday
        self.weekday_var = tk.StringVar(value="All")  # Default value is "All"
        weekday_dropdown = ttk.Combobox(frame, textvariable=self.weekday_var, values=["All", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], font=("Arial", 24), state='readonly', width=5)
        weekday_dropdown.grid(row=0, column=1, pady=(0, 5), columnspan=1, sticky=tk.E)

        #Label text for the frequency dropdown
        frequency_label = tk.Label(frame, text="Frequency:", font=("Arial", 24))
        frequency_label.grid(row=0, column=6, pady=(0, 5), columnspan=1, sticky=tk.W)

        #Label text for the length slider
        length_label = tk.Label(frame, text="Length:", font=("Arial", 24))
        length_label.grid(row=0, column=8, pady=(0, 5), columnspan=1, sticky=tk.W)

        # Dropdown for filtering by frequency
        #self.frequency_start_var = tk.StringVar(value="1")  # Default value is "1"
        #adds a text box that you can only enter numbers into
        #frequency_start_dropdown = ttk.Combobox(frame, textvariable=self.frequency_start_var, values=[str(i) for i in range(1, 97)], font=("Arial", 24), state='readonly', width=2)
        #frequency_start_dropdown.grid(row=0, column=4, pady=(0, 5), columnspan=1, sticky=tk.W)
        #self.frequency_end_var = tk.StringVar(value="96")  # Default value is "96"
        #frequency_end_dropdown = ttk.Combobox(frame, textvariable=self.frequency_end_var, values=[str(i) for i in range(1, 97)], font=("Arial", 24), state='readonly', width=2)
        #frequency_end_dropdown.grid(row=0, column=5, pady=(0, 5), columnspan=1, sticky=tk.W)

        self.label_streak = tk.Label(frame, text="", anchor="w")
        self.label_streak.grid(row=1, column=9, pady=(0, 5), sticky=tk.W)

        self.label_clue = tk.Label(frame, text="", wraplength=1100, anchor="w", justify=tk.LEFT, font=("Arial", 24))
        self.label_clue.grid(row=1, column=0, pady=(10, 5), columnspan=8, sticky=tk.W)

        self.label_result = tk.Label(frame, text="", anchor="w", font=("Arial", 24))
        self.label_result.grid(row=4, column=0, pady=(0, 5), columnspan=8, sticky=tk.W)

        # Scrolled text widget for explanation
        self.explanation_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=10, font=("Arial", 20))
        self.explanation_text.grid(row=6, column=0, pady=(0, 50), columnspan=10, sticky=tk.W)

        self.label_controls = tk.Label(frame, text="\n - Enter\n - cmd+n\n - cmd+j", wraplength=1100, anchor="w", justify=tk.LEFT, pady=5, font=("Arial", 24))
        self.label_controls.grid(row=7, column=1, pady=(0, 5), columnspan=1, sticky=tk.W)

        self.label_controls2 = tk.Label(frame, text="Controls\nSubmit Answer\nNext Clue\nReveal Letter", wraplength=1100, anchor="w", justify=tk.LEFT, pady=5, font=("Arial", 24))
        self.label_controls2.grid(row=7, column=0, pady=(0, 5), columnspan=1, sticky=tk.W)


        # Bind the Enter key to the check_answer method with button state check
        self.root.bind('<Return>', self.enter_pressed)
        self.root.bind("<Key>", self.handle_key_press)
        self.root.bind("<BackSpace>", self.handle_backspace)
        self.root.bind("<Left>", self.shift_left)
        self.root.bind("<Right>", self.shift_right)

        # Bind the Command-N key combination to the play_game method
        self.root.bind('<Command-n>', lambda event: self.play_game())

        self.root.bind('<Command-j>', lambda event: self.show_hint())


    def create_entry_boxes(self):
        # Remove existing entry boxes
        for entry_box in self.entry_boxes:
            entry_box["frame"].destroy()

        # Clear the list of entry boxes
        self.entry_boxes = []

        entry_frame = tk.Frame(self.frame)
        entry_frame.grid(row=3, column=0, columnspan=10, padx=10, pady=(10, 15), sticky="nsew")


        for i in range(self.clue_length):
            box_frame = tk.Frame(entry_frame, bg='black', borderwidth=0, relief='solid', highlightbackground='black', highlightthickness=4)
            box_frame.grid(row=0, column=i, padx=1, pady=2)

            box = tk.Entry(box_frame, width=2, justify='center', font=('Arial', 24, 'bold'))
            box.pack(side='top', fill='both', expand=True)
            box.config(state='readonly')  # Set boxes to read-only by default

            self.entry_boxes.append({"frame": box_frame, "entry": box, "hint_shown": False, "index": i})


    def play_game(self):
        # Check if the DataFrame is empty
        if self.df.empty:
            messagebox.showinfo("No Clues Found", "No clues found. Exiting the game.")
            self.root.destroy()
            return

        # Filter clues based on the selected weekday
        selected_weekday = self.weekday_var.get()
        if selected_weekday != "All":
            filtered_df = self.df[self.df['Weekday'] == selected_weekday]
            if filtered_df.empty:
                messagebox.showinfo("No Clues Found", f"No {selected_weekday} clues found.")
                self.root.destroy()
                return
        else:
            filtered_df = self.df

        selected_frequency_start = self.frequency_start_var.get()
        selected_frequency_end = self.frequency_end_var.get()
        # Filter clues based on the selected frequency range
        if selected_frequency_start != "1" or selected_frequency_end != "96" and not filtered_df.empty:
            filtered2_df = filtered_df[(filtered_df['Total'] >= int(float(selected_frequency_start))) & (filtered_df['Total'] <= int(float(selected_frequency_end)))]
            if filtered2_df.empty:
                messagebox.showinfo("No Clues Found", f"No clues found in the selected frequency range.")
                return
            filtered_df = filtered2_df
        else:
            filtered_df = filtered_df

        selected_length_start = self.length_start_var.get()
        selected_length_end = self.length_end_var.get()
        # Filter clues based on the selected length range
        if selected_length_start != "3" or selected_length_end != "21" and not filtered_df.empty:
            filtered3_df = filtered_df[(filtered_df['Length'] >= int(float(selected_length_start))) & (filtered_df['Length'] <= int(float(selected_length_end)))]
            if filtered3_df.empty:
                messagebox.showinfo("No Clues Found", f"No clues found in the selected length range.")
                return
            filtered_df = filtered3_df

        # Randomly select a row from the filtered DataFrame
        self.random_row = filtered_df.sample()


        # Extract clue information
        self.clue = self.random_row['Clue'].values[0]
        self.word = self.random_row['Word'].values[0]
        self.times_used = self.random_row['Total'].values[0]
        self.correct_answer_stripped = re.sub(r'\([^)]*\)', '', self.word.lower()).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "").replace("!", "").replace("?", "").replace(",", "").replace("_", "")
        clue_length = len(self.correct_answer_stripped)
        self.year = self.random_row['Year'].values[0]
        self.weekday = self.random_row['Weekday'].values[0]
        self.clue_length = clue_length

        self.create_entry_boxes()
        self.current_box_index = 0
        self.entry_boxes[self.current_box_index]["entry"].focus()
        self.set_background_color()  # Set background color for the currently selected box

        self.label_clue.config(text=f"🤨 Clue: {self.clue}\n🗓️ Date: {self.year}, {self.weekday}\nTimes Used: ??")
        self.label_result.config(text="")
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.config(state=tk.DISABLED)
        if self.current_streak > self.on_fire_size:
            self.label_streak.config(text=f"🔥🔥 {self.current_streak} 🔥🔥\nTotal Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}", font=("Arial", 20))
        else:
            self.label_streak.config(text=f"{'🔥' * self.current_streak}{'🧊' * (self.on_fire_size - self.current_streak)}\nTotal Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}", font=("Arial", 20))

        # Enable the "Submit Answer" button for the new clue
        self.submit_enabled = True
        self.hint_length = 1
        # Clear the revealed indices set
        self.revealed_indices = set()
        self.used_hint = False

    def handle_key_press(self, event):
        key = event.char.upper()

        if key.isalpha() and self.current_box_index < len(self.entry_boxes) and not self.entry_boxes[self.current_box_index]["hint_shown"]:
            self.reset_background_color()  # Reset background color for all boxes
            self.entry_boxes[self.current_box_index]["entry"].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index]["entry"].delete(0, tk.END)  # Clear existing text
            self.entry_boxes[self.current_box_index]["entry"].insert(0, key)
            self.current_box_index += 1
            if self.current_box_index < len(self.entry_boxes):
                self.entry_boxes[self.current_box_index]["entry"].focus()
            else:
                self.current_box_index -= 1  # Keep the current box index within the valid range
                self.entry_boxes[self.current_box_index]["entry"].config(state='readonly')  # Change back to read-only
                self.reset_background_color()  # Reset background color for all boxes
                self.set_background_color()  # Set background color for the currently selected box
        elif key.isalpha() and self.entry_boxes[self.current_box_index]["hint_shown"] and self.current_box_index < len(self.entry_boxes) - 1:
            self.reset_background_color()  # Reset background color for all boxes
            self.current_box_index += 1
            self.entry_boxes[self.current_box_index]["entry"].focus()
            self.set_background_color()  # Set background color for the currently selected box

        if self.current_box_index >= len(self.entry_boxes):
            self.current_box_index = len(self.entry_boxes) - 1  # Keep the current box index within the valid range
            self.reset_background_color()  # Reset background color for all boxes
            self.set_background_color()  # Set background color for the currently selected box


        self.entry_boxes[self.current_box_index]["entry"].config(state='readonly')  # Change back to read-only
        self.entry_boxes[self.current_box_index - 1]["entry"].config(state='readonly')  # Change back to read-only

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


    def handle_backspace(self, event):
        if self.current_box_index >= 0 and self.entry_boxes[self.current_box_index]["hint_shown"] == False:
            self.reset_background_color()  # Reset background color for all boxes
            self.entry_boxes[self.current_box_index]["entry"].config(state='normal')  # Make box writable
            self.entry_boxes[self.current_box_index]["entry"].delete(0, tk.END)
            self.entry_boxes[self.current_box_index]["entry"].config(state='readonly')  # Change back to read-only
        if self.current_box_index > 0:
            self.current_box_index -= 1
            self.entry_boxes[self.current_box_index]["entry"].focus()
            self.reset_background_color()  # Reset background color for all boxes
            self.set_background_color()  # Set background color for the currently selected box
        if self.current_box_index < 0:
            self.current_box_index = 0
            self.entry_boxes[self.current_box_index]["entry"].focus()
            self.reset_background_color()  # Reset background color for all boxes
            self.set_background_color()  # Set background color for the currently selected box

    def check_answer(self):
        user_answer = ''.join(entry["entry"].get() for entry in self.entry_boxes)

        user_answer_stripped = re.sub(r'\([^)]*\)', '', user_answer).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")
        user_answer_lower = user_answer_stripped.lower()
        self.label_clue.config(text=f"🤨 Clue: {self.clue}\n🗓️ Date: {self.year}, {self.weekday}\nTimes Used: {self.times_used}")

        if user_answer_lower == "exit":
            messagebox.showinfo("Thanks for playing!", f"Total Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}")
            self.root.destroy()
            return

        # Disable the "Submit Answer" button to prevent multiple submissions
        self.submit_enabled = False
        self.total_tried += 1
        if user_answer_lower == self.correct_answer_stripped or user_answer_lower == "3824":
            self.label_result.config(text=f"✅ Correct! Formatted Answer: {self.word.lower()}")
            if not self.used_hint:
                self.total_correct += 1
                self.current_streak += 1
            else:
                self.current_streak = 0
        else:
            self.label_result.config(text=f"❌ Incorrect. The correct answer is: {self.word.lower()}")
            self.current_streak = 0

        explanation = self.random_row['Explanation'].values[0]
        explanation = "No explanation found" if pd.isna(explanation) else explanation
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.insert(tk.END, explanation)
        self.explanation_text.config(state=tk.DISABLED)

    def enter_pressed(self, event):
        # Check if the "Submit Answer" button is enabled before processing the answer
        if self.submit_enabled:
            self.check_answer()
        else:
            self.play_game()

    def reset_background_color(self):
        for entry_box in self.entry_boxes:
            if entry_box["hint_shown"] == False:
                entry_box["frame"].config(highlightbackground='black')
            else:
                entry_box["frame"].config(highlightbackground='lightcoral')

    def set_background_color(self):
        self.entry_boxes[self.current_box_index]["frame"].config(highlightbackground='white')

    def show_hint(self):
        self.used_hint = True
        if hasattr(self, 'word'):
            # Increment the hint length and update the displayed hint
            self.hint_length += 1
            box_to_fill = self.randomly_select_box()
            if box_to_fill != None:
                box_to_fill["entry"].config(state='normal')
                box_to_fill["entry"].delete(0, tk.END)
                # Fill the box with the correct letter from the stripped down word upper case
                box_to_fill["entry"].insert(0, self.correct_answer_stripped[box_to_fill["index"]].upper())
                box_to_fill["entry"].config(state='readonly')
                box_to_fill["hint_shown"] = True
                #change the background color of the hint box to red
                box_to_fill["frame"].config(highlightbackground='lightcoral')

    def randomly_select_box(self):
        # Filter entry boxes with "hint_shown" field as False
        eligible_boxes = [entry_box for entry_box in self.entry_boxes if not entry_box["hint_shown"]]

        if eligible_boxes:
            # Randomly select an entry box
            selected_box = random.choice(eligible_boxes)
            return selected_box
        else:
            return None



if __name__ == "__main__":
    root = tk.Tk()
    window_width, window_height = 1440, 900
    root.geometry(f"{window_width}x{window_height}+{(root.winfo_screenwidth() - window_width) // 2}+{(root.winfo_screenheight() - window_height) // 2}")
    game_gui = CrosswordGameGUI(root)
    root.mainloop()
