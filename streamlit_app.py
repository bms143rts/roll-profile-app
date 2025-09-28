import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --------------------------
# 1. Load service account from secrets
# --------------------------
creds_dict = st.secrets["gcp_service_account"]

scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

# --------------------------
# 2. Connect to Google Sheets
# --------------------------
client = gspread.authorize(creds)

# Replace with your sheet name
SHEET_NAME = "Roll_Data"
sheet = client.open(SHEET_NAME).sheet1  

st.title("📊 Roll Profile Data Entry App")

# --------------------------
# 3. User input form
# --------------------------
with st.form("data_entry_form"):
    user_name = st.text_input("Your Name")
    values = [st.number_input(f"Diameter {i+1}", step=0.01) for i in range(17)]
    submitted = st.form_submit_button("Submit Data")

if submitted:
    if user_name.strip() == "":
        st.error("⚠️ Please enter your name before submitting.")
    else:
        # Append row to Google Sheet
        row = [user_name] + values
        sheet.append_row(row)
        st.success("✅ Data submitted successfully!")

# --------------------------
# 4. Show current sheet data
# --------------------------
st.subheader("📜 All Submitted Data")
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    st.dataframe(df)

    # Download as CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download as CSV", csv, "roll_profile_data.csv", "text/csv")
else:
    st.info("No data submitted yet.")
