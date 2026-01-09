import numpy as np

def compute_delta_time(tel_a, tel_b, n_points=1000):
    """
    Computes delta time using distance + speed interpolation
    """

    # Safety checks
    for col in ['Distance', 'Speed']:
        if col not in tel_a.columns or col not in tel_b.columns:
            raise RuntimeError(
                f"Telemetry does not contain required channel '{col}'"
            )

    # Common distance axis
    common_distance = np.linspace(
        max(tel_a['Distance'].min(), tel_b['Distance'].min()),
        min(tel_a['Distance'].max(), tel_b['Distance'].max()),
        n_points
    )

    # Convert km/h → m/s
    speed_a = np.interp(common_distance, tel_a['Distance'], tel_a['Speed']) / 3.6
    speed_b = np.interp(common_distance, tel_b['Distance'], tel_b['Speed']) / 3.6

    # Avoid division by zero
    speed_a[speed_a <= 0] = np.nan
    speed_b[speed_b <= 0] = np.nan

    segment = common_distance[1] - common_distance[0]

    time_a = np.nancumsum(segment / speed_a)
    time_b = np.nancumsum(segment / speed_b)

    delta = time_b - time_a

    return common_distance, delta

def compute_sector_deltas(distance, delta):
    """
    Splits delta time into 3 distance-based sectors.
    Returns dict with sector-wise delta.
    """

    total_distance = distance.max()

    s1_end = total_distance / 3
    s2_end = 2 * total_distance / 3

    # Find nearest indices
    s1_idx = (distance >= s1_end).argmax()
    s2_idx = (distance >= s2_end).argmax()
    s3_idx = -1

    sector_deltas = {
        "Sector 1": delta[s1_idx],
        "Sector 2": delta[s2_idx] - delta[s1_idx],
        "Sector 3": delta[s3_idx] - delta[s2_idx]
    }

    return sector_deltas

