from collections import Counter
import pandas as pd

# def normalize(col_name):
#     values = sorted(df[col_name].unique())
#     value_to_index = {
#         value: index
#         for index, value
#         in enumerate(values)
#         }

#     df[col_name] = df[col_name].map(value_to_index)
#     df[col_name] = pd.to_numeric(df[col_name], errors='raise')
#     return value_to_index

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
    'ProfessionalCloud', 'ProfessionalQuestion', 'SOHow', 'TechDoc', 'TechEndorse', 'OpSys', 'OpSysProfessional use'
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
    df['ConvertedCompYearly'] = pd.to_numeric(df['ConvertedCompYearly'], errors='raise')

    df = df[
        (df['MainBranch'] == 'I am a developer by profession') 
        & (df['Employment'].isin(['Employed full-time', 'Employed, full-time'])) 
        & (df['ConvertedCompYearly'] > 100)
        & (df['YearsCodePro'] >= 0)
        ]

    df = df.drop(['MainBranch', 'Employment'], axis=1)
    df.columns = [col.removesuffix("HaveWorkedWith") for col in df.columns]
    return df

dfs = []
for year in [2021,2022,2023,2024]:
    df = get_df(f'/Users/byar/Downloads/stack-overflow-developer-survey-{year}/survey_results_public.csv')
    df['Year'] = year
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)
df.to_csv("merged.csv", index=False)
print(df.columns.to_list())

# # --- Preprocessing (Modify df in-place) ---
# for col in tag_columns_to_analyze:
#     df[col] = (
#         df[col]
#         .fillna('')
#         .astype(str)
#         .str.split(';')
#         .apply(lambda lst: [tag.strip() for tag in lst if tag.strip()])
#     )

# # --- Initialize Counters and Filter ---
# # Use a dictionary to hold a Counter for each column type
# grouped_tag_counts = {col: Counter() for col in tag_columns_to_analyze}

# # Create boolean mask for filtering criteria
# filter_mask = (
#     (df['Country'] == 'Germany') &
#     # Uncomment and adjust YearsCodePro filter as needed
#     # (df['YearsCodePro'] >= 3) &
#     # (df['YearsCodePro'] <= 6) &
#     (df['Language'].apply(lambda lang_list: target_language in lang_list))
# )

# # --- Tag Extraction and Counting (Grouped) ---
# # Iterate directly over the filtered slice of the DataFrame
# for index, row in df[filter_mask].iterrows():
#     for col in tag_columns_to_analyze: # Iterate through the columns/categories
#         for tag in row[col]: # Iterate through tags in the list for that row/column
#             if tag != target_language:
#                 # Increment the count for this tag within its specific category's Counter
#                 grouped_tag_counts[col][tag] += 1

# # --- Output (Grouped, Sorted, Filtered by Count) ---
# print(f"Tags most often reported with '{target_language}' (Grouped by Category)")
# print(f"Filter: Country=Germany") # Add YearsCodePro if uncommented above
# print("-" * 60)

# found_any = False
# for category, tag_counter in grouped_tag_counts.items():
#     # Get tags for this category sorted by count, descending
#     sorted_tags = tag_counter.most_common()

#     # Filter for count >= 100 and check if any tags remain for this category
#     filtered_sorted_tags = [(tag, count) for tag, count in sorted_tags if count >= 1] # Changed threshold to 1 for example visibility

#     if filtered_sorted_tags:
#         found_any = True
#         print(f"\n{category}:") # Print category header
#         for tag, count in filtered_sorted_tags:
#             # Print each tag and its count for this category
#             print(f"- {tag:<25}: {count}")

# if not found_any:
#     print("\nNo co-occurring tags found meeting the count threshold for the specified criteria.")

# countries = [
#     'Germany', 
#     # 'United Kingdom of Great Britain and Northern Ireland', 
#     # 'Netherlands',
#     # 'Denmark', 
#     # 'Switzerland',
#     ]

# language_stats = (
#     df.loc[
#         (df['Country'].isin(countries)) &
#         (df['YearsCodePro'] >= 3) &
#         (df['YearsCodePro'] <= 8)
#     ]
#       .explode('Language')
#       .dropna(subset=['Language', 'ConvertedCompYearly'])
#       .loc[lambda x: x['Language'] != '']
#       .groupby('Language')['ConvertedCompYearly']
#       .agg(['median', 'count'])
#       .sort_values(by='median', ascending=False)
# )

# for language, stats in language_stats.iterrows():
#     median_comp = stats['median']
#     sample_size = stats['count']
#     if sample_size > 400:
#         print(f"{language:<30}: Median Comp = ${median_comp:>12,.0f}, Sample Size = {int(sample_size):>8}")


# countries = normalize('Country')
# print(countries)

# os = normalize('OpSys')
# print(os)
