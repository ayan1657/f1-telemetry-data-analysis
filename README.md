🏎️ Formula 1 Telemetry & Performance Analysis Dashboard

An interactive motorsport data analytics dashboard built using Python, FastF1, and Streamlit to analyze Formula 1 telemetry data.

The project focuses on lap time performance, driver behavior, and race strategy insights, similar to tools used by performance engineers and race strategists.

🚀 Project Overview

This dashboard analyzes publicly available Formula 1 telemetry to identify where and why lap time is gained or lost.

It enables:

Direct performance comparison between drivers

Visualization of lap-by-lap and corner-level deltas

Evaluation of tyre usage and stint strategies

Insight generation to support race strategy decisions

The goal is to transform raw telemetry into actionable performance insights, not just visualizations.

❓ Key Questions This Project Answers

Where does one driver gain or lose lap time compared to another?

How does tyre choice and stint length affect race pace?

Which sectors and corners have the highest performance impact?

How does qualifying pace translate into race performance?

These questions mirror the analysis performed in real-world motorsport environments.

🧠 Core Analytical Capabilities
Telemetry & Lap Analysis

Speed, throttle, and braking comparison across laps

Delta time visualization over lap distance

Sector-wise performance breakdown

Track & Corner-Level Analysis

GPS-based racing line overlays

Corner detection and time-loss visualization

Identification of critical corners influencing lap time

Tyre & Strategy Analysis

Tyre compound detection and stint visualization

Strategy timeline showing compound usage and stint lengths

Fastest and slowest lap identification per stint

Automated Performance Insights

Lap winner identification

Strongest sector detection

Largest corner-level time delta

Natural-language insights generated from telemetry trends

🧰 Tools & Technologies

Python

FastF1 (public F1 telemetry data)

Streamlit (interactive dashboards)

Pandas & NumPy (data processing)

Matplotlib (visualization)

📊 Data Source & Analytical Limitations

Telemetry is sourced from public broadcast data via FastF1

High-frequency sensor data, fuel load, and car setup parameters are not available

Pit in-laps and out-laps may contain incomplete tyre information

These constraints reflect real-world scenarios where analysts must work with partial or imperfect data.

🔮 Future Enhancements

Predictive tyre degradation modeling

Driver consistency metrics across race stints

Qualifying vs race pace comparison

Exportable performance reports

👤 Author

Mohammed Ayan
B.Tech Computer Science (Data Science)
Aspiring motorsport data & performance analyst

⚠️ Disclaimer

This project is for educational and analytical purposes only and uses non-proprietary public telemetry data.
It is not affiliated with Formula 1, the FIA, or any Formula 1 team.