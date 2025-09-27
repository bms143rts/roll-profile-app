import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO

# ==============================
# Google Sheets Setup
# ==============================
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["google_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)

# Open your Google Sheet (replace with your actual sheet name)
SHEET = client.open("Roll Profile Data").sheet1

# ==============================
# Helper Functions
# ==============================
def load_sheet_data():
    """Fetch data from Google Sheet and return as DataFrame"""
    records = SHEET.get_all_records(expected_headers=[
        "Date", "Roll No", "D_50", "D_350", "D_650",
        "D_950", "D_1250", "D_1450", "D_1650"
    ])
    return pd.DataFrame(records)

def add_data(date, roll_no, values):
    """Append new row of data"""
    new_row = [date, roll_no] + values
    SHEET.append_row(new_row)

def delete_data(row_index):
    """Delete a row by its index in the sheet (1-based, including headers)"""
    SHEET.delete_rows(row_index)

def download_as_excel(df):
    """Convert DataFrame to Excel for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()

# ==============================
# Streamlit App UI
# ==============================
st.title("📊 Roll Profile Data App")

# Load data
df = load_sheet_data()

# Show current data
st.subheader("Current Data in Google Sheet")
st.dataframe(df)

# ------------------------------
# Add new data
# ------------------------------
st.subheader("➕ Add New Roll Profile Data")

with st.form("add_data_form"):
    date = st.date_input("Date")
    roll_no = st.text_input("Roll No")
    values = []
    for col in ["D_50", "D_350", "D_650", "D_950", "D_1250", "D_1450", "D_1650"]:
        values.append(st.number_input(col, value=0.0, step=0.1))
    
    submitted = st.form_submit_button("Add Data")
    if submitted:
        add_data(str(date), roll_no, values)
        st.success("✅ Data added successfully! Refresh to see changes.")

# ------------------------------
# Delete data
# ------------------------------
st.subheader("🗑️ Delete Data")

if not df.empty:
    row_to_delete = st.number_input(
        "Enter row number to delete (starting from 2 for first data row)",
        min_value=2, max_value=len(df)+1, step=1
    )
    if st.button("Delete Row"):
        delete_data(int(row_to_delete))
        st.warning(f"Row {row_to_delete} deleted successfully! Refresh to update view.")

# ------------------------------
# Download as Excel
# ------------------------------
st.subheader("⬇️ Download Data")
excel_data = download_as_excel(df)
st.download_button(
    label="Download Excel",
    data=excel_data,
    file_name="roll_profile_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
