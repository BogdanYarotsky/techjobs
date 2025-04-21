from collections import Counter
import io
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

def sql_safe(value):
    if pd.isna(value):
        return "NULL"
    elif isinstance(value, (int, float)):
        if pd.isna(value): # Explicit check for float NaN
             return "NULL"
        return str(value)
    elif isinstance(value, str):
        sanitized = value.replace("'", "''")
        return f"'{sanitized}'"
    else:
        # Attempt to convert non-standard types to string and sanitize
        sanitized = str(value).replace("'", "''")
        return f"'{sanitized}'"

# dfs = []
# for year in [2021,2022,2023,2024]:
#     df = get_df(f'/Users/byar/Downloads/stack-overflow-developer-survey-{year}/survey_results_public.csv')
#     df['Year'] = year
#     dfs.append(df)

# df = pd.concat(dfs, ignore_index=True)
# df.to_csv("merged.csv", index=False)
df = pd.read_csv("merged.csv")

reports_table = "SalaryReports"
tags_table = "Tags"
link_table = "SalaryReportTags"
output_sql_file = "insert_statements.sql"

tags_cols = [
    'DevType', 'Language', 'Database', 
    'Platform', 'Webframe', 'MiscTech', 
    'ToolsTech', 'NEWCollabTools']

report_info_cols = [
    'Country', 'YearsCodePro', 'ConvertedCompYearly', 'Year']

for col in tags_cols:
    df[col] = df[col].str.split(';').apply(lambda x: x if isinstance(x, list) else [])

unique_tags_map = {}
tag_inserts = io.StringIO()
current_tag_id = 1

for tag_type in tags_cols:
    # Assuming columns exist now due to active_tags_cols filter
    # Explode, fillna for potential empty lists, get unique
    exploded_series = df[tag_type].explode().fillna('')
    unique_in_col = exploded_series.unique()

    for tag_name in unique_in_col:
        tag_name = str(tag_name).strip()
        if not tag_name: # Skip empty tags
            continue

        tag_key = (tag_name, tag_type)
        if tag_key not in unique_tags_map:
            unique_tags_map[tag_key] = current_tag_id
            sql = f"INSERT INTO {tags_table} (TagID, TagName, TagType) VALUES ({current_tag_id}, {sql_safe(tag_name)}, {sql_safe(tag_type)});\n"
            tag_inserts.write(sql)
            current_tag_id += 1

# --- Generate SalaryReports and SalaryReportTags INSERTs ---
report_inserts = io.StringIO()
link_inserts = io.StringIO()
current_report_id = 1

# Use itertuples for efficiency
for row_tuple in df.itertuples(index=False, name=None):
    row_dict = dict(zip(df.columns, row_tuple))

    # Generate INSERT for SalaryReports
    report_values = [sql_safe(row_dict.get(col)) for col in report_info_cols]
    sql_report = f"INSERT INTO {reports_table} (ReportID, {', '.join(report_info_cols)}) VALUES ({current_report_id}, {', '.join(report_values)});\n"
    report_inserts.write(sql_report)

    # Generate INSERTs for SalaryReportTags
    for tag_type in tags_cols:
         # Get list, defaulting to empty list if column somehow missing (shouldn't happen)
        tag_list = row_dict.get(tag_type, [])
        if isinstance(tag_list, list): # Check it's a list
            for tag_name in tag_list:
                tag_name = str(tag_name).strip()
                if not tag_name: # Skip empty tag names
                    continue

                tag_key = (tag_name, tag_type)
                # Look up tag_id only if the key exists in the map
                tag_id = unique_tags_map.get(tag_key)
                if tag_id is not None:
                    sql_link = f"INSERT INTO {link_table} (ReportID, TagID) VALUES ({current_report_id}, {tag_id});\n"
                    link_inserts.write(sql_link)
                # No warning needed in production if tag not found

    current_report_id += 1

# --- Combine and Output SQL ---
final_sql = f"-- INSERT statements for {tags_table} --\n"
final_sql += tag_inserts.getvalue()
final_sql += f"\n-- INSERT statements for {reports_table} --\n"
final_sql += report_inserts.getvalue()
final_sql += f"\n-- INSERT statements for {link_table} (Link Table) --\n"
final_sql += link_inserts.getvalue()

tag_inserts.close()
report_inserts.close()
link_inserts.close()

# Write to file, assuming permissions are correct
with open(output_sql_file, "w", encoding="utf-8") as f:
    f.write(final_sql)


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
