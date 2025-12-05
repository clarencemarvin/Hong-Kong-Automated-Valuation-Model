import pandas as pd
import numpy as np
from scipy.spatial import KDTree

# --- 1. Load the Datasets ---
try:
    print("Loading datasets...")
    df_housing = pd.read_csv('txn_df_easting_northing.csv')
    df_poi = pd.read_csv('GeoCom.csv')
except FileNotFoundError as e:
    print(f"Error loading files: {e}. Please ensure the correct files are in the directory.")
    exit()

# --- 2. Prepare and Clean the Data ---
print("Preparing data...")
df_housing.dropna(subset=['easting', 'northing'], inplace=True)
df_poi.dropna(subset=['EASTING', 'NORTHING', 'CLASS', 'TYPE'], inplace=True)

for col in ['easting', 'northing']:
    df_housing[col] = pd.to_numeric(df_housing[col], errors='coerce')
for col in ['EASTING', 'NORTHING']:
    df_poi[col] = pd.to_numeric(df_poi[col], errors='coerce')
df_housing.dropna(subset=['easting', 'northing'], inplace=True)
df_poi.dropna(subset=['EASTING', 'NORTHING'], inplace=True)

housing_coords = df_housing[['easting', 'northing']].to_numpy()

# --- 3. Configuration Section (More Specific) ---

# Define specific CLASS and TYPE combinations for each category
# 'types': None means all types within that class are included
CATEGORY_CONFIG = {
    'Community_Facilities': {
        'filters': [
            {'class': 'COM', 'types': ['CMC']}
        ],
        'radius': 1000
    },
    'Education': {
        'filters': [
            {'class': 'SCH', 'types': None} # All types
        ],
        'radius': 2000
    },
    'Recreation': {
        'filters': [
            {'class': 'RSF', 'types': ['PAR', 'PLG', 'TCT', 'BAS', 'ICR', 'IGH', 'SGD', 'STD', 'GCO', 'RGD', 'SPL', 'BWG', 'SCO']}
        ],
        'radius': 1000
    },
    'Medical': {
        'filters': [
            {'class': 'HNC', 'types': ['HOS', 'CLI']}
        ],
        'radius': 2000
    },
    'Public_Market': {
        'filters': [
            {'class': 'MUF', 'types': ['CFS', 'MKT']}
        ],
        'radius': 1000
    },
    'Religion': {
        'filters': [
            {'class': 'REM', 'types': ['CHU', 'TMP', 'MON']}
        ],
        'radius': 2000
    },
    'Transportation': {
        'filters': [
            {'class': 'BUS', 'types': None}, # All BUS types
            {'class': 'TRS', 'types': ['MTA', 'LRA']}
        ],
        'radius': 1000
    },
    'Tourism': {
        'filters': [
            {'class': 'TRH', 'types': ['SIG']}
        ],
        'radius': 2000
    }
}

TOTAL_POI_RADIUS = 1000 # Set to 1km as requested

# --- 4. Calculation Functions ---
def calculate_poi_counts(housing_coords, poi_df, radius):
    """Calculates the number of POIs within a given radius for each housing coordinate."""
    if poi_df.empty:
        return np.zeros(len(housing_coords), dtype=int)
    kdtree = KDTree(poi_df[['EASTING', 'NORTHING']].to_numpy())
    indices = kdtree.query_ball_point(housing_coords, r=radius)
    return np.array([len(result) for result in indices])

def get_filtered_poi_df(poi_df, filters):
    """Filters the POI dataframe based on a list of class/type rules."""
    # Create a boolean mask for each filter rule and combine them with an OR condition
    masks = []
    for f in filters:
        class_mask = (poi_df['CLASS'] == f['class'])
        if f['types'] is not None:
            type_mask = (poi_df['TYPE'].isin(f['types']))
            masks.append(class_mask & type_mask)
        else:
            masks.append(class_mask) # Apply only the class filter
            
    # Combine all individual masks with a logical OR
    combined_mask = pd.concat(masks, axis=1).any(axis=1)
    return poi_df[combined_mask]

# --- 5. Execute Feature Creation ---

# A. Total POI Count (Radius 1km)
print(f"\n--- Calculating Total POIs (Radius: {TOTAL_POI_RADIUS}m) ---")
df_housing[f'total_poi_within_{TOTAL_POI_RADIUS}m'] = calculate_poi_counts(housing_coords, df_poi, TOTAL_POI_RADIUS)

# B. Counts per your new specific category division
print("\n--- Calculating Counts per Specific Category ---")
for category_name, details in CATEGORY_CONFIG.items():
    radius = details['radius']
    filters = details['filters']
    print(f"Processing Category: {category_name} (Radius: {radius}m)...")
    
    # Get the subset of POIs matching the specific class/type filters
    df_category_poi = get_filtered_poi_df(df_poi, filters)
    
    # Calculate counts and add to the main dataframe
    column_name = f'category_{category_name}_within_{radius}m'
    df_housing[column_name] = calculate_poi_counts(housing_coords, df_category_poi, radius)

# C. Special MTR Proximity Feature (in KM)
print(f"\n--- Calculating Distance to Nearest MTR Station (in km) ---")
df_mtr = df_poi[(df_poi['CLASS'] == 'TRS') & (df_poi['TYPE'] == 'MTA')]
if not df_mtr.empty:
    kdtree_mtr = KDTree(df_mtr[['EASTING', 'NORTHING']].to_numpy())
    distances, _ = kdtree_mtr.query(housing_coords, k=1)
    # Convert meters to kilometers
    df_housing['distance_to_nearest_mtr_km'] = distances / 1000
else:
    df_housing['distance_to_nearest_mtr_km'] = np.inf

# --- 6. Finalizing the Dataset ---
# Create a list of the new feature columns to keep, plus identifiers
new_feature_columns = (
    [f'total_poi_within_{TOTAL_POI_RADIUS}m'] +
    [f'category_{name}_within_{details["radius"]}m' for name, details in CATEGORY_CONFIG.items()] +
    ['distance_to_nearest_mtr_km']
)

# You may want to keep some original columns for identification
# Let's assume you want to keep all original columns and just add the new ones
# If you want ONLY the new features plus some identifiers, you would do this:
# id_cols = ['property_name', 'easting', 'northing'] # Example identifiers
# df_final = df_housing[id_cols + new_feature_columns]
df_final = df_housing # For this example, we keep all original columns

# --- 7. Save the Final Enriched Dataset ---
output_filename = 'txn_df_v2.csv'
df_final.to_csv(output_filename, index=False)
print(f"\n✅ All done! Enriched data saved to '{output_filename}'")

# --- 8. Display Preview ---
print("\nPreview of the new features:")
preview_cols = [col for col in df_final.columns if col in ['property_name'] + new_feature_columns]
print(df_final[preview_cols].head())