import pandas as pd
import random
import re
import tkinter as tk
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
        
        # Automatically start the game by pressing the "Next Clue" button
        self.play_game()

    def load_data(self):
        self.df = pd.read_excel('./NYT Crossword_2009_2016.xlsx')

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, pady=50)

        # Dropdown for filtering by weekday
        self.weekday_var = tk.StringVar(value="All")  # Default value is "All"
        weekday_dropdown = ttk.Combobox(frame, textvariable=self.weekday_var, values=["All", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], font=("Arial", 20), state='readonly')
        weekday_dropdown.grid(row=1, column=0, pady=(0, 5), columnspan=2, sticky=tk.W)

        self.label_streak = tk.Label(frame, text="", anchor="w")
        self.label_streak.grid(row=0, column=2, pady=(0, 5), sticky=tk.W)

        self.label_clue = tk.Label(frame, text="", wraplength=1100, anchor="w", justify=tk.LEFT, font=("Arial", 20))
        self.label_clue.grid(row=2, column=0, pady=(10, 5), columnspan=2, sticky=tk.W)

        self.label_result = tk.Label(frame, text="", anchor="w", font=("Arial", 20))
        self.label_result.grid(row=3, column=0, pady=(0, 5), columnspan=3, sticky=tk.W)

        # Scrolled text widget for explanation
        self.explanation_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=10, font=("Arial", 20))
        self.explanation_text.grid(row=4, column=0, pady=(0, 5), columnspan=3, sticky=tk.W)

        self.label_correct_answer = tk.Label(frame, text="", wraplength=1100, anchor="w", justify=tk.LEFT, pady=5, font=("Arial", 20))
        self.label_correct_answer.grid(row=5, column=0, pady=(0, 5), columnspan=3, sticky=tk.W)

        self.entry_answer = tk.Entry(frame, width=50, font=("Arial", 20))
        self.entry_answer.grid(row=6, column=0, pady=(5, 10), sticky=tk.W)

        # Move the "Submit Answer" button to the left of the "Next Clue" button
        self.button_submit = tk.Button(frame, text="Submit Answer (enter)", command=self.check_answer, font=("Arial", 20))
        self.button_submit.grid(row=7, column=0, pady=(5, 10), sticky=tk.W)

        button_next_clue = tk.Button(frame, text="Next Clue (cmd+n)", command=self.play_game, font=("Arial", 20))
        button_next_clue.grid(row=7, column=2, pady=(10, 5), columnspan=3, sticky=tk.W)

        #hint button
        self.button_hint = tk.Button(frame, text="Hint (cmd+j)", command=self.show_hint, font=("Arial", 20))
        self.button_hint.grid(row=7, column=1, pady=(10, 5), sticky=tk.W)

        self.hint_text = tk.Text(frame, wrap=tk.WORD, width=50, height=1, font=("Arial", 14))
        self.hint_text.grid(row=8, column=0, pady=(5, 10), columnspan=2, sticky=tk.W)
        self.hint_text.insert(tk.END, "Hint box")
        self.hint_text.config(state=tk.DISABLED)

        # Bind the Enter key to the check_answer method with button state check
        self.root.bind('<Return>', self.enter_pressed)

        # Bind the Command-N key combination to the play_game method
        self.root.bind('<Command-n>', lambda event: self.play_game())

        self.root.bind('<Command-j>', lambda event: self.show_hint())


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
                messagebox.showinfo("No Clues Found", f"No {selected_weekday} clues found. Exiting the game.")
                self.root.destroy()
                return
            self.random_row = filtered_df.sample()
        else:
            self.random_row = self.df.sample()

        # Extract clue information
        self.clue = self.random_row['Clue'].values[0]
        self.word = self.random_row['Word'].values[0]
        self.correct_answer_stripped = re.sub(r'\([^)]*\)', '', self.word.lower()).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")
        clue_length = len(self.correct_answer_stripped)
        year = self.random_row['Year'].values[0]
        weekday = self.random_row['Weekday'].values[0]

        self.label_clue.config(text=f"🤨 Clue: {self.clue}\n🔢 Chars: {clue_length} characters \n🗓️ Date: {year}, {weekday}")
        self.label_result.config(text="")
        self.label_correct_answer.config(text="")
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.config(state=tk.DISABLED)
        self.entry_answer.delete(0, 'end')
        if self.current_streak > self.on_fire_size:
            self.label_streak.config(text=f"🔥🔥 {self.current_streak} 🔥🔥\nTotal Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}", font=("Arial", 20))
        else:
            self.label_streak.config(text=f"{'🔥' * self.current_streak}{'🧊' * (self.on_fire_size - self.current_streak)}\nTotal Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}", font=("Arial", 20))

        # Enable the "Submit Answer" button for the new clue
        self.enable_submit_button()
        self.hint_length = 1
        # Clear the hint box
        self.hint_text.config(state=tk.NORMAL)
        self.hint_text.delete(1.0, tk.END)
        self.hint_text.insert(tk.END, "Hint box")
        self.hint_text.config(state=tk.DISABLED)
        # Clear the revealed indices set
        self.revealed_indices = set()
        self.used_hint = False

    def check_answer(self):
        user_answer = self.entry_answer.get().strip()

        user_answer_stripped = re.sub(r'\([^)]*\)', '', user_answer).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")
        user_answer_lower = user_answer_stripped.lower()

        if user_answer_lower == "exit":
            messagebox.showinfo("Thanks for playing!", f"Total Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}")
            self.root.destroy()
            return

        # Disable the "Submit Answer" button to prevent multiple submissions
        self.disable_submit_button()
        self.total_tried += 1
        if user_answer_lower == self.correct_answer_stripped or user_answer_lower == "3824":
            self.label_result.config(text="✅ Correct!")
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

    def disable_submit_button(self):
        # Disable the "Submit Answer" button
        self.button_submit.config(state=tk.DISABLED)

    def enable_submit_button(self):
        # Enable the "Submit Answer" button
        self.button_submit.config(state=tk.NORMAL)

    def enter_pressed(self, event):
        # Check if the "Submit Answer" button is enabled before processing the answer
        if self.button_submit.cget('state') == 'normal':
            self.check_answer()

    def show_hint(self):
        self.used_hint = True
        if hasattr(self, 'word'):
            # Increment the hint length and update the displayed hint
            self.hint_length += 1
            hint = self.generate_hint(self.word, self.hint_length)
            self.hint_text.config(state=tk.NORMAL)
            self.hint_text.delete(1.0, tk.END)
            self.hint_text.insert(tk.END, hint)
            self.hint_text.config(state=tk.DISABLED)

    def generate_hint(self, word, hint_length):
        # Replace all previously revealed letters and one extra random letter with "_"
        if hint_length <= len(word):
            unrevealed_indices = set(range(len(word))) - self.revealed_indices
            extra_revealed_indices = random.sample(list(unrevealed_indices), hint_length - 1 - len(self.revealed_indices))
            self.revealed_indices.update(extra_revealed_indices)
            hint = ''.join(char if i in self.revealed_indices else "_ " for i, char in enumerate(word))
        else:
            hint = word  # Show the complete word if the hint length exceeds the word length

        return hint



if __name__ == "__main__":
    root = tk.Tk()
    game_gui = CrosswordGameGUI(root)
    root.mainloop()
