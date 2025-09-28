import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from datetime import date as dt_date

# --- Configuration ---
DISTANCES = [100, 350, 600, 850, 1100, 1350, 1600]
MIN_DIA = 1200.0
MAX_DIA = 1400.0
PAGE_SIZE = 10

# --- Init session state storage for rows and form fields ---
if "data" not in st.session_state:
    cols = ["Entry No", "Date", "Roll No"] + [str(d) for d in DISTANCES]
    st.session_state.data = pd.DataFrame(columns=cols)

# initialize form field defaults
if "form_date" not in st.session_state:
    st.session_state.form_date = dt_date.today()
if "form_roll_no" not in st.session_state:
    st.session_state.form_roll_no = ""
for d in DISTANCES:
    key = f"form_d_{d}"
    if key not in st.session_state:
        st.session_state[key] = 0.0

st.title("Backup Roll Profile Data Entry ")

# --- Entry form ---
with st.form("entry_form", clear_on_submit=False):
    st.subheader("Add a roll ")
    entry_date = st.date_input("Date", key="form_date")

    roll_no_input = st.text_input(
        "Roll No (required)",
        key="form_roll_no",
        help="Will be stored in uppercase"
    )

    st.markdown("**Diameters (mm)** — values must be between 1200 and 1400")
    diam_inputs = {}
    for d in DISTANCES:
        diam_inputs[d] = st.number_input(f"{d} mm", key=f"form_d_{d}", step=0.01)

    submitted = st.form_submit_button("Add Entry")

# --- Validation and submission handling ---
if submitted:
    roll_no = roll_no_input.strip().upper()
    diams = {d: float(st.session_state[f"form_d_{d}"]) for d in DISTANCES}

    # Flags to check validity
    errors = {}

    if roll_no == "":
        errors["roll_no"] = "❌ Roll No cannot be empty."

    for d, v in diams.items():
        if not (MIN_DIA <= v <= MAX_DIA):
            errors[d] = f"❌ {d} mm value {v} out of range [{MIN_DIA}-{MAX_DIA}]."

    if errors:
        # Show inline errors under fields
        if "roll_no" in errors:
            st.error(errors["roll_no"])
        for d in DISTANCES:
            if d in errors:
                st.error(errors[d])
    else:
        # Append row
        new_entry_no = len(st.session_state.data) + 1
        row = {
            "Entry No": new_entry_no,
            "Date": entry_date.strftime("%Y-%m-%d"),
            "Roll No": roll_no,
        }
        for d, v in diams.items():
            row[str(d)] = v

        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([row])],
            ignore_index=True
        )
        st.success(f"✅ Entry {new_entry_no} added.")
        st.rerun()

# --- Display stored table ---
st.subheader("Stored Data")
if st.session_state.data.empty:
    st.info("No entries yet.")
else:
    total = len(st.session_state.data)
    total_pages = (total - 1) // PAGE_SIZE + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    st.dataframe(st.session_state.data.iloc[start:end].reset_index(drop=True), hide_index=True)

# --- Downloads ---
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

st.download_button(
    "Download Excel",
    data=to_excel_bytes(st.session_state.data),
    file_name="roll_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button(
    "Download Word",
    data=to_word_bytes(st.session_state.data),
    file_name="roll_data.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
