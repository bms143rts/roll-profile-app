import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Roll Profile Comparison", layout="centered")

st.title("Roll Profile Plotter")

# Step 1: Mid Diameter Input
mid_dia = st.number_input("Enter Mid Diameter (in mm)", min_value=850.0, max_value=950.0, value=894.7, step=0.01)

# Step 2: Taper Parameters
barrel_length = 1700  # mm
taper_height = 1.5    # mm
half_taper = taper_height / 2

# Step 3: Generate Positions
positions = np.arange(0, barrel_length + 1, 100)  # [0, 100, ..., 1700]

# Step 4: Calculate Ideal Profile
ideal_profile = []
for pos in positions:
    if pos <= 500:
        dia = mid_dia - half_taper + (pos / 500) * half_taper
    elif pos >= 1200:
        dia = mid_dia - half_taper + ((1700 - pos) / 500) * half_taper
    else:
        dia = mid_dia
    ideal_profile.append(round(dia, 2))

# Step 5: Measured Diameters Input
st.subheader("Enter Measured Diameter at Each Position (in mm)")
measured_dia = []
cols = st.columns(4)
for i, pos in enumerate(positions):
    with cols[i % 4]:
        val = st.number_input(f"{pos} mm", key=f"meas_{i}", value=round(ideal_profile[i], 2), step=0.01)
        measured_dia.append(val)

# Step 6: Plotting
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(positions, ideal_profile, label="Ideal Profile", linestyle='--', marker='o')
ax.plot(positions, measured_dia, label="Measured Diameter", linestyle='-', marker='s', color='red')
ax.set_xlabel("Position (mm)")
ax.set_ylabel("Diameter (mm)")
ax.set_title("Roll Profile Comparison")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# Optional: Table Display
st.subheader("Comparison Table")
import pandas as pd
df = pd.DataFrame({
    "Position (mm)": positions,
    "Ideal Dia (mm)": ideal_profile,
    "Measured Dia (mm)": measured_dia,
    "Error (mm)": np.round(np.array(measured_dia) - np.array(ideal_profile), 2)
})
st.dataframe(df)

# Optional: CSV download
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download as CSV", csv, "roll_profile_comparison.csv", "text/csv")


