import numpy as np
import pandas as pd
import math
import civis
import json

#lee = [948327, 947318, 948329] 

print("here")

client = civis.APIClient()

sql = "SELECT * FROM analytics_ia.precinct_data"
df = client.read_civis_sql(sql, "Warren for MA", use_pandas=True)