def get_telemetry(lap):
    """
    Safe telemetry loader for Streamlit + FastF1
    Works across FastF1 versions
    """

    session = lap.session

    # ✅ Always ensure telemetry is loaded (safe to call multiple times)
    session.load(telemetry=True, weather=False, messages=False)

    car_data = lap.get_car_data().add_distance()
    pos_data = lap.get_pos_data()

    if car_data.empty or "Speed" not in car_data.columns:
        raise RuntimeError(
            "Telemetry data not available for this lap. "
            "Try Qualifying (Q) or a different lap."
        )

    return car_data, pos_data
