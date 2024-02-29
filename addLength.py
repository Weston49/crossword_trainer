import pandas as pd
import re

def clean_and_calculate_length(word):
    # Remove non-letter characters and calculate the length
    cleaned_word = re.sub(r'\([^)]*\)', '', str(word).lower()).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "").replace("!", "").replace("?", "").replace(",", "").replace("_", "")
    return len(cleaned_word)

def process_excel(input_file, output_file):
    # Read Excel file
    df = pd.read_excel(input_file)

    # Apply cleaning and length calculation to "Word" column
    df['Length'] = df['Word'].apply(clean_and_calculate_length)

    # Write back to Excel file
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    # Replace 'input.xlsx' with your input Excel file and 'output.xlsx' with your desired output file
    input_file_path = './NYTCrossword_2009_2016.xlsx'
    output_file_path = './test.xlsx'

    process_excel(input_file_path, output_file_path)
