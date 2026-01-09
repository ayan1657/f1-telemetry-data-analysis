# 🏎️ Formula 1 Telemetry Analysis Dashboard

An interactive data analytics dashboard for exploring **Formula 1 telemetry data** using **Python, FastF1, and Streamlit**.  
This project enables **corner-by-corner**, **lap-by-lap**, and **strategy-level** performance comparisons between F1 drivers.

---

## 🚀 Project Overview

This application analyzes publicly available Formula 1 telemetry data to uncover **performance differences**, **driving styles**, and **race strategies**.

Users can:
- Compare two drivers on selected laps
- Visualize speed, throttle, braking, and delta time
- Identify strongest sectors and critical corners
- Analyze tyre compounds and race strategies
- View automatically generated performance insights

The dashboard is designed to feel **broadcast-grade**, **intuitive**, and **insight-driven**, making complex telemetry data accessible even to non-technical users.

---

## 🧠 Key Capabilities

### 🔍 Telemetry Analysis
- Speed vs Distance
- Throttle vs Distance
- Delta Time across the lap
- Sector-wise performance comparison
- Corner-by-corner delta impact

### 🗺️ Track & Corner Analysis
- Racing line overlay using GPS data
- Automatic corner detection
- Visual markers showing time gained or lost per corner

### 🛞 Tyre & Strategy Analysis
- Fastest and slowest lap identification
- Tyre compound detection per lap
- Tyre strategy timeline (stint-based, in race order)
- Tyre usage overview with lap ranges and stint lengths
- Compound color coding (F1 broadcast style)

### 🧠 Auto-Generated Insights
- Overall lap winner
- Strongest sector for the winning driver
- Biggest corner time swing
- Natural-language insights generated dynamically from telemetry data

---

## 🧰 Tools & Technologies

- **Python 3.10**
- **FastF1** (official open F1 telemetry API)
- **Streamlit** (interactive dashboard)
- **Pandas & NumPy** (data processing)
- **Matplotlib** (visualization)
- **Git & GitHub** (version control & deployment)

---

## 🗂️ Project Structure

f1-telemetry-data-analysis/
│
├── app.py # Main Streamlit dashboard
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── src/
│ ├── data_loader.py # Session & data loading logic
│ ├── telemetry_utils.py# Telemetry extraction helpers
│ └── delta_utils.py # Delta & sector calculations
│
├── notebooks/ # Exploratory analysis (development)
└── .gitignore



---

## 📊 Data Source & Limitations

- Telemetry data is sourced via **FastF1**, which uses publicly available broadcast data.
- Some laps may have **missing or invalid tyre compound information** due to:
  - Pit laps (in-laps / out-laps)
  - Incomplete broadcast telemetry
  - Data unavailability from the source

Such gaps are **handled gracefully** and clearly indicated in the dashboard to avoid user confusion.

---

## 🌐 Deployment

The application is deployed on **Streamlit Cloud** and can be accessed directly via the browser.

> No local setup required for end users.

---

## 🔮 Roadmap (Planned Enhancements)

- Qualifying vs Race mode comparison
- Driver consistency metrics
- Braking efficiency scoring
- Exportable reports (PDF / images)
- Public “Insight of the Day” feed for social media
- Pro version with advanced analytics (future)

---

## 👤 Author

**Mohammed Ayan**  
B.Tech CSE | Data Science & Analytics  
Passionate about motorsport analytics, telemetry, and performance engineering.

---

## ⚠️ Disclaimer

This project is for **educational and analytical purposes only**.  
It uses **non-proprietary, publicly accessible telemetry data** and is not affiliated with Formula 1, FIA, or any F1 team.

---
