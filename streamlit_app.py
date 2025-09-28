import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# -------------------------
# Google Sheets Setup
# -------------------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load secrets (service account JSON stored in st.secrets)
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# Open your Google Sheet (must be shared with service account email)
SHEET_NAME = "RollProfileData"   # change to your sheet name
sheet = client.open(SHEET_NAME).sheet1


# -------------------------
# App UI
# -------------------------
st.title("📊 Roll Profile Data Collector")

st.markdown("Enter your roll profile measurements below:")

# Example input: 17 diameter values
values = []
for i in range(1, 18):
    val = st.number_input(f"Diameter {i}", step=0.01, format="%.2f")
    values.append(val)

username = st.text_input("Your Name / ID")

if st.button("Submit"):
    if username.strip() == "":
        st.warning("⚠️ Please enter your name or ID before submitting.")
    else:
        try:
            # Save to Google Sheet
            row = [username] + values
            sheet.append_row(row)
            st.success("✅ Data submitted successfully!")
        except Exception as e:
            st.error(f"❌ Error saving data: {e}")


# -------------------------
# View & Download History
# -------------------------
st.subheader("📜 Submission History")

try:
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)

        # Download button
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="roll_profile_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No submissions yet.")
except Exception as e:
    st.error(f"❌ Could not load history: {e}")
