"""
AI Tool for Automated Hazard Identification and Risk Assessment on Construction Sites
University of Bolton / Regent College London - BSc (Hons) Computer Science Project
Author: Serghei Coceban
"""

import streamlit as st
from PIL import Image
import io
from pathlib import Path
from datetime import datetime

# Resilient pandas import for numpy 1.x / 2.x ABI compatibility
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except Exception:
    PANDAS_AVAILABLE = False

# Local core modules
from config import (
    DEFAULT_MODEL_PATH,
    DEFAULT_CONFIDENCE,
    DEFAULT_IOU_THRESHOLD,
    WEIGHTS_DIR
)
from core.detector import HazardDetector, ULTRALYTICS_AVAILABLE
from core.risk_engine import RiskAssessmentEngine
from core.visualizer import annotate_image, generate_risk_matrix_plot
from core.report_generator import generate_pdf_report, generate_html_report, REPORTLAB_AVAILABLE

# Page layout and metadata
st.set_page_config(
    page_title="AI Construction Hazard & Risk Assessment",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .kpi-title {
        font-size: 11px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .kpi-val {
        font-size: 22px;
        font-weight: 700;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_detector(weights_path: str):
    """Initializes and caches the detector instance."""
    return HazardDetector(model_path=Path(weights_path))


def main():
    # Header Banner
    st.markdown('<div class="main-header">🏗️ Construction Safety AI: Hazard Detection & 5×5 Risk Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">BSc (Hons) Computer Science Final Year Project &bull; Serghei Coceban &bull; University of Bolton & Regent College London</div>', unsafe_allow_html=True)

    # Initialize Backend Engines
    detector = get_detector(str(DEFAULT_MODEL_PATH))
    risk_engine = RiskAssessmentEngine()

    # Sidebar: Model and Configuration Controls
    with st.sidebar:
        st.header("⚙️ System Configuration")

        # Check weights file
        weights_exist = DEFAULT_MODEL_PATH.exists()
        st.subheader("Model Status")
        if weights_exist and detector.is_custom_model:
            st.success(f"✅ Active Trained Model: `{DEFAULT_MODEL_PATH.name}`")
            with st.expander(f"Detected Model Classes ({len(detector.class_names)})", expanded=False):
                for idx, cls_name in enumerate(detector.class_names):
                    badge = "🔴 Hazard" if "no_" in cls_name else ("🚜 Machinery" if cls_name == "forklift" else "🟢 Compliant")
                    st.markdown(f"- **{cls_name}** `[{badge}]`")
        elif not ULTRALYTICS_AVAILABLE:
            st.warning("⚠️ `ultralytics` not installed. Running in Demo Simulation Mode.")
        else:
            st.info("ℹ️ Running in **Demo / Simulation Mode**")
            st.caption(f"To deploy your model, place `best.pt` in:\n`{WEIGHTS_DIR}/`")

        # Custom Model File Uploader
        with st.expander("📦 Upload Custom Weights (.pt)"):
            uploaded_weights = st.file_uploader("Upload .pt weights file", type=["pt"])
            if uploaded_weights:
                target_path = WEIGHTS_DIR / uploaded_weights.name
                WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
                with open(target_path, "wb") as f:
                    f.write(uploaded_weights.getbuffer())
                st.success(f"Saved `{target_path.name}`! Please reload app.")

        st.divider()

        # Inference Parameters
        st.subheader("Inference Settings")
        conf_threshold = st.slider("Confidence Threshold", 0.10, 0.95, float(DEFAULT_CONFIDENCE), 0.05)
        iou_threshold = st.slider("IoU NMS Threshold", 0.10, 0.90, float(DEFAULT_IOU_THRESHOLD), 0.05)
        show_compliant = st.checkbox("Show Compliant PPE in annotations", value=True)

        st.divider()

        # Inspection Audit Details
        st.subheader("Audit Metadata")
        site_name = st.text_input("Site / Project Name", "Bolton Central Construction Phase 2")
        inspector_name = st.text_input("Safety Officer / Inspector", "S. Coceban (Safety Lead)")
        inspection_date = st.date_input("Audit Date", datetime.now())

        st.caption("Framework: OSHA 29 CFR 1926 / 5×5 Risk Matrix")

    # Image Upload Section
    st.subheader("📸 Site Photography Inspection")
    uploaded_files = st.file_uploader(
        "Upload one or more construction site photos (JPG, PNG):",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    # Quick Demo Sample Button if no files uploaded
    col_demo, _ = st.columns([2, 5])
    with col_demo:
        use_sample = st.checkbox("Or test with included sample image", value=(len(uploaded_files) == 0))

    images_to_process = []
    if uploaded_files:
        for uf in uploaded_files:
            try:
                img = Image.open(uf).convert("RGB")
                images_to_process.append((uf.name, img))
            except Exception as e:
                st.error(f"Error opening image {uf.name}: {e}")
    elif use_sample:
        sample_path = Path(__file__).resolve().parent / "samples" / "sample_site.jpg"
        if sample_path.exists():
            images_to_process.append(("sample_site.jpg", Image.open(sample_path).convert("RGB")))
        else:
            sample_img = Image.new("RGB", (900, 600), color=(185, 200, 215))
            images_to_process.append(("sample_site_photo.jpg", sample_img))

    if not images_to_process:
        st.info("👆 Please upload construction site photos or select the sample option above to begin inspection.")
        return

    # Process all uploaded images
    all_detections = []
    processed_results = []

    with st.spinner("Analyzing site imagery with YOLOv8 & evaluating 5×5 risk matrix..."):
        for filename, pil_img in images_to_process:
            dets = detector.detect(pil_img, conf_threshold=conf_threshold, iou_threshold=iou_threshold)
            img_eval = risk_engine.assess_batch(dets)
            items_to_draw = img_eval["all_items"] if show_compliant else img_eval["hazards"]
            annotated_img = annotate_image(pil_img, items_to_draw)
            
            processed_results.append({
                "filename": filename,
                "original": pil_img,
                "annotated": annotated_img,
                "eval": img_eval
            })
            all_detections.extend(dets)

    # Batch Aggregation across all images
    site_assessment = risk_engine.assess_batch(all_detections)

    # Top KPI Metrics Dashboard
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Overall Status</div>
            <div class="kpi-val" style="color: {site_assessment['overall_color']};">{site_assessment['overall_site_risk']}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Hazards / Violations</div>
            <div class="kpi-val" style="color: {'#dc3545' if site_assessment['total_hazards'] > 0 else '#28a745'};">{site_assessment['total_hazards']}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Compliant PPE</div>
            <div class="kpi-val" style="color: #28a745;">{site_assessment.get('compliant_count', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Compliance Rate</div>
            <div class="kpi-val" style="color: {'#28a745' if site_assessment.get('compliance_rate', 0) >= 80 else '#fd7e14'};">{site_assessment.get('compliance_rate', 0)}%</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Critical (15-25)</div>
            <div class="kpi-val" style="color: #dc3545;">{site_assessment['tier_counts'].get('Critical', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">High (10-14)</div>
            <div class="kpi-val" style="color: #fd7e14;">{site_assessment['tier_counts'].get('High', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Interactive Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🖼️ Visual Detection",
        "📊 5×5 Risk Matrix",
        "📋 Hazard & Compliance Register",
        "📄 Safety Audit Report & PDF"
    ])

    # TAB 1: Visual Hazard Inspection
    with tab1:
        st.subheader("Visual Inspection & Bounding Box Annotations")
        for res in processed_results:
            st.markdown(f"**Image:** `{res['filename']}` — Detected Hazards: **{res['eval']['total_hazards']}** | Compliant PPE: **{res['eval']['compliant_count']}**")
            col_orig, col_annot = st.columns(2)
            with col_orig:
                st.image(res["original"], caption="Original Site Photo", use_container_width=True)
            with col_annot:
                st.image(res["annotated"], caption="YOLOv8 Detection (Green = Compliant, Red/Orange = Hazard)", use_container_width=True)
            st.divider()

    # TAB 2: 5x5 Risk Assessment Matrix
    with tab2:
        st.subheader("5×5 Construction Risk Matrix Distribution")
        col_mat, col_info = st.columns([3, 2])
        with col_mat:
            matrix_fig = generate_risk_matrix_plot(site_assessment["matrix_counts"])
            st.pyplot(matrix_fig)

        with col_info:
            st.markdown("### Risk Evaluation Rubric")
            st.markdown("""
            Risk Score = **Likelihood (1–5) × Severity (1–5)**:
            - 🔴 **Critical (15 – 25):** Immediate Work Stoppage. Major hazard likely to result in fatal or permanent injury.
            - 🟠 **High (10 – 14):** Urgent Rectification within 1 hour. Significant regulatory non-compliance.
            - 🟡 **Medium (5 – 9):** Remedial Action required within current shift.
            - 🟢 **Low (1 – 4):** Routine monitoring & toolbox talks.
            """)
            st.info(f"**Audit Finding:** {site_assessment['summary_statement']}")

    # TAB 3: Hazard Action Register Table
    with tab3:
        st.subheader("Identified Hazard & Compliance Register")
        
        filter_opt = st.radio("Display Filter:", ["Hazards Only (Violations)", "All Detections (Including Compliant PPE)"], horizontal=True)
        items_to_show = site_assessment["hazards"] if filter_opt.startswith("Hazards") else site_assessment["all_items"]

        if not items_to_show:
            st.success("No items match the selected filter.")
        else:
            table_rows = []
            for h in items_to_show:
                table_rows.append({
                    "Status": "⚠ VIOLATION" if h.get("is_hazard") else "✔ COMPLIANT",
                    "Finding / Item": h["title"],
                    "Confidence": f"{int(h['confidence']*100)}%",
                    "Likelihood": f"{h['likelihood']} ({h['likelihood_label']})",
                    "Severity": f"{h['severity']} ({h['severity_label'].split(' ')[0]})",
                    "Risk Score": h["risk_score"],
                    "Risk Tier": h["risk_tier"],
                    "Standard": h["standard_ref"],
                    "Action Required": h["recommendation"]
                })

            if PANDAS_AVAILABLE:
                df = pd.DataFrame(table_rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.table(table_rows)

    # TAB 4: Safety Audit Report & Download
    with tab4:
        st.subheader("Downloadable Safety Recommendation Report")
        st.write("Generate and download formal safety audit reports for site management and safety audits.")

        # HTML Report Generation
        html_report = generate_html_report(site_assessment, project_name=site_name)

        col_rep1, col_rep2 = st.columns(2)
        with col_rep1:
            st.download_button(
                label="📥 Download HTML Safety Audit Report",
                data=html_report,
                file_name=f"Safety_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html",
                use_container_width=True
            )

        with col_rep2:
            if REPORTLAB_AVAILABLE:
                try:
                    pdf_bytes = generate_pdf_report(site_assessment, project_name=site_name)
                    st.download_button(
                        label="📄 Download Official PDF Audit Report",
                        data=pdf_bytes,
                        file_name=f"Safety_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error compiling PDF: {e}")
            else:
                st.button("📄 PDF Export (Install `reportlab` to enable direct PDF)", disabled=True, use_container_width=True)

        st.divider()
        st.markdown("### Report Preview")
        st.components.v1.html(html_report, height=600, scrolling=True)


if __name__ == "__main__":
    main()
