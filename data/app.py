import pandas as pd
csv_file_path = '/Users/byar/Downloads/stack-overflow-developer-survey-2021/survey_results_public.csv'
df = pd.read_csv(csv_file_path, low_memory=False)


cols_to_remove = [
    'ResponseId', 'US_State', 'UK_Country', 
    'EdLevel', 'Age1stCode', 'LearnCode', 
    'YearsCode', 'OrgSize', 'Currency', 
    'CompTotal', 'CompFreq', 'Age', 'Gender', 'Trans', 'Sexuality', 
    'Ethnicity', 'Accessibility', 'MentalHealth', 'SurveyLength', 'SurveyEase',
    'NEWStuck', 'NEWSOSites', 'SOVisitFreq', 'SOAccount', 'SOPartFreq', 'SOComm', 'NEWOtherComms'
    ] + [col for col in df.columns if col.endswith('WantToWorkWith')]

clean_df = df.drop(cols_to_remove, axis=1)
print(clean_df.columns.tolist())


