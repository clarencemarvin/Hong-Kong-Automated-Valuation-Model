import pandas as pd
import json

# Replace 'your_file.csv' with the path to your CSV file
sale_df = pd.read_csv('map/merged_housing_data.csv')
print(sale_df.head())


# Load the dictionary from the text file
with open('dictionary.txt', 'r', encoding='utf-8') as file:
    hong_kong_districts = json.load(file)['districts']  # Access the 'districts' key

#add a new column 
district_mapping = {area: district for district, areas in hong_kong_districts.items() for area in areas}
district_keys = set(hong_kong_districts.keys())

def clean_district_name(d):
    if isinstance(d, str):
        d_clean = d.split('/')[0].strip() if '/' in d else d.strip()
        if d_clean in district_keys:
            return d_clean
        return district_mapping.get(d_clean, None)
    return None

sale_df['main_district'] = sale_df['district'].apply(clean_district_name)

# Check and count unmatched districts
unmatched_df = sale_df[sale_df['district'].isnull()]
print('Number of unmatched rows:', len(unmatched_df))
print('Distinct unmatched District values:')
unmatched_districts = unmatched_df['district'].drop_duplicates()
unmatched_districts = unmatched_districts[unmatched_districts.notnull()]
print(unmatched_districts.to_list())

sale_df['price_per_sqft'] = sale_df['price'] / sale_df['saleable_area']

# #arrange order by district 
sale_df['housing_market_area'] = sale_df['district']
sale_df = sale_df[['main_district', 'housing_market_area', 'price', 'saleable_area', 'price_per_sqft', 'latitude', 'longitude', 'bedroom_count', 'property_age']]

print(sale_df.head())
# district_demog_df2.sort_values(by='district')
sale_df.to_csv('txn_df.csv', index=False)