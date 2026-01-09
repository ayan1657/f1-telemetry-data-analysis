import os
import fastf1

def load_session(year, race, session_type):
    # Use Streamlit Cloud env var if available, else fallback
    cache_dir = os.getenv("FASTF1_CACHE_DIR", "cache")

    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    fastf1.Cache.enable_cache(cache_dir)

    session = fastf1.get_session(year, race, session_type)
    session.load(telemetry=True)
    return session
