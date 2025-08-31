import json
import pandas as pd
import argparse
import sys
from pathlib import Path

def geojson_to_csv(input_path, output_path):
    """
    Converts a GeoJSON file to a CSV file.

    Extracts properties from each feature. If the geometry is a Point,
    it adds 'longitude' and 'latitude' columns to the CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

    # Ensure the GeoJSON is a FeatureCollection
    if geojson_data.get('type') != 'FeatureCollection':
        raise ValueError("Input file must be a GeoJSON FeatureCollection")

    features = geojson_data.get('features', [])
    if not features:
        raise ValueError("No features found in GeoJSON file")
    
    rows = []
    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry')

        # If geometry is a Point, extract coordinates
        if geometry and geometry.get('type') == 'Point':
            coords = geometry.get('coordinates')
            if coords and len(coords) >= 2:
                properties['longitude'] = coords[0]
                properties['latitude'] = coords[1]
        
        rows.append(properties)

    # Convert the list of property dictionaries to a DataFrame
    df = pd.DataFrame(rows)

    # Write the DataFrame to a CSV file
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert .geojson files to .csv. Retains filename but changes the extension to .csv"
    )
    parser.add_argument(
        "input_files",
        nargs='+', 
        help="Path(s) to the input GeoJSON file."
    )
    
    args = parser.parse_args()

    # Loop through files
    for file_path in args.input_files:
        input_path = Path(file_path)
        output_path = input_path.with_suffix('.csv')

        try:
            geojson_to_csv(input_path, output_path)
            print(f"Successfully converted {input_path} to {output_path}")
        except FileNotFoundError:
            print(f"Error: Input file not found at '{input_path}'", file=sys.stderr)
            sys.exit(1)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error processing file: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)
