import pandas as pd
import random
import re
import shutil

# Read the Excel file into a pandas DataFrame
df = pd.read_excel('./NYT Crossword_2009_2016.xlsx')

total_correct = 0
current_streak = 0
wrong_streak = 0
total_tried = 0
terminal_columns = shutil.get_terminal_size().columns
terminal_rows = shutil.get_terminal_size().lines

# Prompt the user to choose a day
while True:
    print("\n" * (terminal_rows - 1))
    chosen_day = input("Choose a day to train (Mon, Tue, Wed, Thu, Fri, Sat, Sun): ").capitalize()

    if chosen_day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        break
    else:
        print("Invalid day. Please choose a valid day.")
        continue

while True:
    # Filter rows where 'Weekday' is the chosen day
    day_df = df[df['Weekday'] == chosen_day]

    # Check if the filtered DataFrame is empty
    if day_df.empty:
        print(f"No {chosen_day} clues found. Exiting the game.")
        break

    # Select a random clue from the filtered DataFrame
    random_row = day_df.sample()

    # Extract clue information
    clue = random_row['Clue'].values[0]
    word = random_row['Word'].values[0]
    correct_answer_stripped = re.sub(r'\([^)]*\)', '', word.lower()).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")
    clue_length = len(correct_answer_stripped)
    year = random_row['Year'].values[0]
    weekday = random_row['Weekday'].values[0]

    print(f"🤨Crossword Clue:            {clue}")
    print(f"🔢Clue Length:               {clue_length} characters", "_ " * clue_length)
    print(f"🗓️Date:                      {year}, {weekday}")

    # Prompt the user for an answer
    user_answer = input("Your answer (type 'exit' to stop): ").strip()
    print("")
    total_tried += 1
    
    # Check if the user wants to stop
    if user_answer.lower() == 'exit':
        print("Thanks for playing!")
        break

    # Remove anything in parentheses and characters like '-', ' ', "'", '/', etc. from the user's answer
    user_answer_stripped = re.sub(r'\([^)]*\)', '', user_answer).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")

    # Check if the answer is correct
    user_answer_lower = user_answer_stripped.lower()

    if user_answer_lower == correct_answer_stripped or user_answer_lower == "3824":
        print("✅Correct!")
        total_correct += 1
        current_streak += 1
        if current_streak + 20 > (terminal_columns // 2):
            print("🔥STREAK TOO HOT🔥")
        else:
            print(f"Current Streak: {'🔥' * current_streak}")
        wrong_streak = 0
    else:
        print("❌Incorrect. The correct answer is:", word.lower())
        wrong_streak += 1
        current_streak = 0
        if wrong_streak+20 > ((terminal_columns // 2)):
            print("❌YOU SUCK SO BAD❌")
        else:
            print(f"Wrong Streak: {'❌' * wrong_streak}")

    # Display the explanation, handling empty explanation
    explanation = random_row['Explanation'].values[0]
    explanation = "No explanation found" if pd.isna(explanation) else explanation
    print("\nExplanation:")
    print(explanation)

    # Calculate the number of newlines to print based on the length of the explanation and terminal columns
    newline_count = max(terminal_rows - len(explanation) // (terminal_columns) - 18, 0)

    # Print the appropriate number of newlines

    # Display total correct, current streak, and answer word length
    print("")
    print(f"Total Attempted: {total_tried}")
    print(f"Total Correct:   {total_correct}")
    print("\n" * newline_count)

