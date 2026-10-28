from pathlib import Path
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from audit_history import record_audit, load_history
from report_generator import generate_audit_report
from audit_comparison import compare_audit_runs

from audit_engine import run_audit

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "employees.csv"
REMEDIATION_FILE = BASE_DIR / "data" / "remediation.json"

SEVERITY_ORDER = ["Critical", "High", "Medium"]
SEVERITY_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
}

st.set_page_config(
    page_title="AccessGuard | Technology Risk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# VISUAL DESIGN
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --bg: #F5F7FB;
    --surface: #FFFFFF;
    --text: #18243A;
    --muted: #68768D;
    --border: #E1E7F0;
    --blue: #3659D9;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp,
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.block-container {
    max-width: 1600px;
    padding-top: 0.9rem !important;
    padding-right: 2rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
}

.block-container h1 {
    margin-top: 0.25rem !important;
    margin-bottom: 0.2rem !important;
    line-height: 1.35 !important;
    overflow: visible !important;
}

/* Compact headings */
h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.025em;
}

h1 {
    font-size: 1.8rem !important;
    margin-bottom: 0.15rem !important;
}

h2 {
    font-size: 1.3rem !important;
}

h3 {
    font-size: 1rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{
    gap: 0.3rem;
}

[data-testid="stSidebar"] hr {
    margin: 0.8rem 0;
    border-color: var(--border);
}

/* Smaller, consistent KPI cards */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    box-shadow: 0 2px 5px rgba(24, 36, 58, 0.025);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 1.65rem !important;
    font-weight: 800;
}

/* Tabs: readable in both selected and unselected states */
[data-testid="stTabs"] [role="tablist"] {
    gap: 1.1rem;
    border-bottom: 1px solid var(--border);
    padding-top: 0 !important;
    margin-top: 0 !important;
}

[data-testid="stTabs"] button[role="tab"] {
    color: #53627A !important;
    background: transparent !important;
    font-weight: 600;
    padding: 0.7rem 0.15rem;
}

[data-testid="stTabs"] button[role="tab"]:hover {
    color: var(--blue) !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
}

/* File uploader: restore contrast */
[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border-radius: 10px;
}

[data-testid="stFileUploader"] section {
    background: #F8FAFD !important;
    border: 1px dashed #B8C5D8 !important;
    border-radius: 10px !important;
    padding: 0.8rem !important;
}

[data-testid="stFileUploader"] section button {
    background: #FFFFFF !important;
    color: #263750 !important;
    border: 1px solid #C7D2E2 !important;
    border-radius: 7px !important;
}

[data-testid="stFileUploader"] section button:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
}

/* Other buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"] {
    background: var(--blue) !important;
    color: #FFFFFF !important;
    border-color: var(--blue) !important;
}

.stDownloadButton > button {
    background: #FFFFFF !important;
    color: var(--text) !important;
    border: 1px solid #C7D2E2 !important;
}

/* Inputs and tables */
.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: var(--text) !important;
    border-color: #D5DEEA !important;
    border-radius: 8px !important;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border-color: var(--border) !important;
    border-radius: 12px;
}

/* Less vertical space between elements */
[data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

hr {
    border-color: var(--border);
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }
    h1 {
        font-size: 1.5rem !important;
    }
}

/* Compact the main dashboard header */
.block-container h1 {
    margin-top: 0 !important;
    margin-bottom: 0.1rem !important;
    line-height: 1.2 !important;
}

/* Reduce spacing between the header's text elements */
.block-container h1 + div {
    margin-top: 0 !important;
}

/* Tighten Streamlit's vertical layout */
.block-container [data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}

/* Reduce excess space around horizontal separators */
.block-container hr {
    margin-top: 0.25rem !important;
    margin-bottom: 0.2rem !important;
}

/* Keep KPI cards compact */
[data-testid="stMetric"] {
    min-height: 88px !important;
    padding: 0.7rem 1rem !important;
}

/* Reduce space above the navigation tabs */
[data-testid="stTabs"] {
    margin-top: 0rem !important;
    padding-top: 0rem !important;
}

/* Keep the page content from creating artificial height */
[data-testid="stPlotlyChart"] {
    margin-top: 0 !important;
}

/* Give the KPI row room above and below */
.block-container [data-testid="stHorizontalBlock"] {
    margin-top: 0.5rem;
    margin-bottom: 0.75rem;
}

/* Ensure metric cards have comfortable internal spacing */
[data-testid="stMetric"] {
    min-height: 96px !important;
    padding: 0.9rem 1rem !important;
    margin-top: 0.2rem;
}

/* Restore comfortable spacing around separators */
.block-container hr {
    margin-top: 0.9rem !important;
    margin-bottom: 0.9rem !important;
}

/* Don't clip the title or other content */
.block-container {
    overflow: visible !important;
}

/* Remove unused space above sidebar branding */
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    margin-top: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}


</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# REMEDIATION STORAGE
# --------------------------------------------------

def load_remediation():
    if not REMEDIATION_FILE.exists():
        return {}

    try:
        with REMEDIATION_FILE.open("r", encoding="utf-8") as file:
            result = json.load(file)
        return result if isinstance(result, dict) else {}
    except (OSError, json.JSONDecodeError):
        st.warning(
            "The saved remediation file could not be read. "
            "Existing records were not overwritten."
        )
        return {}


def save_remediation(records):
    REMEDIATION_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    temporary_file = REMEDIATION_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    temporary_file.replace(REMEDIATION_FILE)


if "remediation" not in st.session_state:
    st.session_state.remediation = load_remediation()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🛡️ AccessGuard")
    st.caption("TECHNOLOGY RISK · ACCESS ASSURANCE")
    st.divider()

    st.subheader("Audit workspace")

    uploaded_file = st.file_uploader(
        "Employee access records",
        type=["csv"],
        help="Upload a CSV matching the required employee schema.",
    )

    st.caption(
        "Demo mode uses fictional data. "
        "Only upload data you are authorized to process."
    )

    st.divider()

    st.markdown("**Control framework**")
    st.caption("AC-01 · Leaver access")
    st.caption("AC-02 · Privileged access")
    st.caption("AC-03 · Segregation of duties")
    st.caption("AC-04 · Dormant accounts")
    st.caption("AC-05 · Data quality")

# -------------------------------------------------- 
# LOAD AND VALIDATE DATA
# --------------------------------------------------

try:
    if uploaded_file is not None:
        employees = pd.read_csv(uploaded_file)
        source_name = "Uploaded dataset"
    else:
        employees = pd.read_csv(DATA_FILE)
        source_name = "Synthetic demonstration dataset"

    findings = run_audit(employees)

except (ValueError, KeyError, OSError, pd.errors.ParserError) as exc:
    st.error("The audit could not be completed.")
    st.write(str(exc))
    st.info(
        "Check the CSV column names, data types, employee IDs "
        "and file formatting. The required schema is listed "
        "under the Methodology tab after loading a valid dataset."
    )
    st.stop()

except Exception as exc:
    st.error("An unexpected error occurred while running the audit.")
    st.caption(f"Technical details: {exc}")
    st.stop()

# --------------------------------------------------
# AUDIT REPORT DOWNLOAD
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.subheader("Audit report")

try:
    pdf_report = generate_audit_report(
        employees,
        findings,
        source_name,
    )

    st.sidebar.download_button(
        label="Download audit report (PDF)",
        data=pdf_report,
        file_name="AccessGuard_Audit_Report.pdf",
        mime="application/pdf",
    )

except Exception as exc:
    st.sidebar.error(f"Could not generate report: {exc}")
# --------------------------------------------------
# AUDIT RUN HISTORY
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.subheader("Audit run history")

if st.sidebar.button("Record current audit run", type="primary"):
    try:
        saved_run = record_audit(
            employees,
            findings,
            source_name,
        )
        st.session_state["last_recorded_run_id"] = saved_run["run_id"]
        st.sidebar.success(
            "Audit run saved: " + saved_run["run_id"][:8]
        )
    except (OSError, RuntimeError, ValueError) as exc:
        st.sidebar.error(f"Could not save audit run: {exc}")

try:
    history = load_history()
    st.sidebar.caption(f"{len(history)} recorded audit run(s)")
except RuntimeError as exc:
    history = []
    st.sidebar.error(str(exc))

# --------------------------------------------------
# NORMALIZE RESULTS AND METRICS
# --------------------------------------------------

total_accounts = len(employees)
total_findings = len(findings)

if not findings.empty:
    findings["severity"] = findings["severity"].astype(str)

    # Prevent unexpected severities from breaking the dashboard.
    unknown_severities = sorted(
        set(findings["severity"]) - set(SEVERITY_ORDER)
    )

    if unknown_severities:
        st.warning(
            "The audit engine returned unrecognized severity labels: "
            + ", ".join(unknown_severities)
        )

    critical_count = int(
        (findings["severity"] == "Critical").sum()
    )
    high_count = int(
        (findings["severity"] == "High").sum()
    )
    medium_count = int(
        (findings["severity"] == "Medium").sum()
    )
else:
    critical_count = high_count = medium_count = 0

# A finding count is not a count of distinct employees.
affected_accounts = (
    findings["employee_id"].nunique()
    if not findings.empty else 0
)


def remediation_for(finding_id):
    return st.session_state.remediation.get(
        finding_id,
        {
            "status": "Open",
            "owner": "",
            "due_date": "",
            "notes": "",
        },
    )


def remediation_status(finding_id):
    return remediation_for(finding_id)["status"]

# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

header_title, header_status = st.columns([4, 1])

with header_title:
    st.title("Access Control Overview")
    st.markdown(
        '<p class="ag-muted">Access governance · Control testing · '
        'Risk remediation</p>',
        unsafe_allow_html=True,
    )

with header_status:
    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div style="
        margin: 0.15rem 0 0.9rem 0;
        color: #68768D;
        font-size: 0.92rem;
    ">
        Reviewing <strong>{total_accounts:,}</strong> employee records
        from <strong>{source_name}</strong>. Identify potential
        access-control exceptions and coordinate remediation.
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# TOP-LEVEL METRICS
# --------------------------------------------------

m1, m2, m3, m4, m5 = st.columns(5, gap="small")

with m1:
    st.metric("Accounts reviewed", f"{total_accounts:,}")

with m2:
    st.metric("Potential findings", f"{total_findings:,}")

with m3:
    st.metric("Critical findings", f"{critical_count:,}")

with m4:
    st.metric("High-risk findings", f"{high_count:,}")

with m5:
    st.metric("Affected accounts", f"{affected_accounts:,}")

st.divider()

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

overview_tab, findings_tab, remediation_tab, methodology_tab, history_tab, comparison_tab = (
    st.tabs([
        "Overview",
        "Findings",
        "Remediation",
        "Methodology",
        "Audit History",
        "Run Comparison"
    ])
)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

with overview_tab:
    st.subheader("Risk distribution")
    st.caption(
        "Counts represent rule-triggered findings, "
        "not confirmed security incidents."
    )

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("**Findings by severity**")

        severity_data = pd.DataFrame({
            "Severity": SEVERITY_ORDER,
            "Findings": [
                critical_count,
                high_count,
                medium_count,
            ],
        })

        if total_findings:
            fig = px.bar(
                severity_data,
                x="Severity",
                y="Findings",
                color="Severity",
                color_discrete_map=SEVERITY_COLORS,
                category_orders={"Severity": SEVERITY_ORDER},
                text="Findings",
            )
            
            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(
                    family="DM Sans, sans-serif",
                    color="#53627A",
                    size=12,
                ),
                height=260,
                showlegend=False,
                margin=dict(l=10, r=10, t=25, b=10),
                xaxis_title=None,
                yaxis_title="Finding count",
                yaxis=dict(
                    gridcolor="#E8EDF4",
                    zeroline=False,
                ),
                xaxis=dict(
                    showgrid=False,
                    linecolor="#E1E7F0",
                ),
            )

            fig.update_traces(
                textposition="outside",
                cliponaxis=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No findings were detected by the configured rules.")

    with chart_right:
        st.markdown("**Findings by control**")

        control_names = {
            "AC-01": "Leaver access",
            "AC-02": "Privileged access",
            "AC-03": "Duty conflicts",
            "AC-04": "Dormant accounts",
            "AC-05": "Data quality",
        }

        if total_findings:
            control_data = (
                findings.groupby("rule_id")
                .size()
                .rename("Findings")
                .reset_index()
            )

            control_data["Control"] = (
                control_data["rule_id"]
                .map(control_names)
                .fillna(control_data["rule_id"])
            )

            fig2 = px.bar(
                control_data,
                x="Control",
                y="Findings",
                text="Findings",
                color_discrete_sequence=["#4776C5"],
                template="plotly_white",
            )
            fig2.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(
                    family="DM Sans, sans-serif",
                    color="#53627A",
                    size=12,
                ),
                height=260,
                showlegend=False,
                margin=dict(l=10, r=10, t=25, b=10),
                xaxis_title=None,
                yaxis_title="Finding count",
                yaxis=dict(
                    gridcolor="#E8EDF4",
                    zeroline=False,
                ),
                xaxis=dict(
                    showgrid=False,
                    linecolor="#E1E7F0",
                ),
            )
            fig2.update_traces(
                textposition="outside",
                cliponaxis=False,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("There are no control findings to display.")

    st.divider()

    st.subheader("Priority findings")

    if total_findings:
        priority_order = {
            "Critical": 0,
            "High": 1,
            "Medium": 2,
        }

        priority = findings.copy()
        priority["_priority"] = (
            priority["severity"].map(priority_order).fillna(99)
        )
        priority = priority.sort_values(
            ["_priority", "employee_id"]
        ).head(5)

        preview = priority[[
            "finding_id",
            "employee_name",
            "finding",
            "severity",
        ]].copy()

        preview["status"] = preview["finding_id"].map(
            remediation_status
        )

        st.dataframe(
            preview,
            hide_index=True,
            use_container_width=True,
            column_config={
                "finding_id": "Finding ID",
                "employee_name": "Employee",
                "finding": "Finding",
                "severity": "Severity",
                "status": "Remediation status",
            },
        )

        st.caption(
            "Review each finding before determining whether a "
            "control failure is confirmed."
        )
    else:
        st.success("No findings require prioritization.")

# --------------------------------------------------
# FINDINGS WORKBENCH
# --------------------------------------------------

with findings_tab:
    st.subheader("Findings workbench")
    st.caption(
        "Search, prioritize and investigate exceptions identified "
        "by the configured access-control tests."
    )

    if findings.empty:
        st.success("No findings were generated by the configured rules.")
    else:
        # -------------------------------
        # FINDINGS SUMMARY
        # -------------------------------
        critical_total = int(
            (findings["severity"] == "Critical").sum()
        )
        high_total = int(
            (findings["severity"] == "High").sum()
        )
        medium_total = int(
            (findings["severity"] == "Medium").sum()
        )

        summary1, summary2, summary3, summary4 = st.columns(4)

        summary1.metric("Total findings", len(findings))
        summary2.metric("Critical", critical_total)
        summary3.metric("High", high_total)
        summary4.metric("Medium", medium_total)

        st.divider()

        # -------------------------------
        # SEARCH AND FILTERS
        # -------------------------------
        st.markdown("#### Find exceptions")

        search_term = st.text_input(
            "Search",
            placeholder="Employee, finding ID, control or keyword...",
            key="finding_search",
        )

        filter_left, filter_middle, filter_right = st.columns(3)

        with filter_left:
            selected_severities = st.multiselect(
                "Severity",
                SEVERITY_ORDER,
                default=SEVERITY_ORDER,
                key="findings_severity_filter",
            )

        with filter_middle:
            available_rules = [
                "AC-01",
                "AC-02",
                "AC-03",
                "AC-04",
                "AC-05",
            ]

            selected_rule_ids = st.multiselect(
                "Control rule",
                available_rules,
                default=available_rules,
                format_func=lambda rule: (
                    f"{rule} · {control_names.get(rule, rule)}"
                ),
                key="findings_rule_filter",
            )

        with filter_right:
            all_statuses = [
                "Open",
                "Under review",
                "Remediation in progress",
                "Resolved",
            ]

            selected_statuses = st.multiselect(
                "Remediation status",
                all_statuses,
                default=all_statuses,
                key="findings_status_filter",
            )

        filtered = findings[
            findings["severity"].isin(selected_severities)
            & findings["rule_id"].isin(selected_rule_ids)
        ].copy()

        filtered["status"] = filtered["finding_id"].map(
            remediation_status
        )

        filtered = filtered[
            filtered["status"].isin(selected_statuses)
        ]

        if search_term.strip():
            search_columns = [
                "finding_id",
                "employee_id",
                "employee_name",
                "finding",
                "rule_id",
                "evidence",
            ]

            mask = pd.Series(False, index=filtered.index)

            for column in search_columns:
                mask |= (
                    filtered[column]
                    .astype(str)
                    .str.contains(
                        search_term.strip(),
                        case=False,
                        na=False,
                        regex=False,
                    )
                )

            filtered = filtered[mask]

        st.markdown(
            f"**{len(filtered)}** of **{len(findings)}** findings shown"
        )

        # -------------------------------
        # FINDINGS TABLE
        # -------------------------------
        display_columns = [
            "finding_id",
            "employee_id",
            "employee_name",
            "rule_id",
            "finding",
            "severity",
            "status",
        ]

        display = filtered[display_columns].copy()

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            height=(len(display) + 1) * 35 + 3,
            column_config={
                "finding_id": st.column_config.TextColumn(
                    "Finding ID",
                    width="small",
                ),
                "employee_id": st.column_config.TextColumn(
                    "Employee ID",
                    width="small",
                ),
                "employee_name": st.column_config.TextColumn(
                    "Employee",
                    width="medium",
                ),
                "rule_id": st.column_config.TextColumn(
                    "Control",
                    width="small",
                ),
                "finding": st.column_config.TextColumn(
                    "Potential exception",
                    width="large",
                ),
                "severity": st.column_config.TextColumn(
                    "Severity",
                    width="small",
                ),
                "status": st.column_config.TextColumn(
                    "Remediation status",
                    width="medium",
                ),
            },
        )

        # Export only the currently filtered results.
        export_data = filtered.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download filtered findings (CSV)",
            data=export_data,
            file_name="accessguard_filtered_findings.csv",
            mime="text/csv",
        )

        st.divider()

        # -------------------------------
        # FINDING INVESTIGATION
        # -------------------------------
        st.markdown("#### Investigate a finding")

        finding_options = filtered["finding_id"].tolist()

        if finding_options:
            chosen_id = st.selectbox(
                "Choose a finding to inspect",
                finding_options,
                format_func=lambda value: (
                    f"{value} · "
                    + str(
                        filtered.loc[
                            filtered["finding_id"] == value,
                            "finding",
                        ].iloc[0]
                    )
                ),
                key="finding_detail_selector",
            )

            record = findings.loc[
                findings["finding_id"] == chosen_id
            ].iloc[0]

            st.markdown(f"### {record['finding']}")

            detail_status = remediation_status(chosen_id)

            meta1, meta2, meta3 = st.columns(3)

            meta1.markdown("**Employee**")
            meta1.write(
                f"{record['employee_name']} ({record['employee_id']})"
            )

            meta2.markdown("**Control**")
            meta2.write(
                f"{record['rule_id']} · "
                f"{control_names.get(record['rule_id'], record['rule_id'])}"
            )

            meta3.markdown("**Remediation status**")
            meta3.write(detail_status)

            if record["severity"] == "Critical":
                st.error(f"Critical severity · {record['severity']}")
            elif record["severity"] == "High":
                st.warning(f"High severity · {record['severity']}")
            else:
                st.info(f"Medium severity · {record['severity']}")

            evidence_col, action_col = st.columns(2)

            with evidence_col:
                with st.container(border=True):
                    st.markdown("**Observed evidence**")
                    st.write(record["evidence"])

            with action_col:
                with st.container(border=True):
                    st.markdown("**Recommended action**")
                    st.write(record["recommended_action"])

            st.caption(
                "These are rule-generated screening results. "
                "Validate the evidence and business context before "
                "confirming a control exception or marking it resolved."
            )

        else:
            st.info(
                "No findings match the current filters. "
                "Adjust the filters or clear your search."
            )

# --------------------------------------------------
# REMEDIATION TRACKER
# --------------------------------------------------

with remediation_tab:
    st.subheader("Remediation management")
    st.caption(
        "Record an owner, due date, status and reviewer notes "
        "for each detected finding."
    )

    if findings.empty:
        st.info("No findings are available for remediation.")
    else:
        remediation_rows = []

        for _, record in findings.iterrows():
            state = remediation_for(record["finding_id"])

            remediation_rows.append({
                "finding_id": record["finding_id"],
                "employee_name": record["employee_name"],
                "finding": record["finding"],
                "severity": record["severity"],
                "status": state["status"],
                "owner": state["owner"],
                "due_date": state["due_date"],
            })

        remediation_df = pd.DataFrame(remediation_rows)

        open_count = int(
            (remediation_df["status"] == "Open").sum()
        )
        progress_count = int(
            (
                remediation_df["status"]
                == "Remediation in progress"
            ).sum()
        )
        resolved_count = int(
            (remediation_df["status"] == "Resolved").sum()
        )

        r1, r2, r3 = st.columns(3)
        r1.metric("Open", open_count)
        r2.metric("In progress", progress_count)
        r3.metric("Resolved", resolved_count)

        st.dataframe(
            remediation_df,
            hide_index=True,
            use_container_width=True,
        )

        st.divider()
        st.markdown("**Update remediation record**")

        selected_id = st.selectbox(
            "Finding",
            findings["finding_id"].tolist(),
            key="remediation_finding",
        )

        selected_record = findings.loc[
            findings["finding_id"] == selected_id
        ].iloc[0]

        current = remediation_for(selected_id)

        st.write(
            f"**{selected_record['finding']}** — "
            f"{selected_record['employee_name']}"
        )

        with st.form("remediation_form"):
            new_status = st.selectbox(
                "Status",
                [
                    "Open",
                    "Under review",
                    "Remediation in progress",
                    "Resolved",
                ],
                index=[
                    "Open",
                    "Under review",
                    "Remediation in progress",
                    "Resolved",
                ].index(current["status"]),
            )

            new_owner = st.text_input(
                "Remediation owner",
                value=current["owner"],
            )

            current_due_date = current.get("due_date", "")
            due_date_value = None

            if current_due_date:
                try:
                    due_date_value = datetime.strptime(
                        current_due_date, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    due_date_value = None

            new_due_date = st.date_input(
                "Target completion date",
                value=due_date_value,
            )

            new_notes = st.text_area(
                "Reviewer notes",
                value=current["notes"],
                placeholder=(
                    "Record the action taken, evidence reviewed "
                    "and any outstanding work."
                ),
            )

            submitted = st.form_submit_button(
                "Save remediation record",
                type="primary",
            )

        if submitted:
            updated = dict(st.session_state.remediation)
            updated[selected_id] = {
                "status": new_status,
                "owner": new_owner.strip(),
                "due_date": new_due_date.isoformat(),
                "notes": new_notes.strip(),
                "updated_at": datetime.now().isoformat(
                    timespec="seconds"
                ),
            }

            try:
                save_remediation(updated)
                st.session_state.remediation = updated
                st.success("Remediation record saved locally.")
                st.rerun()
            except OSError as exc:
                st.error(f"Could not save the record: {exc}")

        st.download_button(
            "Export remediation register",
            data=remediation_df.to_csv(index=False).encode("utf-8"),
            file_name="accessguard_remediation_register.csv",
            mime="text/csv",
        )

        st.caption(
            "Local JSON storage is suitable for this prototype only. "
            "It does not provide multi-user access controls, "
            "tamper-evident audit logs or database backups."
        )

# --------------------------------------------------
# METHODOLOGY
# --------------------------------------------------

with methodology_tab:
    st.subheader("Audit methodology")

    st.write(
        "AccessGuard applies deterministic rules to a supplied "
        "employee access dataset. Each rule identifies a potential "
        "exception that requires auditor validation."
    )

    methodology = pd.DataFrame([
        {
            "Rule": "AC-01",
            "Control": "Leaver access",
            "Test": (
                "Employment status is Terminated and "
                "account status is Active."
            ),
            "Assigned severity": "Critical",
            "Validation required": (
                "Confirm HR termination and verify access "
                "revocation evidence."
            ),
        },
        {
            "Rule": "AC-02",
            "Control": "Privileged access",
            "Test": (
                "Role matches admin, administrator or superadmin."
            ),
            "Assigned severity": "High",
            "Validation required": (
                "Check approval, role necessity and "
                "periodic access review."
            ),
        },
        {
            "Rule": "AC-03",
            "Control": "Segregation of duties",
            "Test": (
                "Permissions contain create_vendor and "
                "approve_payment."
            ),
            "Assigned severity": "High",
            "Validation required": (
                "Confirm the permissions are effective and "
                "the duties conflict in the actual workflow."
            ),
        },
        {
            "Rule": "AC-04",
            "Control": "Dormant accounts",
            "Test": (
                "Account is Active and last login is "
                "more than 90 days ago."
            ),
            "Assigned severity": "Medium",
            "Validation required": (
                "Check service-account exceptions, approved "
                "leave and ongoing business need."
            ),
        },
        {
            "Rule": "AC-05",
            "Control": "Data quality",
            "Test": (
                "Last-login date is missing, invalid or in the future."
            ),
            "Assigned severity": "Medium",
            "Validation required": (
                "Verify source data  before concluding the access review."
            ),
        },
    ])

    st.dataframe(
        methodology,
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("**Required CSV columns**")

    required_columns = [
        "employee_id",
        "employee_name",
        "department",
        "employment_status",
        "account_status",
        "role",
        "last_login",
        "permissions",
    ]

    st.code(", ".join(required_columns), language="text")

    st.markdown("**Important limitations**")

    st.markdown("""
    - Results are rule-triggered exceptions, not confirmed incidents.
    - Severity labels are illustrative and require risk-based validation.
    - AC-02 identifies privileged roles for review; it does not prove
      that the privilege is unauthorized.
    - AC-03 only tests the specific permission combination implemented.
    - AC-04 does not independently validate legitimate inactivity.
    - The prototype does not connect to a real identity provider.
    - Local remediation records are not tamper-evident audit evidence.
    """)

    st.caption(
        "AccessGuard is an educational portfolio prototype, "
        "not a certification or substitute for a formal audit."
    )

with history_tab:
    st.subheader("Audit run history")
    st.caption(
        "Previously recorded audit snapshots. "
        "Each record contains the results saved at that time."
    )

    try:
        runs = load_history()
    except RuntimeError as exc:
        st.error(str(exc))
        runs = []

    if not runs:
        st.info(
            "No audit runs recorded yet. Use "
            "'Record current audit run' in the sidebar."
        )
    else:
        # Newest runs first
        recent_runs = list(reversed(runs))

        # Format timestamps for display in Indian Standard Time
        def format_timestamp(timestamp):
            return (
                pd.to_datetime(timestamp, utc=True)
                .tz_convert("Asia/Kolkata")
                .strftime("%d %b %Y, %I:%M:%S %p IST")
            )

        history_df = pd.DataFrame([
            {
                "Run ID": f"RUN-{run['run_id'][:8].upper()}",
                "Timestamp (IST)": format_timestamp(
                    run["run_time_utc"]
                ),
                "Source": run["source_name"],
                "Ruleset": run["ruleset_version"],
                "Accounts reviewed": run["accounts_reviewed"],
                "Findings": run["findings_count"],
                "Affected accounts": run["unique_affected_accounts"],
            }
            for run in recent_runs
        ])

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Run ID": st.column_config.TextColumn(
                    "Run ID",
                    help="Short display identifier. The full UUID is retained below.",
                ),
                "Timestamp (IST)": st.column_config.TextColumn(
                    "Timestamp (IST)",
                    help="Time converted from UTC to Indian Standard Time.",
                ),
            },
        )

        st.download_button(
            "Export audit run history",
            data=history_df.to_csv(index=False).encode("utf-8"),
            file_name="accessguard_audit_history.csv",
            mime="text/csv",
        )

        st.divider()
        st.markdown("#### Inspect saved run")

        selected_run_id = st.selectbox(
            "Select an audit run",
            [run["run_id"] for run in recent_runs],
            format_func=lambda value: (
                f"RUN-{value[:8].upper()} · "
                + format_timestamp(
                    next(
                        run["run_time_utc"]
                        for run in recent_runs
                        if run["run_id"] == value
                    )
                )
            ),
            key="history_run_selector",
        )

        selected_run = next(
            run for run in recent_runs
            if run["run_id"] == selected_run_id
        )

        st.markdown("#### Saved run details")

        detail1, detail2, detail3 = st.columns(3)

        detail1.metric(
            "Accounts reviewed",
            selected_run["accounts_reviewed"],
        )
        detail2.metric(
            "Findings",
            selected_run["findings_count"],
        )
        detail3.metric(
            "Affected accounts",
            selected_run["unique_affected_accounts"],
        )

        st.divider()

        # Severity summary displayed directly on the page
        st.markdown("#### Severity summary")

        severity_counts = selected_run.get("severity_counts", {})

        severity_styles = {
            "Critical": ("#D64550", "Critical findings"),
            "High": ("#D99024", "High-risk findings"),
            "Medium": ("#4776C5", "Medium-risk findings"),
        }

        severity_columns = st.columns(3, gap="medium")

        for column, (severity, (color, label)) in zip(
            severity_columns, severity_styles.items()
        ):
            with column:
                st.markdown(
                    f"""
                    <div style="
                        background: #FFFFFF;
                        border: 1px solid #DFE6F0;
                        border-radius: 14px;
                        padding: 20px;
                        min-height: 124px;
                        box-shadow: 0 2px 5px rgba(20, 40, 80, 0.04);
                    ">
                        <div style="
                            color: {color};
                            font-size: 0.95rem;
                            margin-bottom: 12px;
                        ">{label}</div>
                        <div style="
                            color: #172033;
                            font-size: 2rem;
                            font-weight: 650;
                            line-height: 1.2;
                        ">{severity_counts.get(severity, 0)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")
        snapshot = pd.DataFrame(selected_run["findings"])

        st.markdown("#### Findings snapshot")

        if snapshot.empty:
            st.success("No findings were saved for this run.")
        else:
            st.dataframe(
                snapshot,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "Export saved findings snapshot",
                data=snapshot.to_csv(index=False).encode("utf-8"),
                file_name=(
                    f"accessguard_{selected_run_id[:8]}.csv"
                ),
                mime="text/csv",
                key=f"export_{selected_run_id}",
            )
            
with comparison_tab:
    st.header("Audit Run Comparison")
    st.write(
        "Compare findings from two saved runs to identify "
        "new, continuing, and resolved control exceptions."
    )

    try:
        saved_runs = load_history()
    except RuntimeError as exc:
        st.error(f"Could not load audit history: {exc}")
        saved_runs = []

    if len(saved_runs) < 2:
        st.info(
            "Record at least two audit runs before comparing them. "
            "You can record another run using the sidebar."
        )
    else:
        # Newest and oldest runs remain linked to their full IDs.
        saved_runs = list(reversed(saved_runs))

        def comparison_timestamp(timestamp):
            return (
                pd.to_datetime(timestamp, utc=True)
                .tz_convert("Asia/Kolkata")
                .strftime("%d %b %Y, %I:%M:%S %p IST")
            )

        def comparison_label(run):
            return (
                f"RUN-{run['run_id'][:8].upper()} · "
                f"{comparison_timestamp(run['run_time_utc'])} · "
                f"{run.get('source_name', 'Unknown source')}"
            )

        run_options = {
            run["run_id"]: run
            for run in saved_runs
        }

        run_ids = list(run_options.keys())

        older_run_id = st.selectbox(
            "Older audit run",
            run_ids,
            index=0,
            format_func=lambda run_id: comparison_label(
                run_options[run_id]
            ),
            key="comparison_older_run",
        )

        newer_run_id = st.selectbox(
            "Newer audit run",
            run_ids,
            index=len(run_ids) - 1,
            format_func=lambda run_id: comparison_label(
                run_options[run_id]
            ),
            key="comparison_newer_run",
        )

        if older_run_id == newer_run_id:
            st.warning("Select two different audit runs.")
        else:
            older_run = run_options[older_run_id]
            newer_run = run_options[newer_run_id]

            comparison = compare_audit_runs(
                older_run,
                newer_run,
            )

            resolved_count = int(
                (comparison["comparison_status"] == "Resolved").sum()
            ) if not comparison.empty else 0

            continuing_count = int(
                (comparison["comparison_status"] == "Continuing").sum()
            ) if not comparison.empty else 0

            new_count = int(
                (comparison["comparison_status"] == "New").sum()
            ) if not comparison.empty else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Resolved", resolved_count)
            col2.metric("Continuing", continuing_count)
            col3.metric("New", new_count)

            st.caption(
                "Matching uses employee ID and control rule ID. "
                "A finding absent from a later run is classified as "
                "resolved by the comparison logic; confirm the underlying "
                "evidence before treating it as genuinely remediated."
            )

            if comparison.empty:
                st.success("Neither run contains findings.")
            else:
                st.dataframe(
                    comparison,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "Export comparison (CSV)",
                    data=comparison.to_csv(index=False).encode("utf-8"),
                    file_name="AccessGuard_Run_Comparison.csv",
                    mime="text/csv",
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AccessGuard · Technology Risk & Assurance · "
    "Rule-based access review prototype"
)