import json
import pandas as pd
import argparse
import sys

def geojson_to_csv(input_path, output_path):
    """
    Converts a GeoJSON file to a CSV file.

    Extracts properties from each feature. If the geometry is a Point,
    it adds 'longitude' and 'latitude' columns to the CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # Ensure the GeoJSON is a FeatureCollection
        if geojson_data.get('type') != 'FeatureCollection':
            print("Error: Input file must be a GeoJSON FeatureCollection.", file=sys.stderr)
            return

        rows = []
        for feature in geojson_data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry')

            # If geometry is a Point, extract coordinates
            if geometry and geometry.get('type') == 'Point':
                coords = geometry.get('coordinates')
                if coords and len(coords) >= 2:
                    properties['longitude'] = coords[0]
                    properties['latitude'] = coords[1]
            
            rows.append(properties)

        if not rows:
            print("Warning: No features found in the GeoJSON file.")
            return

        # Convert the list of property dictionaries to a DataFrame
        df = pd.DataFrame(rows)

        # Write the DataFrame to a CSV file
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Successfully converted {input_path} to {output_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a GeoJSON file to a CSV file, extracting feature properties and Point coordinates."
    )
    parser.add_argument("input_file", help="Path to the input GeoJSON file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    
    args = parser.parse_args()
    
    geojson_to_csv(args.input_file, args.output_file)
