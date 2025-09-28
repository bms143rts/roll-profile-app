import streamlit as st
import traceback
import gspread
from google.oauth2.service_account import Credentials

st.title("DEBUG: Google Sheets auth check")

# 1) show keys present
st.write("Secrets keys:", list(st.secrets.keys()))

try:
    # 2) load dict and normalize private_key newlines
    creds_dict = dict(st.secrets["gcp_service_account"])
    pk = creds_dict.get("private_key", "")
    if isinstance(pk, str) and "\\n" in pk:
        creds_dict["private_key"] = pk.replace("\\n", "\n")
        st.write("Replaced '\\\\n' with real newlines in private_key.")

    # 3) initialize creds + client
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    st.success("Auth OK — gspread client created.")

    # 4) test open by key (replace with your SHEET_ID)
    SHEET_ID = "PUT_YOUR_SHEET_ID_HERE"
    st.write("Attempting to open sheet id:", SHEET_ID)
    sh = client.open_by_key(SHEET_ID)
    st.success("Opened spreadsheet: " + sh.title)
    st.write("Sheet owner / url:", sh.url)

except Exception as e:
    st.error("Auth / Sheet open failed: " + str(e))
    st.text("Full traceback (for debugging):")
    st.text(traceback.format_exc())
