# =========================
# Imports
# =========================
import os
os.environ["FASTF1_DISABLE_TIMING_PATCH"] = "1"

import matplotlib
matplotlib.use("Agg")

import matplotlib as mpl
mpl.rcParams["axes.formatter.useoffset"] = False
mpl.rcParams["axes.formatter.use_mathtext"] = False

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import fastf1



TEAM_COLORS = {
    "Red Bull Racing": "#1E41FF",
    "Ferrari": "#DC0000",
    "Mercedes": "#00D2BE",
    "McLaren": "#FF8700",
    "Aston Martin": "#006F62",
    "Alpine": "#0090FF",
    "Williams": "#005AFF",
    "AlphaTauri": "#2B4562",
    "Alfa Romeo": "#900000",
    "Haas F1 Team": "#B6BABD"
}

# =========================
# Tyre Compound Colors (F1 Broadcast Style)
# =========================
TYRE_COLORS = {
    "SOFT": "#FF3333",          # Red
    "MEDIUM": "#FFD700",        # Yellow
    "HARD": "#FFFFFF",          # White
    "INTERMEDIATE": "#00FF00",  # Green
    "WET": "#0066FF"            # Blue
}

def tyre_color(compound):
    """
    Returns color for a given tyre compound
    """
    if compound is None:
        return "#888888"
    return TYRE_COLORS.get(str(compound).upper(), "#888888")



# =========================
# Make src importable
# =========================
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.data_loader import load_session
from src.telemetry_utils import get_telemetry
from src.delta_utils import compute_delta_time, compute_sector_deltas


# =========================
# Streamlit config
# =========================
st.set_page_config(
    page_title="F1 Telemetry Analysis",
    layout="wide"
)

st.title("🏎️ Formula 1 Telemetry Analysis Tool")
st.write("Interactive analysis of F1 telemetry using Python & FastF1")
st.markdown(
    """
    This dashboard allows interactive exploration of Formula 1 telemetry data.
    Select a season, race, session, and drivers to compare performance at a
    corner-by-corner level.
    """
)

def generate_insights(
    driver_1,
    driver_2,
    final_delta,
    sector_deltas,
    corner_data
):
    insights = []

    # -------------------------
    # Determine overall winner
    # -------------------------
    if final_delta < 0:
        winner = driver_2
        loser = driver_1
    else:
        winner = driver_1
        loser = driver_2

    insights.append(
        f"🏆 **{winner}** emerged as the faster driver, finishing the lap "
        f"**{abs(final_delta):.3f}s** ahead overall."
    )

    # -------------------------
    # Strongest sector (winner-based)
    # -------------------------
    winning_sectors = {}

    for sector, sec_delta in sector_deltas.items():
        # Driver 1 gains when delta > 0
        if winner == driver_1 and sec_delta > 0:
            winning_sectors[sector] = sec_delta

        # Driver 2 gains when delta < 0
        elif winner == driver_2 and sec_delta < 0:
            winning_sectors[sector] = abs(sec_delta)

    if winning_sectors:
        strongest_sector = max(winning_sectors, key=winning_sectors.get)

        insights.append(
            f"📊 **{winner} gained the most time in {strongest_sector}**, "
            f"highlighting stronger pace through that part of the lap."
        )
    else:
        insights.append(
            "📊 No single sector showed a decisive advantage across the lap."
        )

    # -------------------------
    # Biggest corner impact
    # -------------------------
    if corner_data:
        biggest_corner = max(
            corner_data,
            key=lambda x: abs(x["Delta Change (s)"])
        )

        insights.append(
            f"⚠️ The biggest time swing occurred at "
            f"**{biggest_corner['Corner']}** "
            f"({biggest_corner['Delta Change (s)']:.3f}s)."
        )

    return insights



def detect_corners(
    car,
    min_speed_drop=18,
    window=6,
    min_spacing=25
):
    speed = car["Speed"].values
    corner_indices = []

    for i in range(window, len(speed) - window):
        speed_before = np.mean(speed[i - window:i])
        speed_after = np.mean(speed[i:i + window])

        if (speed_before - speed_after) > min_speed_drop:
            corner_indices.append(i)

    # Remove clustered detections
    filtered = []
    last = -1000
    for idx in corner_indices:
        if idx - last > min_spacing:
            filtered.append(idx)
            last = idx

    return filtered




# =========================
# Helper functions
# =========================


def extract_tyre_stints(laps):
    """
    Extract tyre stints in correct race order.
    Returns list of dicts:
    [
      {
        'compound': 'MEDIUM',
        'start_lap': 1,
        'end_lap': 18,
        'length': 18
      },
      ...
    ]
    """
    stints = []

    if laps.empty:
        return stints

    laps = laps.sort_values("LapNumber")

    current_compound = laps.iloc[0]["Compound"]
    start_lap = int(laps.iloc[0]["LapNumber"])

    for i in range(1, len(laps)):
        row = laps.iloc[i]

        if row["Compound"] != current_compound:
            end_lap = int(laps.iloc[i - 1]["LapNumber"])
            stints.append({
                "compound": current_compound,
                "start_lap": start_lap,
                "end_lap": end_lap,
                "length": end_lap - start_lap + 1
            })

            current_compound = row["Compound"]
            start_lap = int(row["LapNumber"])

    # Last stint
    end_lap = int(laps.iloc[-1]["LapNumber"])
    stints.append({
        "compound": current_compound,
        "start_lap": start_lap,
        "end_lap": end_lap,
        "length": end_lap - start_lap + 1
    })

    return stints



def get_lap_options(laps, driver):
    """
    Returns sorted lap options for UI selection
    """
    driver_laps = laps[laps["Driver"] == driver].copy()

    # Remove invalid laps
    driver_laps = driver_laps[driver_laps["LapTime"].notna()]

    # Sort by lap time
    driver_laps = driver_laps.sort_values("LapTime")

    options = []

    for i, row in driver_laps.iterrows():
        label = (
            f"Lap {int(row['LapNumber'])} | "
            f"{row['LapTime']} | "
            f"{row['Compound']}"
        )

        # Tag fastest & slowest
        if i == driver_laps.index[0]:
            label = "🚀 Fastest — " + label
        elif i == driver_laps.index[-1]:
            label = "🐢 Slowest — " + label

        options.append((label, i))

    return options




@st.cache_data(show_spinner=False)
def get_races_for_year(year):
    schedule = fastf1.get_event_schedule(year)
    return schedule["EventName"].tolist()

def load_data(year, race, session_type):
    session = load_session(year, race, session_type)
    laps = session.laps

    valid_laps = laps[
        laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
        & laps["LapTime"].notna()
    ]

    return session, valid_laps

def get_driver_metadata(session):
    meta = {}
    for drv in session.drivers:
        info = session.get_driver(drv)
        meta[drv] = {
            "name": info["FullName"],
            "team": info["TeamName"],
        }
    return meta

# =========================
# Sidebar controls
# =========================
st.sidebar.header("Session Selection")

year = st.sidebar.selectbox(
    "Season",
    sorted(range(2018, 2026), reverse=True)
)

races = get_races_for_year(year)
race = st.sidebar.selectbox("Race", races)

session_type = st.sidebar.selectbox(
    "Session",
    ["FP1", "FP2", "FP3", "Q", "R"],
    index=3  # ✅ Default = Qualifying (safer than Race)
)


# =========================
# Load session + laps
# =========================
status = st.empty()

status.info("📥 Initializing FastF1 session data… This may take up to a minute.")
session, valid_laps = load_data(year, race, session_type)

status.info("📊 Processing lap and driver data…")
driver_meta = get_driver_metadata(session)

status.empty()


driver_meta = get_driver_metadata(session)

driver_codes = sorted(driver_meta.keys())
driver_labels = [
    f"{code} — {driver_meta[code]['name']}"
    for code in driver_codes
]

driver_1_label = st.sidebar.selectbox("Driver 1", driver_labels, index=0)
driver_2_label = st.sidebar.selectbox("Driver 2", driver_labels, index=1)

driver_1 = driver_1_label.split(" — ")[0]
driver_2 = driver_2_label.split(" — ")[0]

if driver_1 == driver_2:
    st.warning("Please select two different drivers.")
    st.stop()

driver_1_name = driver_meta[driver_1]["name"]
driver_2_name = driver_meta[driver_2]["name"]

# =========================
# Lap Selection (FIXED)
# =========================
st.sidebar.subheader("Lap Selection")

def get_driver_laps(laps, driver):
    drv_laps = laps.pick_driver(driver).copy()
    drv_laps = drv_laps[drv_laps["LapTime"].notna()]
    drv_laps = drv_laps.sort_values("LapTime").reset_index(drop=True)
    return drv_laps

def format_lap(row, is_fastest=False, is_slowest=False):
    tyre = row["Compound"] if pd.notna(row["Compound"]) else "Unknown"
    label = f"Lap {int(row['LapNumber'])} | {row['LapTime']} | {tyre}"
    if is_fastest:
        label = "🚀 Fastest — " + label
    elif is_slowest:
        label = "🐢 Slowest — " + label
    return label


# -------- Driver 1 --------
laps_1 = get_driver_laps(valid_laps, driver_1)

if laps_1.empty:
    st.sidebar.warning(f"No valid laps for {driver_1_name}")
    st.stop()

lap_options_1 = []
for i, row in laps_1.iterrows():
    lap_options_1.append(
        (
            format_lap(
                row,
                is_fastest=(i == 0),
                is_slowest=(i == len(laps_1) - 1)
            ),
            i
        )
    )

lap_choice_1 = st.sidebar.selectbox(
    f"{driver_1_name} Lap",
    lap_options_1,
    index=0,  # 🚀 fastest lap ALWAYS default
    format_func=lambda x: x[0]
)

lap_1 = laps_1.iloc[lap_choice_1[1]]


# -------- Driver 2 --------
laps_2 = get_driver_laps(valid_laps, driver_2)

if laps_2.empty:
    st.sidebar.warning(f"No valid laps for {driver_2_name}")
    st.stop()

lap_options_2 = []
for i, row in laps_2.iterrows():
    lap_options_2.append(
        (
            format_lap(
                row,
                is_fastest=(i == 0),
                is_slowest=(i == len(laps_2) - 1)
            ),
            i
        )
    )

lap_choice_2 = st.sidebar.selectbox(
    f"{driver_2_name} Lap",
    lap_options_2,
    index=0,  # 🚀 fastest lap default
    format_func=lambda x: x[0]
)

lap_2 = laps_2.iloc[lap_choice_2[1]]

# =========================
# Race Strategy Data (FULL RACE)
# =========================
strategy_laps_1 = (
    valid_laps.pick_driver(driver_1)
    .sort_values("LapNumber")
    .reset_index(drop=True)
)

strategy_laps_2 = (
    valid_laps.pick_driver(driver_2)
    .sort_values("LapNumber")
    .reset_index(drop=True)
)

stints_1 = extract_tyre_stints(strategy_laps_1)
stints_2 = extract_tyre_stints(strategy_laps_2)



# =========================
# Driver colors (GLOBAL SCOPE)
# =========================
team_1 = driver_meta[driver_1]["team"]
team_2 = driver_meta[driver_2]["team"]

color_1 = TEAM_COLORS.get(team_1, "#FFFFFF")
color_2 = TEAM_COLORS.get(team_2, "#AAAAAA")


# =========================
# Telemetry processing
# =========================
st.sidebar.markdown("---")
load_telemetry = st.sidebar.button("🚀Compare")

if load_telemetry:
    status = st.empty()  # 👈 progress-style text placeholder

    try:
        # -------------------------
        # Telemetry download
        # -------------------------
        status.info("📡 Downloading telemetry data for selected laps…")
        car_1, pos_1 = get_telemetry(lap_1)
        car_2, pos_2 = get_telemetry(lap_2)


        # -------------------------
        # Delta computation
        # -------------------------
        status.info("⏱️ Computing delta time and sector analysis…")
        dist, delta = compute_delta_time(car_1, car_2)
        sector_deltas = compute_sector_deltas(dist, delta)

        # -------------------------
        # Numeric safety conversion
        # -------------------------
        status.info("🔧 Preparing telemetry for visualization…")

        dist = np.asarray(dist, dtype=float)
        delta = np.asarray(delta, dtype=float)

        car_1["Distance"] = np.asarray(car_1["Distance"], dtype=float)
        car_2["Distance"] = np.asarray(car_2["Distance"], dtype=float)

        car_1["Speed"] = np.asarray(car_1["Speed"], dtype=float)
        car_2["Speed"] = np.asarray(car_2["Speed"], dtype=float)

        car_1["Throttle"] = np.asarray(car_1["Throttle"], dtype=float)
        car_2["Throttle"] = np.asarray(car_2["Throttle"], dtype=float)

        pos_1["X"] = np.asarray(pos_1["X"], dtype=float)
        pos_1["Y"] = np.asarray(pos_1["Y"], dtype=float)
        pos_2["X"] = np.asarray(pos_2["X"], dtype=float)
        pos_2["Y"] = np.asarray(pos_2["Y"], dtype=float)

        status.empty()  # ✅ clear message when done

    except Exception as e:
        status.empty()
        st.error(
            "Telemetry could not be loaded for this selection.\n\n"
            "👉 Try:\n"
            "- Switching to Qualifying (Q)\n"
            "- Choosing a different lap\n"
            "- Reloading once\n\n"
            f"Error: {str(e)}"
        )
        st.stop()

else:
    st.info("👈 Data Loaded Successfully, Click on **🚀Compare** Button")
    st.stop()



corner_data = []


# =========================
# 🏁 Session Performance Summary
# =========================
st.subheader("🏁 Session Performance Summary")

# -------------------------
# Final delta & winner
# -------------------------
final_delta = delta[-1]

winner = driver_2_name if final_delta < 0 else driver_1_name
loser  = driver_1_name if final_delta < 0 else driver_2_name

# -------------------------
# Strongest sector (winner-based)
# -------------------------
sector_strength = {}

for sector, sec_delta in sector_deltas.items():
    if winner == driver_1_name and sec_delta > 0:
        sector_strength[sector] = sec_delta
    elif winner == driver_2_name and sec_delta < 0:
        sector_strength[sector] = abs(sec_delta)

strongest_sector = (
    max(sector_strength, key=sector_strength.get)
    if sector_strength else None
)

# -------------------------
# Biggest corner swing
# -------------------------
biggest_corner = None
biggest_swing = 0

if corner_data:
    for row in corner_data:
        swing = abs(row["Delta Change (s)"])
        if swing > biggest_swing:
            biggest_swing = swing
            biggest_corner = row["Corner"]

# -------------------------
# Summary cards
# -------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Lap Winner", winner)
c2.metric("Final Delta", f"{abs(final_delta):.3f} s")
c3.metric("Strongest Sector", strongest_sector if strongest_sector else "—")
c4.metric("Corners Analyzed", len(corner_data) if corner_data else "—")

st.markdown("### 🛞 Tyre Compound for selected lap")

c1, c2 = st.columns(2)

with c1:
    st.metric(
        label=f"{driver_1_name} Tyre",
        value=lap_1["Compound"]
    )

with c2:
    st.metric(
        label=f"{driver_2_name} Tyre",
        value=lap_2["Compound"]
    )



# =========================
# Dynamic section title
# =========================
if session_type == "R":
    strategy_title = "📈 Race Strategy Comparison"
else:
    strategy_title = "🛞 Tyre Usage Overview"

st.subheader(strategy_title)

if session_type != "R":
    st.info(
        "ℹ️ In non-race sessions (Qualifying / Practice), drivers usually run "
        "**only one tyre compound**.\n\n"
        "This view shows tyre usage, not pit-stop strategy."
    )



fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(111)






def plot_strategy(stints, y):
    if not stints:
        return

    for stint in stints:
        if stint["length"] <= 0:
            continue

        ax.barh(
            y=y,
            width=int(stint["length"]),
            left=int(stint["start_lap"]),
            color=tyre_color(stint["compound"]),
            edgecolor="black",
            height=0.35
        )



plot_strategy(stints_1, y=1)
plot_strategy(stints_2, y=0)


ax.set_yticks([1, 0])
ax.set_yticklabels([driver_1_name, driver_2_name])
ax.set_xlabel("Lap Number")
ax.set_title("Tyre Strategy Timeline")
ax.grid(axis="x", linestyle="--", alpha=0.3)

st.pyplot(fig)
plt.close(fig)

if session_type == "R":
    st.info(
        "ℹ️ **Why are some laps missing in the strategy timeline?**\n\n"
        "Gaps in the timeline represent **pit stop phases**. "
        "Laps where a driver **enters or exits the pit lane** are excluded, "
        "as tyre compound data is not valid during those laps.\n\n"
        "This ensures the strategy view reflects **only full racing laps**, "
        "similar to official Formula 1 broadcast graphics."
    )



st.subheader("🛞 Tyre Usage Overview")

def render_tyre_usage(driver_name, stints):
    st.markdown(f"### {driver_name}")
    for stint in stints:
        st.markdown(
            f"<span style='color:{tyre_color(stint['compound'])}'>●</span> "
            f"{stint['compound']} "
            f"(Lap {stint['start_lap']} → {stint['end_lap']}) "
            f"**[{stint['length']} laps]**",
            unsafe_allow_html=True
        )

c1, c2 = st.columns(2)

with c1:
    render_tyre_usage(driver_1_name, stints_1)

with c2:
    render_tyre_usage(driver_2_name, stints_2)





# =========================
# Plots
# =========================
st.subheader("📊 Telemetry Comparison")
col1, col2 = st.columns(2)

# ---- Speed plot ----
with col1:
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(111)

    ax.plot(
      np.asarray(car_1["Distance"], dtype=float),
      np.asarray(car_1["Speed"], dtype=float),
      label=driver_1_name,
      color=color_1
    )

    ax.plot(
      np.asarray(car_2["Distance"], dtype=float),
      np.asarray(car_2["Speed"], dtype=float),
      label=driver_2_name,
      color=color_2
    ) 


    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)


# ---- Throttle plot ----
with col2:
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(111)

    ax.plot(
      np.asarray(car_1["Distance"], dtype=float),
      np.asarray(car_1["Throttle"], dtype=float),
      label=driver_1_name,
      color=color_1
    )

    ax.plot(
      np.asarray(car_2["Distance"], dtype=float),
       np.asarray(car_2["Throttle"], dtype=float),
      label=driver_2_name,
      color=color_2
    )



    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Throttle (%)")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)


# ---- Delta plot ----
st.subheader("⏱️ Delta Time Analysis")
fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(111)


dist = np.asarray(dist, dtype=float)
delta = np.asarray(delta, dtype=float)

ax.plot(dist, delta, color="purple")
ax.axhline(0, linestyle="--")

ax.set_xlabel("Distance (m)")
ax.set_ylabel("Delta Time (s)")
ax.set_title(f"{driver_2_name} relative to {driver_1_name}")
st.pyplot(fig)
plt.close(fig)


st.subheader("🧩 Sector-wise Delta Analysis")

cols = st.columns(3)

for i, (sector, sec_delta) in enumerate(sector_deltas.items()):
    faster_driver = driver_2_name if sec_delta < 0 else driver_1_name
    color = "green" if sec_delta < 0 else "red"

    cols[i].metric(
        label=sector,
        value=f"{abs(sec_delta):.3f} s",
        delta=f"{faster_driver} faster",
        delta_color="inverse"
    )


corner_indices = detect_corners(
    car_1,
    min_speed_drop=8,
    window=7,
    min_spacing=15
)




corner_data = []

for corner_no, idx in enumerate(corner_indices, start=1):
    try:
        d = car_1.loc[idx, "Distance"]

        if len(dist) == 0:
            continue

        nearest_idx = (np.abs(dist - d)).argmin()

        delta_before = delta[max(nearest_idx - 5, 0)]
        delta_after  = delta[min(nearest_idx + 5, len(delta) - 1)]
        delta_change = delta_after - delta_before

        gained_by = driver_2_name if delta_change < 0 else driver_1_name

        corner_data.append({
            "Corner": f"T{corner_no}",
            "Distance (m)": round(d, 1),
            "Delta Change (s)": round(delta_change, 3),
            "Gained/Lost": f"Gained ({gained_by})"
        })

    except Exception:
        continue


st.subheader("📍 Corner-by-Corner Delta")

if corner_data:
    st.dataframe(corner_data, use_container_width=True)
else:
    st.info("No significant corners detected. Try Qualifying session.")




# =========================
# Track Map Overlay (Corner Analysis)
# =========================
st.subheader("🗺️ Track Map Overlay (Corner Analysis)")

fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(111)


# --- Racing line (outlined for broadcast look) ---
ax.plot(
    pos_1["X"],
    pos_1["Y"],
    color="black",
    linewidth=4.5,
    alpha=0.85,
    zorder=1
)

ax.plot(
    pos_1["X"],
    pos_1["Y"],
    color=color_1,
    linewidth=3,
    zorder=2,
    label=driver_1_name
)

ax.plot(
    pos_2["X"],
    pos_2["Y"],
    color=color_2,
    linestyle="--",
    linewidth=2.5,
    zorder=2,
    label=driver_2_name
)



# --- Corner markers ---
TURN_SIZE = 260  # fixed size for clean look

for i, corner in enumerate(corner_data):
    try:
        idx = corner_indices[i]
        if idx >= len(pos_1):
            continue

        x = float(pos_1.iloc[idx]["X"])
        y = float(pos_1.iloc[idx]["Y"])


        delta_change = corner["Delta Change (s)"]

        # Green = Driver 2 gains | Red = Driver 2 loses
        turn_color = "#00C853" if delta_change < 0 else "#D50000"

        # Turn circle
        ax.scatter(
            x, y,
            s=TURN_SIZE,
            color=turn_color,
            edgecolors="black",
            linewidth=1.4,
            zorder=6
        )

        # Turn label (T1, T2, ...)
        ax.text(
            x, y,
            f"T{i+1}",
            fontsize=9,
            weight="bold",
            color="white",
            ha="center",
            va="center",
            zorder=7
        )

    except Exception:
        continue

# --- Legend (broadcast style, below track) ---
from matplotlib.lines import Line2D

legend_items = [
    Line2D([0], [0], color=color_1, lw=3, label=driver_1_name),
    Line2D([0], [0], color=color_2, lw=3, linestyle="--", label=driver_2_name),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#00C853", markeredgecolor="black",
           markersize=9, label=f"Time gained by {driver_2_name}"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#D50000", markeredgecolor="black",
           markersize=9, label=f"Time lost by {driver_2_name}")
]

ax.legend(
    handles=legend_items,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.08),
    ncol=2,
    frameon=True
)

# --- Final styling ---
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(f"{race} – Racing Line & Corner Delta", fontsize=13)

st.pyplot(fig)
plt.close(fig)



# =========================
# Insights
# =========================
final_delta = delta[-1]



st.markdown("## 🧠 Key Performance Insights")

st.caption(
    f"{driver_1_name} ({driver_meta[driver_1]['team']}) vs "
    f"{driver_2_name} ({driver_meta[driver_2]['team']})"
)

insights = generate_insights(
    driver_1_name,
    driver_2_name,
    final_delta,
    sector_deltas,
    corner_data
)

for insight in insights:
    st.markdown(f"- {insight}")



st.write(
    "📌 Delta time trends show where time is gained or lost across the lap, "
    "highlighting braking zones, corner exits, and straight-line performance."
)

st.markdown("---")
st.caption(
    "Telemetry data sourced via FastF1. "
    "Analysis is indicative and for educational purposes."
)

