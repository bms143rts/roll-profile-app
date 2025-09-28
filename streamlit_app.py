import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from datetime import date as dt_date
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Config ---
SHEET_NAME = "Roll_Data"   # <-- Change if your sheet has a different name
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
    roll_no = st.text_input("Roll No (required, stored in UPPERCASE)").strip().upper()
    st.markdown("**Diameters (mm)** — must be between 1250 and 1352")

    diameters = {}
    for d in DISTANCES:
        diameters[d] = st.number_input(f"{d} mm", step=0.01, key=f"dia_{d}")

    submitted = st.form_submit_button("Save Entry")

# --- Save Entry ---
# --- Save Entry ---
if submitted:
    errors = []

    if roll_no == "":
        errors.append("❌ Roll No cannot be empty")

    # Filter diameters: remove zeros or values out of range
    filtered_diameters = {}
    for d, v in diameters.items():
        if v == 0:
            continue  # Skip zeros
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
st.subheader("Stored Data ")
if df.empty:
    st.info("No entries yet.")
else:
    st.dataframe(df.style.hide_index())


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
    st.download_button("⬇️ Download Excel", data=to_excel_bytes(df),
                       file_name="roll_data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("⬇️ Download Word", data=to_word_bytes(df),
                       file_name="roll_data.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")








