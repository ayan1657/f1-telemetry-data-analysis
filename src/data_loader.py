import os
import fastf1

# Create cache directory ONCE at import time
CACHE_DIR = os.path.join(os.getcwd(), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Enable FastF1 cache ONCE
fastf1.Cache.enable_cache(CACHE_DIR)

def load_session(year, race, session_type):
    session = fastf1.get_session(year, race, session_type)
    session.load(telemetry=True)
    return session
