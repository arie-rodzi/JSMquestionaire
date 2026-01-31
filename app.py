import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="MSS Committees Questionnaire → Google Sheets", layout="wide")

# ================== GOOGLE SHEETS CONFIG ==================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def connect_sheet():
    """
    Uses SHEET_ID and SHEET_TAB from .streamlit/secrets.toml:
      SHEET_ID = "..."
      SHEET_TAB = "..."
    """
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    sheet_id = st.secrets["SHEET_ID"]
    tab_name = st.secrets["SHEET_TAB"]

    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(tab_name)
    return ws

def append_row_safe(ws, data: dict):
    """
    Append a row by matching the exact header order in Row 1 of your Google Sheet.
    Any header not found in `data` will be saved as blank.
    """
    headers = ws.row_values(1)
    if not headers:
        raise ValueError("Header row (Row 1) is empty. Please set headers in Google Sheet first.")
    row = [data.get(h, "") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")

# ================== UI CONSTANTS ==================
LIKERT = [1, 2, 3, 4, 5]
FREQ = ["Never", "Rarely", "Sometimes", "Often", "Always"]

# ================== APP HEADER ==================
st.title("MSS Committees Questionnaire")
st.caption("Responses will be appended as a new row in the connected Google Sheet (by SHEET_ID + SHEET_TAB).")

# ================== FORM ==================
with st.form("mss_committees_form", clear_on_submit=True):

    # ------------------ SECTION A ------------------
    st.subheader("SECTION A – DEMOGRAPHIC INFORMATION")

    respondent_id = st.text_input("Respondent ID (optional)")
    role_multi = st.multiselect(
        "Role (can choose more than 1):",
        ["Chair", "Member", "Secretariat", "Regulator", "Industry", "Academia", "CAB", "Other"]
    )
    committee_type = st.selectbox(
        "Committee type:",
        ["NSC", "WG", "SDA", "Regulatory committee/other"]
    )
    primary_sector_msic = st.text_input("Primary sector (MSIC):")
    themes_multi = st.multiselect(
        "Cross-cutting themes (optional):",
        ["ESG", "Digital/AI", "Halal", "Trade/MRA"]
    )
    ms_worked_3yrs = st.number_input(
        "Approx. number of MS worked on (past 3 years):",
        min_value=0, step=1
    )
    freq_adoption_iso = st.selectbox(
        "Frequency of adoption/adaptation of ISO/IEC/SMIIC:",
        FREQ
    )

    # ------------------ SECTION B ------------------
    st.divider()
    st.subheader("SECTION B – MARKET NEED, REGULATORY ALIGNMENT & INTERNATIONAL COHERENCE")

    st.caption(
        "This section also assesses alignment with international standards to facilitate trade and MRAs, "
        "as well as inclusivity (e.g., MSMEs) and cross-agency coherence. This section yields evidence on "
        "problem-driven prioritisation and policy congruence."
    )

    q06_market_need = st.radio(
        "6. Our standard development is driven by documented market needs (incl. RMK-12/13, NIMP 2030, i-ESG).",
        LIKERT, horizontal=True
    )
    q07_regulatory_need = st.radio(
        "7. Our standard development is driven by documented regulatory needs (incl. RMK-12/13, NIMP 2030, i-ESG).",
        LIKERT, horizontal=True
    )
    q08_consult_regulators_early = st.radio(
        "8. Our standard development consult regulators early to ensure referencing and avoid duplication.",
        LIKERT, horizontal=True
    )
    q09_align_international = st.radio(
        "9. Our standard development is align with international standards to support trade/MRAs.",
        LIKERT, horizontal=True
    )
    q10_msme_inclusivity = st.radio(
        "10. Our standard development we ensure Stakeholder involve mapping ensures MSME inclusivity and downstream adoption.",
        LIKERT, horizontal=True
    )
    q11_cross_agency_coherence = st.radio(
        "11. Our standard development, we ensure Cross-agency coherence.",
        LIKERT, horizontal=True
    )

    # ------------------ SECTION C ------------------
    st.divider()
    st.subheader("SECTION C – PROCESS EFFICIENCY & TIMELINESS")

    st.caption(
        "This section evaluates resource sufficiency (secretariat, experts, budget), digital tooling, and the "
        "efficiency of key process stages (proposal, drafting, public comment, consensus, editing). This section "
        "diagnoses process bottlenecks and identifies leverage points for cycle-time reduction without compromising quality."
    )

    q12_fast_enough = st.radio(
        "12. The current MS standard (eg. for Medical Devices/Digital Health) is fast enough to keep up with regulatory needs.",
        LIKERT, horizontal=True
    )
    q13_secretariat_capacity = st.radio(
        "13. We have sufficient secretariat capacity.",
        LIKERT, horizontal=True
    )
    q14_expert_availability = st.radio(
        "14. We have sufficient expert availability.",
        LIKERT, horizontal=True
    )
    q15_budget_sufficient = st.radio(
        "15. We have sufficient budget.",
        LIKERT, horizontal=True
    )
    q16_digital_tools_accelerate = st.radio(
        "16. We use of digital tools (collab platforms, templates, APIs) accelerates drafting.",
        LIKERT, horizontal=True
    )
    q17_process_steps_efficient = st.radio(
        "17. Our process steps (proposal, drafting, public comment, consensus, editing) are efficient.",
        LIKERT, horizontal=True
    )
    q18_np_to_publication_months = st.number_input(
        "18. Average time from new proposal (NP) to publication (months):",
        min_value=0, step=1
    )

    # ------------------ SECTION D ------------------
    st.divider()
    st.subheader("SECTION D – QUALITY, CLARITY & IMPLEMENTABILITY")

    st.caption(
        "This section assesses the provision of implementation aids (e.g., sector notes, examples, checklists) and appraisal "
        "of downstream costs. This section also considers translation, catalogue metadata, and API readiness to support discoverability and uptake."
    )

    q19_implementable_no_burden = st.radio(
        "19. The MS we produce are implementable without excessive documentation burden.",
        LIKERT, horizontal=True
    )
    q20_conformity_routes_clear = st.radio(
        "20. Conformity assessment routes are clear (SDoC/testing/certification/accreditation).",
        LIKERT, horizontal=True
    )
    q21_guidance_accompanies = st.radio(
        "21. Implementation guidance (sector notes, examples, checklists) accompanies publication.",
        LIKERT, horizontal=True
    )
    q22_evaluate_downstream_costs = st.radio(
        "22. We explicitly evaluate downstream costs (testing, certification, maintenance).",
        LIKERT, horizontal=True
    )
    q23_translation_metadata_api = st.radio(
        "23. We plan for translation, catalogue searchability and API metadata.",
        LIKERT, horizontal=True
    )

    # ------------------ SECTION E ------------------
    st.divider()
    st.subheader("SECTION E – EVIDENCE USE & IMPACT")

    st.caption(
        "This section examines the use of macro/meso evidence (productivity, exports, TFP) in prioritisation and the systematic capture "
        "of post-publication usage metrics (sales, citations, regulatory referencing). This section checks for ex-post portfolio hygiene "
        "(retire/merge/update low-use standards) and quantified case studies. This section embeds continuous improvement logic into our standards development."
    )

    q24_macro_meso_evidence = st.radio(
        "24. We consider macro/meso evidence (productivity, exports, TFP) when prioritising.",
        LIKERT, horizontal=True
    )
    q25_request_usage_metrics = st.radio(
        "25. We request post-publication usage metrics (sales, citations, regulatory referencing).",
        LIKERT, horizontal=True
    )
    q26_ex_post_reviews = st.radio(
        "26. We run ex-post reviews (24–36 months) to retire/merge/update low-use MS.",
        LIKERT, horizontal=True
    )
    q27_quantified_case_studies = st.radio(
        "27. We capture sectoral case studies with quantified benefits.",
        LIKERT, horizontal=True
    )
    q28_reg_clarity = st.radio(
        "28. Referencing MS has improved regulatory clarity and reduced compliance ambiguity.",
        LIKERT, horizontal=True
    )
    q29_reduce_duplication = st.radio(
        "29. Referencing MS reduces duplication between regulatory inspections and conformity assessment.",
        LIKERT, horizontal=True
    )
    q30_public_safety_health = st.radio(
        "30. MS have strengthened public safety and health outcomes.",
        LIKERT, horizontal=True
    )
    q31_environment = st.radio(
        "31. MS have strengthened environmental protection.",
        LIKERT, horizontal=True
    )
    q32_consumer_protection = st.radio(
        "32. MS have strengthened consumer protection",
        LIKERT, horizontal=True
    )
    q33_reference_enforcement = st.radio(
        "33. We use MS as a reference during market surveillance/enforcement activities.",
        LIKERT, horizontal=True
    )
    q34_risk_based_inspections = st.radio(
        "34. We use MS data to inform risk-based inspections.",
        LIKERT, horizontal=True
    )
    q35_reduce_regulator_burden = st.radio(
        "35. MS help reduce the burden on regulators by creating clearer compliance expectations",
        LIKERT, horizontal=True
    )

    # ------------------ SECTION F ------------------
    st.divider()
    st.subheader("SECTION F – SUPPORTS & CAPABILITY")

    st.caption(
        "This section assesses the level of organisational support and capability available to deliver the initiative/work."
    )

    q36_sufficient_experts_sms = st.radio(
        "36. We have sufficient experts/subject matter specialists to support delivery.",
        LIKERT, horizontal=True
    )
    q37_budget_adequate = st.radio(
        "37. The budget available is adequate to implement the required work.",
        LIKERT, horizontal=True
    )
    q38_response_timely = st.radio(
        "38. Response times from relevant parties are timely enough to avoid delays.",
        LIKERT, horizontal=True
    )
    q39_cross_agency_effective = st.radio(
        "39. Cross-agency coordination is effective and supports smooth implementation.",
        LIKERT, horizontal=True
    )
    q40_digital_tools_sufficient = st.radio(
        "40. Our digital tools/systems (e.g., data access, platforms, integration) are sufficient to support execution.",
        LIKERT, horizontal=True
    )
    q41_legal_drafting_support = st.radio(
        "41. We have adequate legal drafting support/capability for required documentation.",
        LIKERT, horizontal=True
    )
    q42_translation_support = st.radio(
        "42. Translation support is adequate to produce accurate and timely bilingual outputs",
        LIKERT, horizontal=True
    )
    q43_training_capacity = st.radio(
        "43. Training and capacity building are sufficient to ensure team readiness to deliver.",
        LIKERT, horizontal=True
    )

    # ------------------ SECTION G ------------------
    st.divider()
    st.subheader("SECTION G – FORWARD AGENDA (MSS 2026–2035)")

    st.caption(
        "This section collects ranked priorities for the next 24 months and requires one fast-track candidate (≤24 months) "
        "with a clearly articulated problem and one withdrawal/merger candidate with justification (usage, duplication, obsolescence). "
        "This section operationalises a “fewer-better-faster” approach to pipeline curation. This section links evidence to decision-making "
        "on initiation, acceleration, and retirement."
    )

    q44_priority_domains_rank = st.multiselect(
        "44. Priority domains next 24 months (rank up to 5):",
        [
            "AI/data",
            "Cybersecurity",
            "Green/circular economy",
            "Carbon/energy management",
            "EV/batteries/charging",
            "Medical devices/healthcare",
            "Agrifood safety/traceability",
            "Logistics & smart ports",
            "Construction/BIM",
            "Halal (incl. digital halal)",
            "Financial services/fintech",
            "Tourism/services",
            "Other",
        ],
        max_selections=5
    )

    q44_other_text = ""
    if "Other" in q44_priority_domains_rank:
        q44_other_text = st.text_input("If Other, please specify:")

    q45_fast_track_ms_problem = st.text_area(
        "45. Name one MS to fast-track (≤24 months) and the problem it solves:",
        height=120
    )

    q46_retire_merge_ms_reason = st.text_area(
        "46. Name one MS to retire/merge and why (usage, duplication, obsolescence):",
        height=120
    )

    submitted = st.form_submit_button("Submit")

# ================== SUBMIT HANDLER ==================
if submitted:
    try:
        ws = connect_sheet()

        row = {
            # --- Meta ---
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "respondent_id": respondent_id.strip(),
            "role_multi": ";".join(role_multi),
            "committee_type": committee_type,
            "primary_sector_msic": primary_sector_msic.strip(),
            "themes_multi": ";".join(themes_multi),
            "ms_worked_3yrs": int(ms_worked_3yrs),
            "freq_adoption_iso": freq_adoption_iso,

            # --- Section B ---
            "q06_market_need": q06_market_need,
            "q07_regulatory_need": q07_regulatory_need,
            "q08_consult_regulators_early": q08_consult_regulators_early,
            "q09_align_international": q09_align_international,
            "q10_msme_inclusivity": q10_msme_inclusivity,
            "q11_cross_agency_coherence": q11_cross_agency_coherence,

            # --- Section C ---
            "q12_fast_enough": q12_fast_enough,
            "q13_secretariat_capacity": q13_secretariat_capacity,
            "q14_expert_availability": q14_expert_availability,
            "q15_budget_sufficient": q15_budget_sufficient,
            "q16_digital_tools_accelerate": q16_digital_tools_accelerate,
            "q17_process_steps_efficient": q17_process_steps_efficient,
            "q18_np_to_publication_months": int(q18_np_to_publication_months),

            # --- Section D ---
            "q19_implementable_no_burden": q19_implementable_no_burden,
            "q20_conformity_routes_clear": q20_conformity_routes_clear,
            "q21_guidance_accompanies": q21_guidance_accompanies,
            "q22_evaluate_downstream_costs": q22_evaluate_downstream_costs,
            "q23_translation_metadata_api": q23_translation_metadata_api,

            # --- Section E ---
            "q24_macro_meso_evidence": q24_macro_meso_evidence,
            "q25_request_usage_metrics": q25_request_usage_metrics,
            "q26_ex_post_reviews": q26_ex_post_reviews,
            "q27_quantified_case_studies": q27_quantified_case_studies,
            "q28_reg_clarity": q28_reg_clarity,
            "q29_reduce_duplication": q29_reduce_duplication,
            "q30_public_safety_health": q30_public_safety_health,
            "q31_environment": q31_environment,
            "q32_consumer_protection": q32_consumer_protection,
            "q33_reference_enforcement": q33_reference_enforcement,
            "q34_risk_based_inspections": q34_risk_based_inspections,
            "q35_reduce_regulator_burden": q35_reduce_regulator_burden,

            # --- Section F ---
            "q36_sufficient_experts_sms": q36_sufficient_experts_sms,
            "q37_budget_adequate": q37_budget_adequate,
            "q38_response_timely": q38_response_timely,
            "q39_cross_agency_effective": q39_cross_agency_effective,
            "q40_digital_tools_sufficient": q40_digital_tools_sufficient,
            "q41_legal_drafting_support": q41_legal_drafting_support,
            "q42_translation_support": q42_translation_support,
            "q43_training_capacity": q43_training_capacity,

            # --- Section G ---
            "q44_priority_domains_rank": ">".join([x for x in q44_priority_domains_rank if x != "Other"]),
            "q44_other_text": q44_other_text.strip(),
            "q45_fast_track_ms_problem": q45_fast_track_ms_problem.strip(),
            "q46_retire_merge_ms_reason": q46_retire_merge_ms_reason.strip(),
        }

        append_row_safe(ws, row)
        st.success("✅ Submitted successfully. Your response has been saved to Google Sheet.")

    except Exception as e:
        st.error(f"❌ Error saving to Google Sheet: {e}")
        st.info("Check: (1) Sheet is shared with the service account, (2) Row 1 headers exist & match your keys.")
