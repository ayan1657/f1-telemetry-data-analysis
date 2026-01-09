def get_telemetry(lap):
    """
    Returns:
    car_data : DataFrame with Speed, Throttle, Brake, Distance
    pos_data : DataFrame with X, Y
    """

    # ✅ Correct FastF1 usage (NO telemetry kwarg)
    car_data = lap.get_car_data()
    car_data = car_data.add_distance()

    pos_data = lap.get_pos_data()

    # 🔒 Validate required channels
    if 'Speed' not in car_data.columns or 'Distance' not in car_data.columns:
        raise RuntimeError(
            f"Telemetry missing required columns. Found: {list(car_data.columns)}"
        )

    return car_data, pos_data
