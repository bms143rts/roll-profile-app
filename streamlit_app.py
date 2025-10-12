import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from datetime import date as dt_date
import gspread
from google.oauth2.service_account import Credentials

import streamlit as st

hide_streamlit_style = """
    <style>
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
import streamlit as st

hide_streamlit_ui = """
    <style>
    /* 1. HIDE TOP-RIGHT ICONS (Profile, Manage App, etc.) */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
    }

    /* 2. HIDE BOTTOM STATUS/FOOTER WIDGETS (e.g., Streamlit status/deploy) */
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        height: 0; /* Ensures it doesn't take up space */
        overflow: hidden; /* Ensures no scrollbar */
    }

    /* Optional: Hides the three-dot menu, if not already hidden */
    #MainMenu {
        visibility: hidden;
    }

    /* Optional: Hides the "Made with Streamlit" footer text */
    footer {
        visibility: hidden;
    }
    </style>
"""
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)


# Must be the first Streamlit command for global settings
st.set_page_config(layout="wide")

# Your app code continues below...


# --- Google Sheets Config ---
SHEET_NAME = "Roll_Data"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# --- Roll Config ---
DISTANCES = [100, 350, 600, 850, 1100, 1350, 1600]
MIN_DIA = 1200.0
MAX_DIA = 1400.0

# --- Streamlit UI ---
st.title("Backup Roll Profile Data Entry")

# Load existing data
existing_data = sheet.get_all_records()
df = pd.DataFrame(existing_data)

# --- Entry Form ---
with st.form("entry_form", clear_on_submit=False):
    st.subheader("Add New Roll Entry")
    entry_date = st.date_input("Date", value=dt_date.today())
    roll_no = st.text_input("Roll No (required)").strip().upper()
    st.markdown("**Diameters (mm)** — must be between 1250 and 1352")

    diameters = {}
    for d in DISTANCES:
        val = st.text_input(f"{d} mm", value="", key=f"dia_{d}")  # empty field by default
        try:
            diameters[d] = float(val) if val.strip() != "" else 0
        except ValueError:
            diameters[d] = 0

    submitted = st.form_submit_button("Save Entry")

# --- Save Entry ---
if submitted:
    errors = []

    if roll_no == "":
        errors.append("❌ Roll No cannot be empty")

    # Filter diameters: remove zeros
    filtered_diameters = {}
    for d, v in diameters.items():
        if v == 0:
            continue
        if not (MIN_DIA <= v <= MAX_DIA):
            errors.append(f"❌ {d} mm value {v} out of range [{MIN_DIA}-{MAX_DIA}]")
        else:
            filtered_diameters[d] = v

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Prepare row without serial number
        row = [str(entry_date), roll_no] + [filtered_diameters.get(d, "") for d in DISTANCES]

        # Append to Google Sheet
        sheet.append_row(row)
        st.success(f"✅ Entry saved for Roll No: {roll_no}")

        # Refresh dataframe
        existing_data = sheet.get_all_records()
        df = pd.DataFrame(existing_data)

# --- Show Data ---
st.subheader("Stored Data")
if df.empty:
    st.info("No entries yet.")
else:
    # Format numeric columns to 2 decimals
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].map(lambda x: f"{x:.2f}" if x != "" else "")

    # Reset index so first column is not shown
    df = df.reset_index(drop=True)

    # Show only 10 rows per page
    page_size = 10
    page = st.number_input("Page", min_value=1, max_value=(len(df) - 1) // page_size + 1, step=1)
    start = (page - 1) * page_size
    end = start + page_size

    st.table(df.iloc[start:end])

# --- Download Functions ---
def to_excel_bytes(df):
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="RollData")
    output.seek(0)
    return output.getvalue()

def to_word_bytes(df):
    doc = Document()
    doc.add_heading("Roll Profile Data", level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr[i].text = str(col)
    for _, r in df.iterrows():
        cells = table.add_row().cells
        for j, col in enumerate(df.columns):
            cells[j].text = str(r[col])
    out = BytesIO()
    doc.save(out)
    out.seek(0)
    return out.getvalue()

# --- Download Buttons ---
if not df.empty:
    st.download_button(
        "⬇️ Download Excel",
        data=to_excel_bytes(df),
        file_name="roll_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.download_button(
        "⬇️ Download Word",
        data=to_word_bytes(df),
        file_name="roll_data.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )










