import pandas as pd
import re

def main():
    # Load the full seized properties CSV
    df = pd.read_csv('../seized_properties_combined.csv', header=None, names=['id','address','full_address','lat','lon','address_norm','status','type'])

    # Filter for Morskoy 46 apartments (canonical format)
    df46 = df[df['address'].str.contains('д. 46', na=False) & df['address'].str.contains('Комсомольский', na=False)]
    
    # Extract apartment number
    df46['apartment'] = df46['address'].str.extract(r'кв\\.? ?(\\d+)')
    df46['apartment'] = pd.to_numeric(df46['apartment'], errors='coerce')
    
    # Assign entrance based on apartment number
    def entrance(ap):
        try:
            ap = int(ap)
            if 1 <= ap <= 54:
                return 1
            elif 55 <= ap <= 108:
                return 2
            elif 109 <= ap <= 164:
                return 3
            elif 165 <= ap <= 190:
                return 4
            else:
                return None
        except:
            return None
    df46['entrance'] = df46['apartment'].apply(entrance)
    
    # Mark all as occupied
    df46['occupied'] = True
    
    # Output summary table
    df46[['apartment','entrance','occupied','status']].sort_values(['entrance','apartment']).to_csv('Morskoy46_apartment_entrance_summary.csv', index=False)

if __name__ == '__main__':
    main()
