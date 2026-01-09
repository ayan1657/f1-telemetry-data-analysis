import os
import fastf1

def load_session(year, race, session_type):
    # Always create cache directory safely
    cache_dir = os.path.join(os.getcwd(), "cache")
    os.makedirs(cache_dir, exist_ok=True)

    fastf1.Cache.enable_cache(cache_dir)

    session = fastf1.get_session(year, race, session_type)
    session.load(telemetry=True)

    return session
