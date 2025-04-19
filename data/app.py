import pandas as pd
csv_file_path = '/Users/byar/Downloads/stack-overflow-developer-survey-2021/survey_results_public.csv'
df = pd.read_csv(csv_file_path)

cols_to_remove = [
    'ResponseId', 'US_State', 'UK_Country', 
    'EdLevel', 'Age1stCode', 'LearnCode', 
    'YearsCode', 'OrgSize', 'Currency', 
    'CompTotal', 'CompFreq', 'Age', 'Gender', 'Trans', 'Sexuality', 
    'Ethnicity', 'Accessibility', 'MentalHealth', 'SurveyLength', 'SurveyEase',
    'NEWStuck', 'NEWSOSites', 'SOVisitFreq', 'SOAccount', 'SOPartFreq', 'SOComm', 'NEWOtherComms'
    ] + [col for col in df.columns if col.endswith('WantToWorkWith')]

df = df.drop(cols_to_remove, axis=1)
df = df.dropna(subset=["ConvertedCompYearly", "YearsCodePro"])

df['YearsCodePro'] = df['YearsCodePro'].replace({
    'More than 50 years': 50,
    'Less than 1 year': 0
})

df['YearsCodePro'] = pd.to_numeric(df['YearsCodePro'], errors='raise')

df = df[
    (df['MainBranch'] == 'I am a developer by profession') 
    & (df['Employment'] == 'Employed full-time') 
    & (df['ConvertedCompYearly'] > 0) 
    & (df['YearsCodePro'] >= 0)
    ]

df = df.drop(['MainBranch', 'Employment'], axis=1)
print(df.columns.to_list())
print(len(df))
