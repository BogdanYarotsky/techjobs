import pandas as pd
print("hello")

csv_file_path = '/Users/byar/Documents/survey_results_public_2021.csv'

df = pd.read_csv(csv_file_path, low_memory=False)



