# streamlit_app.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Roll Profile Plotter")

st.markdown("Enter 17 diameter values measured across the roll (in mm):")

# Input for 17 diameters
diameters = []
cols = st.columns(5)
for i in range(17):
    with cols[i % 5]:
        val = st.number_input(f"Point {i+1}", value=100.0, step=0.01, format="%.2f")
        diameters.append(val)

# Generate ideal profile (linear taper from 102 to 98 mm)
ideal = np.linspace(102, 98, 17)

if st.button("Plot Profile"):
    x = np.linspace(0, 100, 17)

    fig, ax = plt.subplots()
    ax.plot(x, ideal, label="Ideal Profile", color="green", linestyle="--", marker='o')
    ax.plot(x, diameters, label="Measured Profile", color="blue", linestyle="-", marker='x')

    ax.set_xlabel("Position across roll (%)")
    ax.set_ylabel("Diameter (mm)")
    ax.set_title("Comparison of Measured vs Ideal Roll Profile")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
