import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================== PAGE ==================
st.set_page_config(page_title="Questionnaire → Google Sheet", layout="wide")

# ================== GOOGLE SHEET ==================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def connect_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    sheet_name = st.secrets["app"]["spreadsheet_name"]
    ws_name = st.secrets["app"]["worksheet_name"]

    sh = gc.open(sheet_name)
    ws = sh.worksheet(ws_name)
    return ws

def append_row(ws, data: dict):
    # Append row by matching the header order (Row 1) in your Google Sheet.
    headers = ws.row_values(1)
    if not headers:
        raise ValueError("Header row (Row 1) is empty. Please set headers in Google Sheet first.")
    row = [data.get(h, "") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")

LIKERT = [1, 2, 3, 4, 5]
FREQ = ["Never", "Rarely", "Sometimes", "Often", "Always"]

st.title("Online Questionnaire (Streamlit → Google Sheets)")
st.caption("Setiap submit akan tambah 1 row ke Google Sheet.")

# ================== FORM ==================
with st.form("questionnaire_form", clear_on_submit=True):
    st.subheader("Section A – Basic Info")

    respondent_id = st.text_input("Respondent ID (optional)")
    role_multi = st.multiselect(
        "Role (boleh pilih lebih dari 1)",
        ["Chair", "Member", "Secretariat", "Regulator", "Industry", "Academia", "Other"],
    )
    committee_type = st.selectbox("Committee type", ["NSC", "WG", "SDA", "Other"])
    primary_sector_msic = st.text_input("Primary sector (MSIC)")
    freq_adoption_iso = st.selectbox("ISO adoption frequency", FREQ)

    st.divider()
    st.subheader("Section B – Likert Scale (1–5)")

    q1_market_need = st.radio("Q1. Market needs driven", LIKERT, horizontal=True)
    q2_regulatory_need = st.radio("Q2. Regulatory needs driven", LIKERT, horizontal=True)
    q3_consult_regulator = st.radio("Q3. Early regulator consultation", LIKERT, horizontal=True)
    q4_align_international = st.radio("Q4. International alignment", LIKERT, horizontal=True)

    st.divider()
    st.subheader("Section C – Process")

    q5_process_efficient = st.radio("Q5. Process efficient", LIKERT, horizontal=True)
    q6_enough_experts = st.radio("Q6. Enough experts", LIKERT, horizontal=True)
    q7_budget_sufficient = st.radio("Q7. Enough budget", LIKERT, horizontal=True)
    months_to_publish = st.number_input("Time NP → publication (months)", min_value=0, step=1)

    st.divider()
    st.subheader("Forward Agenda")

    priority_domains = st.multiselect(
        "Priority areas (pilih yang relevan)",
        ["AI", "Cybersecurity", "Green economy", "Halal", "Healthcare", "Construction", "Other"],
    )
    fast_track = st.text_area("Standard to fast-track (dan masalah yang diselesaikan)")
    retire_merge = st.text_area("Standard to retire/merge (dan sebab)")

    submitted = st.form_submit_button("Submit")

# ================== SAVE ==================
if submitted:
    try:
        ws = connect_sheet()

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "respondent_id": respondent_id.strip(),
            "role_multi": ";".join(role_multi),
            "committee_type": committee_type,
            "primary_sector_msic": primary_sector_msic.strip(),
            "freq_adoption_iso": freq_adoption_iso,

            "q1_market_need": q1_market_need,
            "q2_regulatory_need": q2_regulatory_need,
            "q3_consult_regulator": q3_consult_regulator,
            "q4_align_international": q4_align_international,

            "q5_process_efficient": q5_process_efficient,
            "q6_enough_experts": q6_enough_experts,
            "q7_budget_sufficient": q7_budget_sufficient,
            "months_to_publish": int(months_to_publish),

            "priority_domains": ">".join(priority_domains),
            "fast_track": fast_track.strip(),
            "retire_merge": retire_merge.strip(),
        }

        append_row(ws, row)
        st.success("✅ Berjaya! Data telah disimpan ke Google Sheet.")
    except Exception as e:
        st.error(f"❌ Gagal simpan ke Google Sheet: {e}")
        st.info("Semak: (1) Google Sheet sudah share ke service account, (2) header row 1 wujud & betul.")
