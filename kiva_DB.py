import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB (local instance)
client = MongoClient('mongodb://localhost:27017/')
db = client['kiva_loans_db']

def import_csv(file_path, collection_name):
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Convert date columns if they exist in 'loans'
    if 'POSTED_TIME' in df.columns:
        df['POSTED_TIME'] = pd.to_datetime(df['POSTED_TIME'])
    
    # Convert DataFrame to dictionary for MongoDB
    data = df.to_dict(orient='records')
    
    # Insert into collection
    db[collection_name].insert_many(data)
    print(f"Successfully imported {len(data)} records into {collection_name}")

# Import all files
import_csv('loans.csv', 'loans')
import_csv('lenders.csv', 'lenders')
import_csv('loans_lenders.csv', 'loans_mapping')