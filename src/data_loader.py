import os
import fastf1

CACHE_DIR = os.path.join(os.getcwd(), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)

def load_session(year, race, session_type):
    session = fastf1.get_session(year, race, session_type)
    session.load(telemetry=True, weather=False, messages=False)
    return session
