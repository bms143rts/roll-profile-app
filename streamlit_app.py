import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- GOOGLE SHEETS SETUP ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)

# Replace with your actual Sheet ID
SHEET_ID = "1k5d9CAPLyBarCQsQ5wBe_YYZElioHucV0VCmwvzm9T8"
worksheet = client.open_by_key(SHEET_ID).sheet1


# --- STREAMLIT APP ---
st.title("Roll Profile Data Entry")

# User input form
with st.form("roll_form"):
    roll_no = st.text_input("Roll Number")
    operator = st.text_input("Operator Name")
    values = [st.number_input(f"Diameter {i+1}", step=0.01) for i in range(17)]
    submitted = st.form_submit_button("Submit")

if submitted:
    if roll_no.strip() == "":
        st.error("⚠️ Roll Number cannot be empty")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare row
        row = [timestamp, roll_no, operator] + values

        # Append row to Google Sheet
        worksheet.append_row(row)

        st.success("✅ Data submitted successfully!")

# --- VIEW & DOWNLOAD DATA ---
if st.checkbox("Show All Submitted Data"):
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)

    st.dataframe(df)

    # Download options
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "roll_data.csv", "text/csv")

    excel = df.to_excel(index=False, engine="openpyxl")
    st.download_button("⬇️ Download Excel", excel, "roll_data.xlsx")



