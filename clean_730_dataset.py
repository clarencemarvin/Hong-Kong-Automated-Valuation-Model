import pandas as pd
import re

# Load the dataset
df = pd.read_csv('raw_data/sale_df_v2.csv')

# Make a copy for cleaning
df_cleaned = df.copy()

# ---- MODIFICATION 1: Drop specified columns ----
columns_to_drop = ['Gross Floor Area', 'Gross Floor Area Price per sq.ft.']
df_cleaned.drop(columns=columns_to_drop, inplace=True, errors='ignore')


# 1. Clean numeric variables
# Price column
df_cleaned['Price'] = df_cleaned['Price'].str.replace(r'Sale \$', '', regex=True).str.replace('M', '').str.strip()
df_cleaned['Price'] = pd.to_numeric(df_cleaned['Price'], errors='coerce') * 1000000
df_cleaned.rename(columns={'Price': 'Price ($)'}, inplace=True)

# Saleable Area column
df_cleaned['Saleable Area'] = df_cleaned['Saleable Area'].str.replace(r'SA', '', regex=True).str.replace('sq.ft.', '', regex=True).str.strip()
df_cleaned['Saleable Area'] = pd.to_numeric(df_cleaned['Saleable Area'], errors='coerce')
df_cleaned.rename(columns={'Saleable Area': 'Saleable Area (sq.ft.)'}, inplace=True)

# Room Count column
df_cleaned['Room Count'] = df_cleaned['Room Count'].str.replace(r'Room\(s\)', '', regex=True).str.strip()
df_cleaned['Room Count'] = pd.to_numeric(df_cleaned['Room Count'], errors='coerce')

# Bathroom Count column
df_cleaned['Bathroom Count'] = df_cleaned['Bathroom Count'].str.replace(r'Bathroom\(s\)', '', regex=True).str.strip()
df_cleaned['Bathroom Count'] = pd.to_numeric(df_cleaned['Bathroom Count'], errors='coerce')

# Convert columns that should be whole numbers to nullable integer type
integer_columns = ['Price ($)', 'Saleable Area (sq.ft.)', 'Room Count', 'Bathroom Count']
for col in integer_columns:
    if col in df_cleaned.columns:
        # Convert to numeric, coerce errors to NaN
        numeric_series = pd.to_numeric(df_cleaned[col], errors='coerce')
        # Round to 0 decimal places and then convert to nullable Integer
        df_cleaned[col] = numeric_series.round(0).astype('Int64')

# Ensure 'Saleable Area Price per sq.ft.' is numeric, but allow it to be a float
if 'Saleable Area Price per sq.ft.' in df_cleaned.columns:
    df_cleaned['Saleable Area Price per sq.ft.'] = pd.to_numeric(df_cleaned['Saleable Area Price per sq.ft.'], errors='coerce')


# 2. Extract year from 'matched_NSEARCH3_E'
df_cleaned['matched_NSEARCH3_E_year'] = pd.to_datetime(df_cleaned['matched_NSEARCH3_E'], errors='coerce').dt.year
df_cleaned['matched_NSEARCH3_E_year'] = df_cleaned['matched_NSEARCH3_E_year'].astype('Int64')


# ---- MODIFICATION 2: Drop rows which are missing a key variable ----
key_variables = [
    'Property ID', 'District', 'property_name', 'Price ($)',
    'Saleable Area (sq.ft.)', 'Saleable Area Price per sq.ft.',
    'Room Count', 'Bathroom Count'
]
# We check if the columns exist before trying to drop NaNs from them
existing_key_vars = [col for col in key_variables if col in df_cleaned.columns]
df_cleaned.dropna(subset=existing_key_vars, inplace=True)


# Save the cleaned dataframe to a new CSV file.
df_cleaned.to_csv('cleaned_data/cleaned_sale_df.csv', index=False)

print("Data cleaning is complete. The cleaned data is saved in 'cleaned_sale_df.csv'.")
print("Cleaned data head:")
print(df_cleaned.head())