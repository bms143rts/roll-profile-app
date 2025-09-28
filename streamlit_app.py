import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

creds_dict = dict(st.secrets["gcp_service_account"])

# Fix private key newlines if needed
if "\\n" in creds_dict.get("private_key", ""):
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# Use sheet ID, not name
SHEET_ID = "1k5d9CAPLyBarCQsQ5wBe_YYZElioHucV0VCmwvzm9T8"
sheet = client.open_by_key(SHEET_ID).sheet1

st.success(f"Connected to Google Sheet: {sheet.title}")
