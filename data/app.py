import pandas as pd

bad_cols_set = {
    'ResponseId', 'US_State', 'UK_Country', 
    'EdLevel', 'Age1stCode', 'LearnCode', 
    'YearsCode', 'OrgSize', 'Currency', 
    'CompTotal', 'CompFreq', 'Age', 'Gender', 'Trans', 'Sexuality', 
    'Ethnicity', 'Accessibility', 'MentalHealth', 'SurveyLength', 'SurveyEase',
    'NEWStuck', 'NEWSOSites', 'SOVisitFreq', 'SOAccount', 'SOPartFreq', 'SOComm', 'NEWOtherComms',
    'Blockchain', 'TBranch', 'ICorPM', 'WorkExp', 'Knowledge_1', 'Knowledge_2', 'Knowledge_3', 
    'Knowledge_4', 'Knowledge_5', 'Knowledge_6', 'Knowledge_7', 'Frequency_1', 'Frequency_2', 
    'Frequency_3', 'TimeSearching', 'TimeAnswering', 'Onboarding', 'ProfessionalTech', 
    'TrueFalse_1', 'TrueFalse_2', 'TrueFalse_3', 'OpSysPersonal use',
    'CodingActivities', 'LearnCodeOnline', 'LearnCodeCoursesCert',
    'PurchaseInfluence', 'BuyNewTool', 'VersionControlSystem', 
    'VCInteraction', 'VCHostingPersonal use', 'VCHostingProfessional use',
    'OfficeStackAsyncHaveWorkedWith', 'OfficeStackSyncHaveWorkedWith',
    'AIAcc', 'AIBen', 'AIDevHaveWorkedWith', 'AINextNeither different nor similar', 
    'AINextSomewhat different', 'AINextSomewhat similar', 
    'AINextVery different', 'AINextVery similar', 'AISearchHaveWorkedWith', 
    'AISelect', 'AISent', 'AIToolCurrently Using', 'AIToolInterested in Using', 
    'AIToolNot interested in Using', 'Industry', 'Knowledge_8', 'Q120', 'SOAI', 'TechList', 'RemoteWork',
    'AIChallenges', 'AIComplex', 'AIEthics', 'AINextLess integrated', 'AINextMore integrated', 'AINextMuch less integrated', 
    'AINextMuch more integrated', 'AINextNo change', 'AISearchDevHaveWorkedWith', 'AIThreat', 'BuildvsBuy', 'Check',
    'EmbeddedHaveWorkedWith', 'Frustration', 'JobSat', 'JobSatPoints_1', 'JobSatPoints_10', 'JobSatPoints_11', 'JobSatPoints_4', 
    'JobSatPoints_5', 'JobSatPoints_6', 'JobSatPoints_7', 'JobSatPoints_8', 'JobSatPoints_9', 'Knowledge_9',
    'ProfessionalCloud', 'ProfessionalQuestion', 'SOHow', 'TechDoc', 'TechEndorse'
}

def get_df(csv_file):
    df = pd.read_csv(csv_file, low_memory=False)

    cols_to_remove = [col for col in df.columns 
                      if col.endswith('WantToWorkWith') 
                      or col in bad_cols_set
                      or col.endswith('Admired')]


    df = df.drop(cols_to_remove, axis=1)

    df = df.dropna(subset=["ConvertedCompYearly", "YearsCodePro", "Country"])

    df['YearsCodePro'] = df['YearsCodePro'].replace({
        'More than 50 years': 50,
        'Less than 1 year': 0
    })

    df['YearsCodePro'] = pd.to_numeric(df['YearsCodePro'], errors='raise')

    df = df[
        (df['MainBranch'] == 'I am a developer by profession') 
        & (df['Employment'].isin(['Employed full-time', 'Employed, full-time'])) 
        & (df['ConvertedCompYearly'] > 100)
        & (df['YearsCodePro'] >= 0)
        ]

    df = df.drop(['MainBranch', 'Employment'], axis=1)
    
    df.columns = [rename_col(col) for col in df.columns]

    return df

def rename_col(col):
    if col == 'OpSysProfessional use':
        return 'OpSys'

    return col.removesuffix("HaveWorkedWith")

dfs = []
for year in [2024]:#,2022,2023,2024]:
    df = get_df(f'/Users/byar/Downloads/stack-overflow-developer-survey-{year}/survey_results_public.csv')
    df['Year'] = year
    # print(df.columns.to_list())
    # print(len(df))
    dfs.append(df)

pd.options.display.max_rows = None

df = pd.concat(dfs, ignore_index=True)

countries = sorted(df['Country'].unique())

country_dict = {
    country: index 
    for index, country
    in enumerate(countries)
    }

df['Country'] = df['Country'].apply(lambda x: country_dict[x])
df['Country'] = pd.to_numeric(df['Country'], errors='raise')
