import pandas as pd
import googlemaps
import numpy as np
import time

# --- Step 1: Setup Google Maps Client ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual Google Maps API key.
try:
    gmaps = googlemaps.Client(key='AIzaSyDHzB39PViHWNZP54HyapRwd0s4yBc0M7U')
except Exception as e:
    print(f"Error initializing Google Maps client: {e}")
    print("Please ensure you have replaced 'YOUR_API_KEY' with a valid key.")
    exit()

# --- Step 2: Load the Data ---
try:
    df = pd.read_csv('cleaned_centanet_data_final.csv')
except FileNotFoundError:
    print("Error: 'cleaned_centanet_data_final.csv' not found.")
    print("Please make sure the CSV file is in the same directory as this script.")
    exit()


# --- Step 3: Get Unique Districts to Geocode ---
unique_districts = df['district'].unique()
unique_districts_10 = unique_districts[:10]  # Limit to first 10 for testing
coordinates = {}

print(f"Found {len(unique_districts)} unique districts. Fetching coordinates...")

for district in unique_districts_10:
    # Skip if district is not a valid string
    if not isinstance(district, str):
        print(f"  - Skipping invalid district entry: {district}")
        continue

    try:
        # Construct the query for the Geocoding API
        geocode_query = f"{district}, Hong Kong"

        # Make the API request
        geocode_result = gmaps.geocode(geocode_query)

        if geocode_result:
            # Extract latitude and longitude
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            coordinates[district] = {'latitude': lat, 'longitude': lng}
            print(f"  - {district}: Lat={lat:.4f}, Lng={lng:.4f}")
        else:
            coordinates[district] = {'latitude': np.nan, 'longitude': np.nan}
            print(f"  - WARNING: Could not geocode {district}")

    except Exception as e:
        coordinates[district] = {'latitude': np.nan, 'longitude': np.nan}
        print(f"  - ERROR: An error occurred for {district}: {e}")
    
    # Add a small delay to respect API rate limits
    time.sleep(0.1)


# --- Step 4: Map Coordinates to the DataFrame ---
print("\nMapping coordinates to the DataFrame...")
df['latitude'] = df['district'].map(lambda d: coordinates.get(d, {}).get('latitude'))
df['longitude'] = df['district'].map(lambda d: coordinates.get(d, {}).get('longitude'))


# --- Step 5: Save and Display Results ---
# Save the updated dataframe to a new CSV file
df.to_csv('centanet_data_with_lat_long.csv', index=False)
print("\nSuccessfully created 'centanet_data_with_lat_long.csv'")

# Display the first few rows with the new features
print("\nPreview of the updated data with lat/long:")
print(df[['property_name', 'district', 'latitude', 'longitude']].head())

# Check for any districts that were not geocoded
print("\nDistricts that could not be geocoded (if any):")
print(df[df['latitude'].isnull()]['district'].unique())