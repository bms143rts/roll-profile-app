import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from datetime import date as dt_date
import gspread
from google.oauth2.service_account import Credentials

# Hide Streamlit UI elements
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

# Custom CSS for attractive design
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

    * {
        margin: 0;
        padding: 0;
    }

    .main-header {
        background: linear-gradient(135deg, #1f77b4 0%, #0d5a9a 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3);
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .main-header p {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 300;
    }

    .form-section {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    .form-section h2 {
        color: #1f77b4;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }

    .data-section {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    .data-section h2 {
        color: #1f77b4;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }

    .table-container {
        overflow-x: auto;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        max-height: 500px;
        overflow-y: auto;
    }

    .table-container table {
        width: 100%;
        border-collapse: collapse;
    }

    .table-container thead th {
        background: linear-gradient(135deg, #1f77b4 0%, #0d5a9a 100%);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        position: sticky;
        top: 0;
        z-index: 10;
    }

    .table-container tbody td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-color);
    }

    .table-container tbody tr:hover {
        background-color: #f0f7ff;
        transition: background-color 0.2s ease;
    }

    .table-container tbody tr:nth-child(even) {
        background-color: #fafbfc;
    }

    .download-section {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1f77b4 0%, #0d5a9a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(31, 119, 180, 0.2) !important;
    }

    .stButton > button:hover {
        box-shadow: 0 6px 15px rgba(31, 119, 180, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    .stForm {
        border: none !important;
    }

    .stSelectbox, .stTextInput, .stDateInput {
        margin-bottom: 1rem;
    }

    .stAlert {
        border-radius: 8px !important;
        margin-bottom: 1rem;
    }

    .diameter-label {
        font-weight: 600;
        color: #333;
        margin-top: 0.5rem;
    }

    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }

    .download-section {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }

    .page-controls {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    body {
        background-color: #f5f7fa;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="Roll Profile Data Entry")

# --- Google Sheets Config ---
SHEET_NAME = "Roll_Data"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# --- Roll Config ---
DISTANCES = [100, 350, 600, 850, 1100, 1350, 1600]
MIN_DIA = 1245.0
MAX_DIA = 1352.0

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1>📊 Backup Roll Profile Data Entry</h1>
        <p>Manage and track roll specifications with ease</p>
    </div>
""", unsafe_allow_html=True)

# Load existing data
existing_data = sheet.get_all_records()
df = pd.DataFrame(existing_data)

# --- Entry Form ---
diameters = {}
with st.container():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    with st.form("entry_form", clear_on_submit=False):
        st.markdown("### ➕ Add New Roll Entry")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            entry_date = st.date_input("📅 Date", value=dt_date.today())
        with col2:
            roll_no = st.text_input("🏷️ Roll No (required)").strip().upper()
        with col3:
            stand = st.selectbox(" Stand", ['Select', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'ROUGHING', 'DC'], index=0)

        col1, col2 = st.columns(2)
        with col1:
            position = st.selectbox("📍 Position", ['Select', 'TOP', 'BOTTOM'], index=0)
        with col2:
            crown = st.selectbox(" Crown", ['Select', 'STRAIGHT', '+100 MICRON', '+200 MICRON'], index=0)

        st.markdown('<p class="diameter-label">📏 Diameters (mm) — must be between 1245 and 1352</p>', unsafe_allow_html=True)
        
        # Single column for diameter inputs
        diameters = {}
        for d in DISTANCES:
            val = st.text_input(f"{d} mm", value="", key=f"dia_{d}", placeholder="Enter value")
            try:
                diameters[d] = float(val) if val.strip() != "" else 0
            except ValueError:
                diameters[d] = 0

        submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)



# --- Save Entry ---
if submitted:
    errors = []

    if roll_no == "":
        errors.append("❌ Roll No cannot be empty")

    filtered_diameters = {}
    for d, v in diameters.items():
        if v == 0:
            continue
        if not (MIN_DIA <= v <= MAX_DIA):
            errors.append(f"❌ {d} mm value {v} out of range [{MIN_DIA}-{MAX_DIA}]")
        else:
            filtered_diameters[d] = v

    if errors:
        for e in errors:
            st.error(e)
    else:
        row = [str(entry_date), roll_no, stand, position, crown] + [filtered_diameters.get(d, "") for d in DISTANCES]
        sheet.append_row(row)
        st.success(f"✅ Entry saved for Roll No: {roll_no}")

        existing_data = sheet.get_all_records()
        df = pd.DataFrame(existing_data)

# --- Show Data ---
with st.container():
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.markdown("### 📋 Stored Data")
    
    if df.empty:
        st.markdown('<div class="info-box">📭 No entries yet. Start by adding a new roll entry above.</div>', unsafe_allow_html=True)
    else:
        for col in df.columns:
            if df[col].dtype in ["float64", "int64"]:
                df[col] = df[col].map(lambda x: f"{x:.2f}" if x != "" else "")

        df_display = df.reset_index(drop=True)

        # Pagination
        page_size = 10
        total_pages = (len(df_display) - 1) // page_size + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input("📄 Page", min_value=1, max_value=total_pages, step=1, label_visibility="collapsed")
        
        start = (page - 1) * page_size
        end = start + page_size

        # Display table with custom scrolling
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.dataframe(df_display.iloc[start:end], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; color: #666; font-size: 0.9rem; margin: 1rem 0;'>Page {page} of {total_pages} | Total entries: {len(df_display)}</p>", unsafe_allow_html=True)

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
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ Download Excel",
                data=to_excel_bytes(df),
                file_name="roll_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "⬇️ Download Word",
                data=to_word_bytes(df),
                file_name="roll_data.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
# ---------- Plot section: select Roll ID and plot profile by date ----------
import altair as alt

# Ensure distances list matches your sheet/order
DISTANCES = [100, 350, 600, 850, 1100, 1350, 1600]

st.markdown("## 📈 Plot Roll Profile")

# Guard if df empty
if df.empty:
    st.info("No data to plot.")
else:
    # Ensure Date column is datetime and Roll No exists
    if "Date" in df.columns:
        df_plot = df.copy()
        # Normalize column names (strip whitespace)
        df_plot.columns = [c.strip() for c in df_plot.columns]

        # Ensure Date is a datetime (if it's a string)
        try:
            df_plot["Date"] = pd.to_datetime(df_plot["Date"])
        except Exception:
            # if conversion fails, keep as string
            pass

        # Convert distance columns to numeric (if they're strings)
        for d in DISTANCES:
            col_name = str(d)
            if col_name in df_plot.columns:
                df_plot[col_name] = pd.to_numeric(df_plot[col_name], errors="coerce")

        # Select roll id
        roll_options = sorted(df_plot["Roll No"].astype(str).unique())
        selected_roll = st.selectbox("Select Roll No", ["-- choose --"] + roll_options)

        if selected_roll and selected_roll != "-- choose --":
            # Filter rows for the chosen roll
            roll_rows = df_plot[df_plot["Roll No"].astype(str) == str(selected_roll)].copy()

            if roll_rows.empty:
                st.warning("No rows found for that Roll No.")
            else:
                # Build a list of human-readable date labels (keep original format)
                # Use the string form for selection, but keep datetime internally.
                roll_rows["_date_str"] = roll_rows["Date"].dt.strftime("%Y-%m-%d") \
                    if pd.api.types.is_datetime64_any_dtype(roll_rows["Date"]) else roll_rows["Date"].astype(str)

                date_options = roll_rows["_date_str"].tolist()
                # allow multi-select (user can compare multiple dates)
                chosen_dates = st.multiselect("Select one or more Dates to plot (multiple lines)", options=date_options, default=[date_options[-1]])

                if not chosen_dates:
                    st.info("Select at least one date to plot.")
                else:
                    # Build long-form dataframe for Altair
                    melt_rows = []
                    for _, r in roll_rows.iterrows():
                        date_label = r["_date_str"]
                        if date_label not in chosen_dates:
                            continue
                        for d in DISTANCES:
                            col = str(d)
                            val = r.get(col, None)
                            # handle NaNs, blanks
                            try:
                                v = float(val) if (val is not None and str(val).strip() != "") else None
                            except Exception:
                                v = None
                            melt_rows.append({
                                "DateLabel": date_label,
                                "Distance": int(d),
                                "Diameter": v
                            })

                    if not melt_rows:
                        st.warning("No numeric diameter values found for the selected dates.")
                    else:
                        long_df = pd.DataFrame(melt_rows)

                        # optionally sort distances (ensures lines draw in order)
                        long_df = long_df.sort_values(["DateLabel", "Distance"])

                        # Altair chart: line + points, legend by DateLabel
                        base = alt.Chart(long_df).encode(
                            x=alt.X("Distance:Q", title="Distance (mm)", scale=alt.Scale(domain=[min(DISTANCES), max(DISTANCES)])),
                            y=alt.Y("Diameter:Q", title="Diameter (mm)"),
                            color=alt.Color("DateLabel:N", title="Date"),
                            tooltip=["DateLabel", "Distance", alt.Tooltip("Diameter", format=".2f")]
                        )

                        line = base.mark_line(point=True).interactive()
                        st.altair_chart(line, use_container_width=True)

                        # Show a small table summary below the chart
                        st.markdown("**Data plotted (sample):**")
                        st.dataframe(long_df.pivot_table(index="Distance", columns="DateLabel", values="Diameter"), use_container_width=True)


    st.markdown('</div>', unsafe_allow_html=True)


