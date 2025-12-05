import pandas as pd
import re
import numpy as np

# --- Helper Function for Attribute Cleaning ---
def clean_attributes(attribute_str):
    """
    Cleans the attribute column by replacing newlines,
    finding unique values, and joining them into a single string.
    """
    if not isinstance(attribute_str, str):
        return '' # Return an empty string if data is not a string

    # Split the string by newline, strip whitespace from each part
    attributes = [attr.strip() for attr in attribute_str.split('\n')]
    
    # Get unique attributes while preserving order
    unique_attributes = list(dict.fromkeys(attributes))
    
    # Join them back with a comma and space
    return ', '.join(unique_attributes)


# --- Main Script ---

# 1. Load the original dataset
try:
    # Use encoding='utf-8' to prevent character issues
    df = pd.read_csv('raw_data/centanet_data_2.csv', encoding='utf-8')
    print("✅ Successfully loaded centanet_data_2.csv")
except FileNotFoundError:
    print("❌ Error: 'centanet_data_2.csv' not found. Please make sure the script is in the same folder as your data file.")
    exit()

# 2. Clean 'property_name' and 'distance' columns
df['property_name'] = df['property_name'].str.replace('・', ' ', regex=False)
df['distance'] = df['distance'].str.replace('·', '', regex=False)
print("✅ Cleaned text columns.")


# 3. Clean the 'attribute' column for Excel compatibility
print("🔧 Cleaning the 'attribute' column for better display...")
df['attribute'] = df['attribute'].apply(clean_attributes)


# 4. Correct and clean bedroom count information
room_pattern = r'\d+\s*Rooms?'
cleaned_count = 0
for index, row in df.iterrows():
    if pd.isna(row['bedroom_count']) or str(row['bedroom_count']).strip() == '':
        if isinstance(row['unit'], str) and re.search(room_pattern, row['unit']):
            room_count = re.search(r'(\d+)', row['unit']).group(1)
            df.at[index, 'bedroom_count'] = room_count
            df.at[index, 'unit'] = re.sub(room_pattern, '', row['unit'], flags=re.IGNORECASE).strip()
            cleaned_count += 1
        elif isinstance(row['floor'], str) and re.search(room_pattern, row['floor']):
            room_count = re.search(r'(\d+)', row['floor']).group(1)
            df.at[index, 'bedroom_count'] = room_count
            df.at[index, 'floor'] = re.sub(room_pattern, '', row['floor'], flags=re.IGNORECASE).strip()
            cleaned_count += 1
print(f"✅ Corrected and cleaned {cleaned_count} bedroom records.")

# 5. Correct misplaced flat information
misplaced_flat_condition = (
    (df['unit'].isnull()) | (df['unit'].str.strip() == '')
) & (
    df['floor'].str.contains('FLAT', na=False, case=False)
)
fix_count = misplaced_flat_condition.sum()
df.loc[misplaced_flat_condition, 'unit'] = df.loc[misplaced_flat_condition, 'floor']
df.loc[misplaced_flat_condition, 'floor'] = ''
print(f"✅ Moved misplaced flat info for {fix_count} records.")

# 6. Final clean-up for leftover 's' characters
df['unit'] = df['unit'].replace(r'^\s*s\s*$', '', regex=True)
df['floor'] = df['floor'].replace(r'^\s*s\s*$', '', regex=True)
print("✅ Performed final clean-up of leftover characters.")

# 7. Convert columns to numeric types before filtering
print("🔧 Converting data types for filtering...")
numeric_cols_to_filter = ['price', 'bedroom_count', 'property_age', 'saleable_area']
for col in numeric_cols_to_filter:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 8. Filter out rows with incomplete data or small area
print("🧹 Filtering data based on your criteria...")
initial_rows = len(df)

# Define the columns that cannot be empty (ADDED 'distance' HERE)
required_data_cols = ['price', 'bedroom_count', 'district', 'property_age', 'saleable_area']

# Replace empty strings in 'distance' with NaN so dropna() catches them
df['distance'] = df['distance'].replace(r'^\s*$', np.nan, regex=True)

# Drop rows missing essential data
df.dropna(subset=required_data_cols, inplace=True)

# Filter for properties with a saleable area greater than 100
df = df[df['saleable_area'] > 100].copy()
final_rows = len(df)
print(f"✅ Removed {initial_rows - final_rows} rows that did not meet the criteria.")

# 9. Save the final cleaned and filtered data
df.to_csv('cleaned_data/cleaned_centanet_data.csv', index=False)
print("\n✨ Data cleaning, formatting, and filtering complete!")
print("The final dataset has been saved to 'cleaned_data/cleaned_and_filtered_centanet_data.csv'")