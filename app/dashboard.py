"""Risk & Advanced Modelling — stakeholder dashboard.

A single Streamlit app surfacing the risk-scored outputs of all four modules
(pharmacovigilance signals, recall risk, clinical trial risk, sanctions
screening). It reads the *processed* outputs written by each notebook under
`data/processed/<module>/` and the model metadata under `models/`, and renders
the corresponding stakeholder summary from `reports/`.

Run from the project root:

    streamlit run app/dashboard.py

If `data/processed/<module>/` is empty, run the corresponding notebook first
(`notebooks/0X_*.ipynb`) to generate it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"

RISK_BAND_ORDER = ["Low", "Medium", "High", "Critical"]
RISK_BAND_COLORS = {
    "Low": "#2ca02c",
    "Medium": "#ffbf00",
    "High": "#ff7f0e",
    "Critical": "#d62728",
}


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


@st.cache_data
def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_report(name: str) -> str | None:
    path = REPORTS / name
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def missing_data_notice(module_dir: str, notebook: str) -> None:
    st.warning(
        f"No processed data found in `data/processed/{module_dir}/`. "
        f"Run `notebooks/{notebook}` once to generate it."
    )


def risk_band_chart(df: pd.DataFrame, title: str):
    counts = (
        df["risk_band"]
        .value_counts()
        .reindex(RISK_BAND_ORDER)
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    counts.columns = ["risk_band", "count"]
    fig = px.bar(
        counts, x="risk_band", y="count", color="risk_band",
        category_orders={"risk_band": RISK_BAND_ORDER},
        color_discrete_map=RISK_BAND_COLORS, title=title,
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
    return fig


def render_model_card(meta_filename: str, label: str) -> None:
    meta = load_json(MODELS / meta_filename)
    if meta is None:
        return
    with st.expander(f"Model details: {label}"):
        st.write(f"**Model**: {meta.get('model')}")
        st.write(f"**Purpose**: {meta.get('purpose')}")
        st.write(f"**Trained**: {meta.get('trained_at')}")
        if "cv_roc_auc" in meta:
            st.write(f"**Cross-validated ROC-AUC**: {meta['cv_roc_auc']:.3f}")
        if "training_rows" in meta:
            st.write(f"**Training rows**: {meta['training_rows']:,}")
        if "class_balance" in meta:
            st.write(f"**Class balance**: {meta['class_balance']}")
        if "anomaly_rate" in meta:
            st.write(f"**Anomaly rate**: {meta['anomaly_rate']:.1%} "
                     f"(contamination={meta.get('contamination')})")
        if meta.get("caveats"):
            st.markdown("**Caveats**")
            for c in meta["caveats"]:
                st.markdown(f"- {c}")


# ---------------------------------------------------------------------------
# Page: Pharmacovigilance signal detection (Module 1)
# ---------------------------------------------------------------------------
def page_faers():
    st.title("Pharmacovigilance Signal Detection — FAERS")
    st.caption("Disproportionality signals + case-level anomaly triage for adverse event reports")

    signals = load_csv(PROCESSED / "faers" / "signal_watchlist.csv")
    cases = load_csv(PROCESSED / "faers" / "case_anomalies.csv")
    meta = load_json(PROCESSED / "faers" / "processed.meta.json")

    if signals is None or cases is None:
        missing_data_notice("faers", "01_faers_signal_detection.ipynb")
        return

    drug = meta.get("drug", "Unknown drug") if meta else "Unknown drug"
    st.subheader(f"Drug: {drug}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Reaction terms screened", len(signals))
    col2.metric("Meeting signal threshold", int(signals["meets_signal_threshold"].sum()))
    col3.metric("Case-level anomalies flagged", int(cases["anomaly_flag"].sum()))

    st.plotly_chart(risk_band_chart(signals, "Signal risk bands"), use_container_width=True)

    st.subheader("Signal watchlist")
    band_filter = st.multiselect("Filter by risk band", RISK_BAND_ORDER, default=RISK_BAND_ORDER, key="faers_band")
    filtered = signals[signals["risk_band"].isin(band_filter)].sort_values("risk_score", ascending=False)
    st.dataframe(
        filtered[["event", "a", "prr", "prr_ci_low", "prr_ci_high", "chi_square",
                  "meets_signal_threshold", "risk_score", "risk_band"]],
        use_container_width=True, hide_index=True,
    )

    fig = px.bar(
        filtered.sort_values("prr", ascending=True).tail(15),
        x="prr", y="event", orientation="h", color="risk_band",
        category_orders={"risk_band": RISK_BAND_ORDER}, color_discrete_map=RISK_BAND_COLORS,
        title="Proportional Reporting Ratio (PRR) by reaction term",
        labels={"prr": "PRR", "event": "Reaction term"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Case-level anomaly scores")
    fig2 = px.histogram(
        cases, x="anomaly_score", color="anomaly_flag", nbins=40,
        title="Distribution of Isolation Forest anomaly scores",
        labels={"anomaly_score": "Anomaly score (higher = more unusual)", "anomaly_flag": "Flagged"},
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        cases[cases["anomaly_flag"]].sort_values("anomaly_score", ascending=False)
        [["safetyreportid", "receivedate", "serious", "patientonsetage_imputed", "n_reactions", "n_drugs", "anomaly_score"]]
        .head(20),
        use_container_width=True, hide_index=True,
    )

    render_model_card("faers_case_anomaly_iforest.meta.json", "FAERS case anomaly (Isolation Forest)")

    report = load_report("faers_summary.md")
    if report:
        with st.expander("Stakeholder summary (reports/faers_summary.md)"):
            st.markdown(report)


# ---------------------------------------------------------------------------
# Page: Recall / manufacturing quality risk (Module 2)
# ---------------------------------------------------------------------------
def page_enforcement():
    st.title("Recall / Manufacturing Quality Risk — openFDA Enforcement")
    st.caption("Firm-level recall risk, blending frequency, severity (model-based), and recency")

    firms = load_csv(PROCESSED / "enforcement" / "firm_watchlist.csv")
    volume = load_csv(PROCESSED / "enforcement" / "recall_volume.csv")

    if firms is None:
        missing_data_notice("enforcement", "02_enforcement_recall_risk.ipynb")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Firms tracked", len(firms))
    col2.metric("Critical risk firms", int((firms["risk_band"] == "Critical").sum()))
    col3.metric("High risk firms", int((firms["risk_band"] == "High").sum()))

    st.plotly_chart(risk_band_chart(firms, "Firm risk bands"), use_container_width=True)

    st.subheader("Firm watchlist")
    band_filter = st.multiselect("Filter by risk band", RISK_BAND_ORDER, default=["Critical", "High"], key="enf_band")
    filtered = firms[firms["risk_band"].isin(band_filter)].sort_values("risk_score", ascending=False)
    st.dataframe(
        filtered[["recalling_firm", "n_recalls", "classI_rate", "severity_risk", "risk_score", "risk_band"]],
        use_container_width=True, hide_index=True,
    )

    fig = px.scatter(
        firms, x="n_recalls", y="severity_risk", color="risk_band", size="risk_score",
        category_orders={"risk_band": RISK_BAND_ORDER}, color_discrete_map=RISK_BAND_COLORS,
        hover_name="recalling_firm",
        title="Recall frequency vs. model-predicted severity",
        labels={"n_recalls": "Number of recalls", "severity_risk": "Mean predicted P(Class I)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    if volume is not None:
        st.subheader("Recall volume over time")
        volume["report_date"] = pd.to_datetime(volume["report_date"])
        fig2 = px.bar(
            volume, x="report_date", y="count", color="is_anomaly",
            title="Monthly recall volume (flagged months in a different colour)",
            labels={"report_date": "Month", "count": "Recalls", "is_anomaly": "Anomalous"},
        )
        st.plotly_chart(fig2, use_container_width=True)

    render_model_card("recall_severity_classifier.meta.json", "Recall severity classifier")

    report = load_report("enforcement_summary.md")
    if report:
        with st.expander("Stakeholder summary (reports/enforcement_summary.md)"):
            st.markdown(report)


# ---------------------------------------------------------------------------
# Page: Clinical trial risk & scenario modelling (Module 3)
# ---------------------------------------------------------------------------
def page_clinicaltrials():
    st.title("Clinical Trial Risk & Scenario Modelling — ClinicalTrials.gov")
    st.caption("Per-trial termination risk (model-based) + Monte Carlo enrollment scenario")

    trials = load_csv(PROCESSED / "clinicaltrials" / "trial_watchlist.csv")
    sim = load_json(PROCESSED / "clinicaltrials" / "enrollment_simulation.json")
    meta = load_json(PROCESSED / "clinicaltrials" / "processed.meta.json")

    if trials is None:
        missing_data_notice("clinicaltrials", "03_clinicaltrials_risk.ipynb")
        return

    area = meta.get("therapeutic_area", "Unknown") if meta else "Unknown"
    n_conditions = len(meta.get("conditions_combined", [])) if meta else 0
    st.subheader(f"Therapeutic area: {area} ({n_conditions} related conditions combined)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Trials reviewed", len(trials))
    col2.metric("Terminated/withdrawn/suspended",
                int(trials["overall_status"].isin(["TERMINATED", "WITHDRAWN", "SUSPENDED"]).sum()))
    col3.metric("Unknown status", int(trials["reporting_risk"].sum()))

    st.plotly_chart(risk_band_chart(trials, "Trial risk bands"), use_container_width=True)

    st.subheader("Trial watchlist")
    status_options = sorted(trials["overall_status"].unique().tolist())
    band_filter = st.multiselect("Filter by risk band", RISK_BAND_ORDER, default=["Critical", "High", "Medium"], key="ct_band")
    filtered = trials[trials["risk_band"].isin(band_filter)].sort_values("risk_score", ascending=False)
    st.dataframe(
        filtered[["nct_id", "brief_title", "overall_status", "why_stopped", "enrollment_count",
                  "termination_risk_model", "risk_score", "risk_band"]],
        use_container_width=True, hide_index=True,
    )

    fig = px.histogram(
        trials, x="termination_risk_model", color="overall_status", nbins=30,
        title="Distribution of model-predicted termination risk by current status",
        labels={"termination_risk_model": "P(terminated/withdrawn/suspended)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    if sim:
        st.subheader("Enrollment scenario for the largest recruiting trial")
        st.write(f"**{sim['target_trial_nct_id']}** — {sim['target_trial_title']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Target enrollment", f"{sim['target_enrollment']:,}")
        c2.metric("Benchmark rate (per month)", f"{sim['benchmark_monthly_rate_mean']:.1f}")
        if sim.get("median_months_to_complete") is not None:
            c3.metric("Median months to complete", f"{sim['median_months_to_complete']:.0f}")
            st.write(
                f"80% confidence range: **{sim['p10_months']:.0f}-{sim['p90_months']:.0f} months**. "
                f"P(complete within 24 months): **{sim.get('p_complete_by_target', 0.0):.0%}**."
            )
        else:
            c3.metric("Median months to complete", "> 60 (horizon)")
            st.write(
                f"0% of {sim['n_simulations']:,} simulations completed enrollment within the "
                f"60-month horizon at this benchmark rate — target enrollment is large relative "
                f"to the typical recruitment pace in this therapeutic area."
            )

    render_model_card("clinical_trial_termination_classifier.meta.json", "Trial termination-risk classifier")

    report = load_report("clinicaltrials_summary.md")
    if report:
        with st.expander("Stakeholder summary (reports/clinicaltrials_summary.md)"):
            st.markdown(report)


# ---------------------------------------------------------------------------
# Page: Sanctions / compliance entity screening (Module 4)
# ---------------------------------------------------------------------------
def page_ofac():
    st.title("Sanctions / Compliance Entity Screening — OFAC SDN")
    st.caption("Fuzzy name matching against the US Treasury SDN list, risk-banded for analyst triage")

    screened = load_csv(PROCESSED / "ofac" / "screening_results.csv")
    meta = load_json(PROCESSED / "ofac" / "processed.meta.json")

    if screened is None:
        missing_data_notice("ofac", "04_ofac_screening.ipynb")
        return

    n_sdn = meta.get("sdn_entity_names_screened_against", 0) if meta else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Candidates screened", len(screened))
    col2.metric("SDN entity names", f"{n_sdn:,}")
    col3.metric("Matches requiring review", int(screened["matched_name"].notna().sum()))

    st.plotly_chart(risk_band_chart(screened, "Screening risk bands"), use_container_width=True)

    st.subheader("Screening results")
    st.dataframe(
        screened.sort_values("risk_score", ascending=False),
        use_container_width=True, hide_index=True,
    )

    report = load_report("ofac_summary.md")
    if report:
        with st.expander("Stakeholder summary (reports/ofac_summary.md)"):
            st.markdown(report)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Risk & Advanced Modelling Dashboard", layout="wide")

    st.sidebar.title("Risk & Advanced Modelling")
    st.sidebar.caption(
        "Practice project simulating a Data Scientist — Risk & Advanced Modelling role "
        "in regulated/life-sciences environments. All data is real, pulled live from "
        "public regulatory sources; see CLAUDE.md and reports/ for caveats."
    )
    page = st.sidebar.radio(
        "Module",
        [
            "1. Pharmacovigilance signals (FAERS)",
            "2. Recall / manufacturing risk (Enforcement)",
            "3. Clinical trial risk & scenarios (ClinicalTrials.gov)",
            "4. Sanctions screening (OFAC SDN)",
        ],
    )

    if page.startswith("1."):
        page_faers()
    elif page.startswith("2."):
        page_enforcement()
    elif page.startswith("3."):
        page_clinicaltrials()
    else:
        page_ofac()

    st.sidebar.divider()
    st.sidebar.caption(
        "Risk scores are decision-support aids for analyst triage, not automated "
        "determinations. See each module's stakeholder summary for caveats and "
        "recommended next steps."
    )


if __name__ == "__main__":
    main()
