import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import gspread
from google.oauth2.service_account import ServiceAccountCredentials

# --- Google Sheets Setup ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
client = gspread.authorize(creds)
SHEET = client.open("BackupRollData").sheet1  # Make sure your sheet exists

# --- Columns matching your sheet ---
columns = ["Date", "Roll No", "D_50", "D_350", "D_650", "D_950", "D_1250", "D_1450", "D_1650"]

# --- Function to safely load sheet data ---
def load_sheet_data(sheet):
    all_values = sheet.get_all_values()
    if not all_values:
        return pd.DataFrame(columns=columns)
    
    header = all_values[0]
    # Make headers unique if duplicates exist
    seen = {}
    unique_header = []
    for h in header:
        if h in seen:
            count = seen[h] + 1
            seen[h] = count
            unique_header.append(f"{h}_{count}")
        else:
            seen[h] = 0
            unique_header.append(h)
    
    df = pd.DataFrame(all_values[1:], columns=unique_header)
    return df

# --- Load existing data ---
df = load_sheet_data(SHEET)

# --- Add new entry ---
st.header("Backup Roll Data Entry")

with st.form("entry_form"):
    date = st.date_input("Date")
    roll_no = st.text_input("Roll No")
    d50 = st.number_input("Diameter at 50 mm", min_value=0.0, step=0.01, format="%.2f")
    d350 = st.number_input("Diameter at 350 mm", min_value=0.0, step=0.01, format="%.2f")
    d650 = st.number_input("Diameter at 650 mm", min_value=0.0, step=0.01, format="%.2f")
    d950 = st.number_input("Diameter at 950 mm", min_value=0.0, step=0.01, format="%.2f")
    d1250 = st.number_input("Diameter at 1250 mm", min_value=0.0, step=0.01, format="%.2f")
    d1450 = st.number_input("Diameter at 1450 mm", min_value=0.0, step=0.01, format="%.2f")
    d1650 = st.number_input("Diameter at 1650 mm", min_value=0.0, step=0.01, format="%.2f")

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        # Prevent duplicate entries for same Date + Roll No
        if not ((df["Date"] == str(date)) & (df["Roll No"] == roll_no)).any():
            new_row = [str(date), roll_no, d50, d350, d650, d950, d1250, d1450, d1650]
            SHEET.append_row(new_row)
            st.success("Entry added successfully!")
            # Reload the latest data
            df = load_sheet_data(SHEET)
        else:
            st.warning("Duplicate entry detected! Not added.")

# --- Show table ---
st.subheader("Stored Data")
st.dataframe(df, use_container_width=True)

# --- Download as Excel ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="BackupRollData")
    return output.getvalue()

st.download_button(
    label="Download Excel",
    data=to_excel(df),
    file_name="BackupRollData.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# --- Download as Word ---
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

st.download_button(
    label="Download Word",
    data=to_word(df),
    file_name="BackupRollData.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

