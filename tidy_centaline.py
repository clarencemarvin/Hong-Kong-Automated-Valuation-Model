import pandas as pd
import json

# Replace 'your_file.csv' with the path to your CSV file
centaline_df = pd.read_csv('centaline_date.csv')


# Load the dictionary from the text file
with open('dictionary.txt', 'r', encoding='utf-8') as file:
    hong_kong_districts = json.load(file)['districts']  # Access the 'districts' key

#add a new column 
district_mapping = {area: district for district, areas in hong_kong_districts.items() for area in areas}
district_keys = set(hong_kong_districts.keys())

def clean_district_name(d):
    if isinstance(d, str):
        # Always split on both '/' and '|', take the first part
        d_clean = d.split('/')[0].split('|')[0].strip()
        # Normalize apostrophes
        d_clean = d_clean.replace("’", "'").replace("‘", "'")
        # Normalize mapping keys for matching
        norm_keys = {k.replace("’", "'").replace("‘", "'") for k in district_keys}
        if d_clean in norm_keys:
            for k in district_keys:
                if d_clean == k.replace("’", "'").replace("‘", "'"):
                    return k
        norm_mapping = {k.replace("’", "'").replace("‘", "'"): v for k, v in district_mapping.items()}
        return norm_mapping.get(d_clean, None)
    return None

centaline_df['18_district'] = centaline_df['district'].apply(clean_district_name)

# Check and count unmatched districts
unmatched_df = centaline_df[centaline_df['18_district'].isnull()]
print('Number of unmatched rows:', len(unmatched_df))
print('Distinct unmatched district values:')
unmatched_districts = unmatched_df['district'].drop_duplicates()
unmatched_districts = unmatched_districts[unmatched_districts.notnull()]
print(unmatched_districts.to_list())

# print(district_demog_df2.head())

# # #arrange order by district 
# # district_demog_df2.sort_values(by='district')
centaline_df.to_csv('centaline_df.csv', index=False)