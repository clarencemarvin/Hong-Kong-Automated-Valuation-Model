import pandas as pd
import googlemaps
from datetime import datetime
import numpy as np
import time

"""
Google Maps Feature Engineering Final Script
"""

# --- Step 1: Setup Google Maps Client ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual Google Maps API key.
try:
    gmaps = googlemaps.Client(key='AIzaSyDHzB39PViHWNZP54HyapRwd0s4yBc0M7U')
except Exception as e:
    print(f"Error initializing Google Maps client: {e}")
    exit()

# --- Step 2: Load the Data ---
try:
    # Using the correct filename that was uploaded
    df = pd.read_csv('cleaned_data/cleaned_centanet_data.csv')
except FileNotFoundError:
    print("Error: 'cleaned_centanet_data.csv' not found.")
    exit()

# --- For testing, uncomment the next line to run on a small sample ---
#df = df.head(5).copy()

# --- Step 3: Define Parameters & POI Configuration ---
central_location = "Central, Hong Kong"
now = datetime.now()
weekday_commute_time = datetime(now.year, now.month, now.day, 8, 0, 0)

# *** MODIFIED: Define categories with their specific search radius ***
POI_CONFIG = {
    'school_count': {'types': ['primary_school', 'secondary_school', 'university'], 'radius': 2000},
    'hospital_count': {'types': ['hospital'], 'radius': 2000},
    'park_count': {'types': ['park'], 'radius': 1000},
    'shopping_mall_count': {'types': ['shopping_mall'], 'radius': 1000}
}

# --- Step 4: Process Each Property Row by Row ---
print(f"Starting to process {len(df)} properties individually. This may take a while.")

results = []

for index, row in df.iterrows():
    # Initialize a dictionary to hold all data for the current row
    poi_columns = {f'{k}_{v["radius"]}m': np.nan for k, v in POI_CONFIG.items()}
    row_data = {
        'latitude': np.nan, 'longitude': np.nan, 'travel_time_to_cbd': np.nan,
        'walking_time_to_mtr': np.nan, **poi_columns
    }
    
    origin_query = f"{row['property_name']}, {row['district']}, Hong Kong"
    print(f"\nProcessing row {index + 1}: {row['property_name']}")

    try:
        # --- API Call 1: Get Latitude and Longitude for the property ---
        geocode_result = gmaps.geocode(origin_query)
        if not geocode_result:
            print(f"  - WARNING: Could not geocode. Skipping.")
            results.append(row_data)
            continue
        
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        row_data['latitude'] = lat
        row_data['longitude'] = lng
        origin_coords = (lat, lng)
        print(f"  - Geocoded: Lat={lat:.4f}, Lng={lng:.4f}")

        # --- API Call 2: Get Travel Time to CBD (Transit) ---
        directions_to_cbd = gmaps.directions(origin_coords, central_location, mode="transit", departure_time=weekday_commute_time)
        if directions_to_cbd:
            row_data['travel_time_to_cbd'] = round(directions_to_cbd[0]['legs'][0]['duration']['value'] / 60)
            print(f"  - Transit time to CBD: {row_data['travel_time_to_cbd']} minutes")

        # --- API Call 3: Find Nearest MTR Station ---
        nearby_mtr = gmaps.places_nearby(location=origin_coords, rank_by='distance', type='subway_station')
        if nearby_mtr and nearby_mtr.get('results'):
            station_coords = nearby_mtr['results'][0]['geometry']['location']
            
            # --- API Call 4: Get Walking Time to Nearest MTR ---
            directions_to_mtr = gmaps.directions(origin_coords, (station_coords['lat'], station_coords['lng']), mode="walking")
            if directions_to_mtr:
                row_data['walking_time_to_mtr'] = round(directions_to_mtr[0]['legs'][0]['duration']['value'] / 60)
                print(f"  - Walking time to MTR: {row_data['walking_time_to_mtr']} minutes")

        # --- API Calls 5+: Count Nearby Amenities with variable radius ---
        print("  - Counting nearby amenities...")
        for category_name, config in POI_CONFIG.items():
            total_places = 0
            radius = config['radius']
            place_types = config['types']
            for place_type in place_types:
                response = gmaps.places_nearby(location=origin_coords, radius=radius, type=place_type)
                total_places += len(response.get('results', []))
                time.sleep(0.05)
            
            column_name = f'{category_name}_{radius}m'
            row_data[column_name] = total_places
            print(f"    - Found {total_places} for '{category_name}' within {radius}m")

    except Exception as e:
        print(f"  - ERROR: An unexpected error occurred: {e}")
    
    results.append(row_data)

# --- Step 5: Merge New Features with Original DataFrame ---
print("\nMerging all new features back into the DataFrame...")
results_df = pd.DataFrame(results)
df_final = pd.concat([df.reset_index(drop=True), results_df], axis=1)

# --- Step 6: Save and Display Results ---
df_final.to_csv('centanet_data_final.csv', index=False)
print("\nSuccessfully created 'centanet_data_final.csv'")

# Display a preview of the new columns
columns_to_show = [
    'property_name', 'latitude', 'longitude', 'travel_time_to_cbd', 'walking_time_to_mtr',
    f'school_count_{POI_CONFIG["school_count"]["radius"]}m',
    f'park_count_{POI_CONFIG["park_count"]["radius"]}m',
    f'hospital_count_{POI_CONFIG["hospital_count"]["radius"]}m',
    f'shopping_mall_count_{POI_CONFIG["shopping_mall_count"]["radius"]}m'
]
print("\nPreview of the final data:")
print(df_final[columns_to_show].head())