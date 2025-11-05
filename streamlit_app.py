# streamlit_app.py
import streamlit as st 
import pandas as pd
from io import BytesIO
from docx import Document
from datetime import date as dt_date
import gspread
from google.oauth2.service_account import Credentials
import math

# --- UI / theme / hide bits (kept from your final app) ---
hide_streamlit_ui = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    div[data-testid="stDecoration"] {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; height: 0; overflow: hidden;}
    </style>
"""
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)

custom_css = """
    <style>
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --bg-light: #f8f9fa;
        --border-color: #e0e0e0;
    }
    * { margin: 0; padding: 0; }
    .main-header { background: linear-gradient(135deg, #1f77b4 0%, #0d5a9a 100%); color: white; padding: 2.5rem 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3); }
    .main-header h1 { font-size: 2.0rem; font-weight: 700; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .main-header p { font-size: 0.95rem; opacity: 0.95; font-weight: 300; }
    .form-section { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid var(--border-color); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .data-section { background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid var(--border-color); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .table-container { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 1.5rem; max-height: 500px; overflow-y: auto; }
    .table-container table { width: 100%; border-collapse: collapse; }
    .table-container thead th { background: linear-gradient(135deg, #1f77b4 0%, #0d5a9a 100%); color: white; padding: 0.6rem; text-align: left; font-weight: 600; position: sticky; top: 0; z-index: 10; }
    .table-container tbody td { padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--border-color); }
    .download-section { display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap; }
    .stButton > button { background: linear-gradient(135deg, #1f77b4 0%, #0d5a9a 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.5rem 1rem !important; font-weight: 600 !important; transition: all 0.2s ease !important; box-shadow: 0 4px 10px rgba(31, 119, 180, 0.12) !important; }
    body { background-color: #f5f7fa; }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.set_page_config(layout="wide", page_title="Roll Profile Data Entry")

# ---------------- Google Sheets Config ----------------
SHEET_NAME = "Roll_Data"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ---------------- Roll Config ----------------
DISTANCES = [100, 350, 600, 850, 1100, 1350, 1600]
MIN_DIA = 1245.0
MAX_DIA = 1352.0

# ---------------- Header ----------------
st.markdown("""
    <div class="main-header">
        <h1>📊 Backup Roll Profile Data Entry</h1>
        <p>Manage and track roll specifications with ease</p>
    </div>
""", unsafe_allow_html=True)

# ---------------- Load existing data ----------------
existing_data = sheet.get_all_records()
df = pd.DataFrame(existing_data)

# --------------- Input Form ---------------
with st.container():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    with st.form("entry_form", clear_on_submit=False):
        st.markdown("### ➕ Add New Roll Entry")
        # Use explicit keys so clearing works reliably
        col1, col2, col3 = st.columns(3)
        with col1:
            entry_date = st.date_input("📅 Date", key="entry_date", value=dt_date.today())
        with col2:
            roll_no = st.text_input("🏷️ Roll No (required)", key="roll_no", value="").strip().upper()
        with col3:
            stand = st.selectbox("🏭 Stand", ["Select...","F1","F2","F3","F4","F5","F6","ROUGHING","DC"], key="stand")
        col1, col2 = st.columns(2)
        with col1:
            position = st.selectbox("📍 Position", ["Select...","TOP","BOTTOM"], key="position")
        with col2:
            crown = st.selectbox("👑 Crown", ["Select...","STRAIGHT","+100 MICRON","+200 MICRON"], key="crown")

        st.markdown('<p style="font-weight:600;">📏 Diameters (mm) — must be between 1245 and 1352</p>', unsafe_allow_html=True)

        # Use text_input for blank-by-default behaviour; keys prefixed 'dia_'
        diameters = {}
        for d in DISTANCES:
            val = st.text_input(f"{d} mm", key=f"dia_{d}", value="", placeholder="Enter value (leave blank if not measured)")
            try:
                diameters[d] = float(val) if val.strip() != "" else 0
            except ValueError:
                diameters[d] = 0

        submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------- Save Entry ---------------
def clear_form_and_rerun():
    # Prepare dict of defaults to reset
    reset_dict = {
        "entry_date": dt_date.today(),
        "roll_no": "",
        "stand": "Select...",
        "position": "Select...",
        "crown": "Select..."
    }
    reset_dict.update({f"dia_{d}": "" for d in DISTANCES})
    st.session_state.update(reset_dict)
    # rerun to show cleared widgets
    st.experimental_rerun()

if submitted:
    errors = []
    # validate roll no
    if not roll_no:
        errors.append("❌ Roll No cannot be empty")
    # validate dropdowns
    if stand == "Select...":
        errors.append("❌ Please choose a Stand")
    if position == "Select...":
        errors.append("❌ Please choose Position")
    if crown == "Select...":
        errors.append("❌ Please choose Crown")

    filtered_diameters = {}
    for d, v in diameters.items():
        if v == 0:
            continue
        if not (MIN_DIA <= v <= MAX_DIA):
            errors.append(f"❌ {d} mm value {v} out of range [{MIN_DIA}-{MAX_DIA}]")
        else:
            filtered_diameters[d] = round(v, 2)

    if errors:
        for e in errors:
            st.error(e)
    else:
        row = [str(entry_date), roll_no, stand, position, crown] + [filtered_diameters.get(d, "") for d in DISTANCES]
        try:
            sheet.append_row(row)
            st.success(f"✅ Entry saved for Roll No: {roll_no}")
            # refresh local dataframe
            existing_data = sheet.get_all_records()
            df = pd.DataFrame(existing_data)
            # clear the form and rerun so cleared values show
            clear_form_and_rerun()
        except Exception as e:
            st.error("❌ Failed to save to Google Sheets: " + str(e))

# ---------------- Show Data ----------------
with st.container():
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.markdown("### 📋 Stored Data")
    if df.empty:
        st.markdown('<div style="background:#e3f2fd;border-left:4px solid #1f77b4;padding:1rem;border-radius:6px;">📭 No entries yet. Start by adding a new roll entry above.</div>', unsafe_allow_html=True)
    else:
        # format numeric columns for display (2 decimals)
        for col in df.columns:
            # detect numeric-like columns by trying conversion
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].map(lambda x: f"{x:.2f}" if pd.notnull(x) and x != "" else "")
            except Exception:
                pass

        # remove unnamed or empty columns if present
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.loc[:, df.columns != '']

        # pagination state
        page_size = 10
        total_pages = max(1, math.ceil(len(df) / page_size))
        if "page" not in st.session_state:
            st.session_state.page = 1
        # page controls
        col_prev, col_center, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅ Prev") and st.session_state.page > 1:
                st.session_state.page -= 1
        with col_center:
            st.markdown(f"<div style='text-align:center; font-weight:600;'>Page {st.session_state.page} of {total_pages} — Total entries: {len(df)}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Next ➡") and st.session_state.page < total_pages:
                st.session_state.page += 1

        page = st.session_state.page
        start = (page - 1) * page_size
        end = start + page_size
        df_page = df.iloc[start:end].reset_index(drop=True)

        # display with scroll container and hide index
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.dataframe(df_page, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#666; font-size:0.9rem; margin:0.75rem 0;'>Page {page} of {total_pages}</p>", unsafe_allow_html=True)

        # ---------------- Download Functions ----------------
        def to_excel_bytes(df_input):
            # prepare numeric columns as numbers (not formatted strings)
            df_export = df_input.copy()
            for c in DISTANCES:
                if str(c) in df_export.columns:
                    df_export[str(c)] = pd.to_numeric(df_export[str(c)], errors="coerce").round(2)
            output = BytesIO()
            df_export.to_excel(output, index=False, sheet_name="RollData")
            output.seek(0)
            return output.getvalue()

        def to_word_bytes(df_input):
            doc = Document()
            doc.add_heading("Roll Profile Data", level=1)
            table = doc.add_table(rows=1, cols=len(df_input.columns))
            table.style = "Table Grid"
            hdr = table.rows[0].cells
            for i, col in enumerate(df_input.columns):
                hdr[i].text = str(col)
            for _, r in df_input.iterrows():
                cells = table.add_row().cells
                for j, col in enumerate(df_input.columns):
                    # keep the cell string (display value)
                    cells[j].text = str(r[col])
            out = BytesIO()
            doc.save(out)
            out.seek(0)
            return out.getvalue()

        # Download buttons
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("⬇️ Download Excel", data=to_excel_bytes(df), file_name="roll_data.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col_dl2:
            st.download_button("⬇️ Download Word", data=to_word_bytes(df), file_name="roll_data.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
