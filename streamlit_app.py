import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# Google Sheets Setup
# -----------------------------
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["google_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)

# Open your Google Sheet (change name if needed)
SHEET = client.open("BackupRollData").sheet1

# Columns
COLUMNS = ["Date", "Roll No", "D_50", "D_350", "D_650", "D_950", "D_1250", "D_1450", "D_1650"]


# -----------------------------
# Helper functions
# -----------------------------
def load_sheet_data(sheet):
    """Load all values into a pandas DataFrame"""
    all_values = sheet.get_all_values()
    if not all_values:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(all_values[1:], columns=all_values[0])
    return df


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="BackupRollData")
    return output.getvalue()


def to_word(df):
    doc = Document()
    doc.add_heading("Backup Roll Data", level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"

    # Header
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)

    # Rows
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            row_cells[i].text = str(row[col])

    output = BytesIO()
    doc.save(output)
    return output.getvalue()


# -----------------------------
# App UI
# -----------------------------
st.title("📊 Backup Roll Data (Mobile-Friendly)")

# Load data
df = load_sheet_data(SHEET)

# --- Add Entry ---
st.header("➕ Add New Entry")
with st.form("add_form"):
    date = st.date_input("Date")
    roll_no = st.text_input("Roll No")
    d50 = st.number_input("D_50", min_value=0.0, step=0.01)
    d350 = st.number_input("D_350", min_value=0.0, step=0.01)
    d650 = st.number_input("D_650", min_value=0.0, step=0.01)
    d950 = st.number_input("D_950", min_value=0.0, step=0.01)
    d1250 = st.number_input("D_1250", min_value=0.0, step=0.01)
    d1450 = st.number_input("D_1450", min_value=0.0, step=0.01)
    d1650 = st.number_input("D_1650", min_value=0.0, step=0.01)

    submitted = st.form_submit_button("✅ Add Entry")
    if submitted:
        if not ((df["Date"] == str(date)) & (df["Roll No"] == roll_no)).any():
            SHEET.append_row([str(date), roll_no, d50, d350, d650, d950, d1250, d1450, d1650])
            st.success("✅ Entry added successfully!")
            df = load_sheet_data(SHEET)
        else:
            st.warning("⚠️ Duplicate entry detected (same Date + Roll No).")


# --- Delete Entry ---
st.header("🗑️ Delete an Entry")
if not df.empty:
    # Let user pick from existing entries
    df["Key"] = df["Date"] + " | " + df["Roll No"]
    choice = st.selectbox("Select entry to delete:", df["Key"].unique())

    if st.button("❌ Delete Selected Entry"):
        idx_list = df.index[df["Key"] == choice].tolist()
        if idx_list:
            for i, idx in enumerate(idx_list):
                SHEET.delete_row(idx + 2 - i)  # Adjust for header + previous deletions
            st.success(f"Deleted {len(idx_list)} entry(ies): {choice}")
            df = load_sheet_data(SHEET)
else:
    st.info("No entries available to delete.")


# --- Show Data ---
st.subheader("📋 Current Data")
st.dataframe(df[COLUMNS], use_container_width=True)


# --- Download buttons ---
st.download_button(
    "⬇️ Download Excel",
    data=to_excel(df[COLUMNS]),
    file_name="BackupRollData.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button(
    "⬇️ Download Word",
    data=to_word(df[COLUMNS]),
    file_name="BackupRollData.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
