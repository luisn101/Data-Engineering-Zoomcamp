"""@bruin

name: ingestion.trips

materialization:
  type: table
  strategy: append
image: python:3.11

connection: duckdb-default

columns:
  - name: pickup_datetime
    type: timestamp
    description: When the meter was engaged
  - name: dropoff_datetime
    type: timestamp
    description: When the meter was disengaged

@bruin"""

import os
import json
import pandas as pd

def materialize():
    start_date = pd.to_datetime(os.environ["BRUIN_START_DATE"])
    end_date = pd.to_datetime(os.environ["BRUIN_END_DATE"])
    
    vars_dict = json.loads(os.environ.get("BRUIN_VARS", "{}"))
    taxi_types = vars_dict.get("taxi_types", ["yellow"])

    all_data = [] # <--- Asegúrate que esté alineado con vars_dict

    for taxi_type in taxi_types:
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_2022-01.parquet"
        
        print(f"Downloading data for {taxi_type}...")
        df = pd.read_parquet(url)
        
        df["taxi_type"] = taxi_type

        # Todo este bloque debe estar DENTRO del for (8 espacios)
        rename_map = {
            "tpep_pickup_datetime": "pickup_datetime",
            "tpep_dropoff_datetime": "dropoff_datetime",
            "PULocationID": "pickup_location_id",
            "DOLocationID": "dropoff_location_id",
            "payment_type": "payment_type"
        }
        df = df.rename(columns=rename_map)
        
        all_data.append(df)

    # Esto va fuera del for (al mismo nivel que all_data)
    final_dataframe = pd.concat(all_data, ignore_index=True)
    return final_dataframe