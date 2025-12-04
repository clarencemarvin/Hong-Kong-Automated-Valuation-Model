import pandas as pd
import json



# Replace 'your_file.csv' with the path to your CSV file
district_population_path_v1 = r'dirtrict_pop/district_population_v1.xlsx' 
district_population_path_v2 = r'dirtrict_pop/district_population_v2.xlsx' 

# Read the excel file
district_demog_df1 = pd.read_excel(district_population_path_v1, sheet_name=0)  
district_demog_df2 = pd.read_excel(district_population_path_v2, sheet_name=3) 
# Remove the first two rows and assign the result back to district_demog_df2

district_demog_df2 = district_demog_df2.drop(index=0)

# Set the second row (now index 0) as the new header
district_demog_df2.columns = district_demog_df2.iloc[0]

# Drop the row that is now the header (originally the second row)
district_demog_df2 = district_demog_df2.drop(index=district_demog_df2.index[0])

# Reset the index if needed
district_demog_df2.reset_index(drop=True, inplace=True)
# print(district_demog_df2.head(10))
district_demog_df2 = district_demog_df2.drop(index=district_demog_df2.index[174:])
print(district_demog_df2.tail(10))

# Load the dictionary from the text file
with open('dictionary.txt', 'r', encoding='utf-8') as file:
    hong_kong_districts = json.load(file)['districts']  # Access the 'districts' key

#add a new column 
district_mapping = {area: district for district, areas in hong_kong_districts.items() for area in areas}
district_demog_df2['district'] = district_demog_df2['hma_eng'].map(district_mapping)
# print(district_demog_df2.head())

#arrange order by district 
district_demog_df2.sort_values(by='district')

# csv_file_path = 'market_area_summary.csv'
# district_demog_df2.to_csv(csv_file_path, index=False)

