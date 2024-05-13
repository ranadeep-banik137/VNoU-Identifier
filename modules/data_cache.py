import os
import time
from modules.database import fetch_table_data_in_tuples

# Cached data
cached_data = None
cache_last_updated = 0


def get_data():
    global cached_data
    global cache_last_updated
    cache_expiry_secs = 60 if os.getenv('CACHE_EXPIRATION_IN_SECONDS') is None else os.getenv('CACHE_EXPIRATION_IN_SECONDS')
    # Check if cache is expired or empty
    if time.time() - cache_last_updated > cache_expiry_secs or cached_data is None:
        # Fetch data from the database
        cached_data = fetch_table_data_in_tuples()
        cache_last_updated = time.time()

    return cached_data
