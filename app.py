"""
DisasterOps Demo Interface
Step 7: Portfolio-Ready Web UI

Streamlit application for the DisasterOps multi-agent disaster response system.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

import streamlit as st
from datetime import datetime

from agents import run_pipeline
from output_generation import generate_from_agent_output, export_to_json, export_to_markdown, export_to_pdf


# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(__file__).parent
CITATION_INDEX_PATH = BASE_DIR / "Data" / "metadata" / "citation_index.json"
CHUNKS_DIR = BASE_DIR / "Data" / "chunks"


# ============================================================================
# Demo Scenarios
# ============================================================================

DEMO_SCENARIOS = [
    {
        "name": "Wildfire Evacuation",
        "description": "Wildfire approaching residential area. 200 homes at risk. Winds 25mph, dry conditions. 5 firefighters on scene. Need evacuation plan and resource requests.",
        "incident_name": "Pine Valley Wildfire",
        "incident_number": "WV-2024-001"
    },
    {
        "name": "Flash Flood Response",
        "description": "Flash flooding in downtown area. Multiple vehicles stranded. 12 people rescued from vehicles. 3 reported injuries. Roads impassable. Water receding but more rain expected.",
        "incident_name": "Downtown Flash Flood",
        "incident_number": "FF-2024-002"
    },
    {
        "name": "Earthquake Triage",
        "description": "5.8 magnitude earthquake. Multiple buildings damaged. 50+ people need medical attention. Power out in 3 blocks. Communications disrupted. CERT teams mobilizing.",
        "incident_name": "Central District Earthquake",
        "incident_number": "EQ-2024-003"
    }
]


# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_data
def load_citation_index():
    """Load citation index for displaying source information."""
    try:
        with open(CITATION_INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Could not load citation index: {e}")
        return {}


def get_citation_info(citation_id: str, citation_index: Dict[str, Any]) -> Dict[str, Any]:
    """Get citation metadata from citation ID."""
    if citation_id in citation_index:
        info = citation_index[citation_id]
        return {
            "source_file": info.get("source_file", "Unknown"),
            "section_title": info.get("section_title", "Unknown"),
            "start_page": info.get("start_page", "Unknown"),
            "content_preview": info.get("content_preview", "")[:200]
        }
    return {
        "source_file": "Unknown",
        "section_title": "Unknown",
        "start_page": "Unknown",
        "content_preview": ""
    }


def format_confidence_score(score: float) -> tuple:
    """Format confidence score with color coding."""
    if score >= 0.8:
        return score, "🟢 High"
    elif score >= 0.6:
        return score, "🟡 Medium"
    else:
        return score, "🔴 Low"


# ============================================================================
# Main Application
# ============================================================================

def main():
    st.set_page_config(
        page_title="DisasterOps - Multi-Agent Disaster Response",
        page_icon="🚨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚨 DisasterOps")
    st.markdown("**Multi-Agent Disaster Response Assistant with Verified RAG**")
    st.markdown("---")
    
    # Initialize session state
    if "incident_report_text" not in st.session_state:
        st.session_state.incident_report_text = ""
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("Demo Scenarios")
        selected_scenario = st.selectbox(
            "Load a demo scenario:",
            ["None"] + [s["name"] for s in DEMO_SCENARIOS],
            index=0
        )
        
        # Load demo scenario button
        if selected_scenario != "None":
            scenario = next(s for s in DEMO_SCENARIOS if s["name"] == selected_scenario)
            if st.button(f"📥 Load '{selected_scenario}' Scenario", use_container_width=True):
                st.session_state.incident_report_text = scenario["description"]
                # Delete widget state keys so they can be reset
                if "incident_name" in st.session_state:
                    del st.session_state.incident_name
                if "incident_number" in st.session_state:
                    del st.session_state.incident_number
                # Set new values
                st.session_state.incident_name = scenario.get("incident_name", "")
                st.session_state.incident_number = scenario.get("incident_number", "001")
                st.rerun()
        
        st.markdown("---")
        
        st.subheader("Incident Details")
        incident_name_input = st.text_input(
            "Incident Name", 
            value=st.session_state.get("incident_name", ""), 
            key="incident_name"
        )
        incident_number_input = st.text_input(
            "Incident Number", 
            value=st.session_state.get("incident_number", "001"), 
            key="incident_number"
        )
        
        st.markdown("---")
        st.markdown("**Status:** Ready")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Incident Report")
        incident_report = st.text_area(
            "Describe the incident:",
            height=200,
            value=st.session_state.get("incident_report_text", ""),
            placeholder="Enter incident details, including hazards, injuries, infrastructure status, weather, available responders, and constraints...",
            key="incident_report"
        )
        # Update session state
        st.session_state.incident_report_text = incident_report
    
    with col2:
        st.subheader("📊 Quick Stats")
        if incident_report:
            word_count = len(incident_report.split())
            st.metric("Words", word_count)
            st.metric("Characters", len(incident_report))
        else:
            st.info("Enter incident report to see stats")
    
    # Process button
    process_btn = st.button("🚀 Process Incident", type="primary", use_container_width=True)
    
    # Process incident
    if process_btn and incident_report:
        with st.spinner("Processing incident through 5-agent pipeline..."):
            start_time = time.time()
            
            try:
                # Run pipeline
                result = run_pipeline(incident_report)
                processing_time = time.time() - start_time
                
                # Generate structured outputs
                incident_name_val = incident_name_input if incident_name_input else "Incident"
                incident_number_val = incident_number_input if incident_number_input else "001"
                all_outputs = generate_from_agent_output(result, incident_name_val, incident_number_val)
                
                # Store in session state
                st.session_state.pipeline_result = result
                st.session_state.all_outputs = all_outputs
                st.session_state.processing_time = processing_time
                
                st.success(f"✓ Processing complete in {processing_time:.2f}s")
                
            except Exception as e:
                st.error(f"❌ Error processing incident: {str(e)}")
                st.exception(e)
                return
    
    # Display results
    if "all_outputs" in st.session_state and "pipeline_result" in st.session_state:
        result = st.session_state.pipeline_result
        all_outputs = st.session_state.all_outputs
        processing_time = st.session_state.get("processing_time", 0)
        
        # Load citation index
        citation_index = load_citation_index()
        
        st.markdown("---")
        st.header("📊 Results Overview")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            verification = result.get("final_output", {}).get("verification", {})
            conf_score = verification.get("confidence_score", 0.5)
            conf_val, conf_label = format_confidence_score(conf_score)
            st.metric("Confidence", f"{conf_val:.2f}", conf_label)
        
        with col2:
            evidence_count = len(result.get("evidence", []))
            st.metric("Evidence Chunks", evidence_count)
        
        with col3:
            unique_citations = len(set(
                ev.get("citation_id", "") for ev in result.get("evidence", [])
            ))
            st.metric("Unique Citations", unique_citations)
        
        with col4:
            st.metric("Processing Time", f"{processing_time:.2f}s")
        
        # Verification status
        st.markdown("### ✅ Verification Status")
        verif_col1, verif_col2, verif_col3 = st.columns(3)
        
        with verif_col1:
            citation_coverage = verification.get("citation_coverage", "unknown")
            st.info(f"**Citation Coverage:** {citation_coverage}")
        
        with verif_col2:
            multi_source = verification.get("multi_source_status", "N/A")
            st.info(f"**Multi-Source Status:** {multi_source}")
        
        with verif_col3:
            flagged_issues = len(verification.get("flagged_issues", []))
            st.info(f"**Flagged Issues:** {flagged_issues}")
        
        # Unknown claims section
        unknown_claims = verification.get("unknown_claims", [])
        if unknown_claims:
            with st.expander("⚠️ Unknown Claims (Needs Human Review)", expanded=True):
                st.warning("The following claims could not be verified from the knowledge base:")
                for claim in unknown_claims:
                    st.markdown(f"- {claim}")
        
        # Safe next steps
        safe_steps = verification.get("safe_next_steps", [])
        if safe_steps:
            with st.expander("✅ Safe Next Steps", expanded=False):
                for step in safe_steps:
                    st.markdown(f"- {step}")
        
        st.markdown("---")
        
        # Artifacts section
        st.header("📋 Operational Artifacts")
        
        artifacts = all_outputs.get("artifacts", {})
        
        # Situation Brief
        with st.expander("📄 Situation Brief", expanded=True):
            brief = artifacts.get("situation_brief", {})
            st.json(brief)
        
        # Triage + Priorities
        with st.expander("🏥 Triage + Priorities"):
            triage = artifacts.get("triage_priorities", {})
            st.json(triage)
        
        # Mini-IAP
        with st.expander("📋 Mini-IAP (Incident Action Plan)"):
            iap = artifacts.get("mini_iap", {})
            st.json(iap)
        
        # Resource Requests
        with st.expander("🔧 Resource Requests"):
            resources = artifacts.get("resource_requests", {})
            st.json(resources)
        
        # Communications
        with st.expander("📢 Communications Drafts"):
            comms = artifacts.get("comms_drafts", {})
            
            st.subheader("Public Advisory")
            st.text_area(
                "Public Advisory Text",
                value=comms.get("public_advisory", ""),
                height=150,
                disabled=True,
                label_visibility="hidden"
            )
            
            st.subheader("Key Talking Points")
            talking_points = comms.get("key_talking_points", [])
            for i, point in enumerate(talking_points, 1):
                st.markdown(f"{i}. {point}")
            
            st.subheader("Internal Briefing")
            st.text_area(
                "Internal Briefing Text",
                value=comms.get("internal_briefing", ""),
                height=150,
                disabled=True,
                label_visibility="hidden"
            )
        
        st.markdown("---")
        
        # ICS Forms
        st.header("📑 ICS Forms")
        
        ics_forms = all_outputs.get("ics_forms", {})
        
        with st.expander("📋 ICS-201: Incident Briefing", expanded=False):
            ics201 = ics_forms.get("ics_201", {})
            st.json(ics201)
        
        with st.expander("📋 ICS-202: Incident Objectives", expanded=False):
            ics202 = ics_forms.get("ics_202", {})
            st.json(ics202)
        
        with st.expander("📋 ICS-205: Radio Communications Plan", expanded=False):
            ics205 = ics_forms.get("ics_205", {})
            st.json(ics205)
        
        with st.expander("📋 ICS-206: Medical Plan", expanded=False):
            ics206 = ics_forms.get("ics_206", {})
            st.json(ics206)
        
        st.markdown("---")
        
        # Evidence & Citations
        st.header("📚 Evidence & Citations")
        
        evidence = result.get("evidence", [])
        if evidence:
            st.markdown(f"**Total evidence chunks retrieved:** {len(evidence)}")
            
            for i, ev in enumerate(evidence[:10], 1):  # Show top 10
                citation_id = ev.get("citation_id", "unknown")
                text = ev.get("text", "")[:300] + "..." if len(ev.get("text", "")) > 300 else ev.get("text", "")
                score = ev.get("score", 0)
                
                citation_info = get_citation_info(citation_id, citation_index)
                
                with st.expander(f"**{i}. {citation_id}** (Score: {score:.3f})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**Evidence Text:**")
                        st.text(text)
                    
                    with col2:
                        st.markdown("**Citation Info:**")
                        st.markdown(f"- **Source:** `{citation_info['source_file']}`")
                        st.markdown(f"- **Section:** {citation_info['section_title']}")
                        st.markdown(f"- **Page:** {citation_info['start_page']}")
            
            if len(evidence) > 10:
                st.info(f"Showing top 10 of {len(evidence)} evidence chunks. Full list available in exports.")
        else:
            st.info("No evidence retrieved.")
        
        st.markdown("---")
        
        # Export section
        st.header("💾 Export Results")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if st.button("📄 Export JSON", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = BASE_DIR / "outputs" / f"incident_{timestamp}.json"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                export_to_json(all_outputs, output_path)
                st.success(f"✓ Exported to {output_path}")
                
                with open(output_path, 'r') as f:
                    st.download_button(
                        label="⬇️ Download JSON",
                        data=f.read(),
                        file_name=f"incident_{timestamp}.json",
                        mime="application/json"
                    )
        
        with export_col2:
            if st.button("📝 Export Markdown", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = BASE_DIR / "outputs" / f"incident_{timestamp}.md"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                export_to_markdown(all_outputs, output_path)
                st.success(f"✓ Exported to {output_path}")
                
                with open(output_path, 'r') as f:
                    st.download_button(
                        label="⬇️ Download Markdown",
                        data=f.read(),
                        file_name=f"incident_{timestamp}.md",
                        mime="text/markdown"
                    )
        
        with export_col3:
            if st.button("📑 Export PDF", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = BASE_DIR / "outputs" / f"incident_{timestamp}.pdf"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    export_to_pdf(all_outputs, output_path)
                    st.success(f"✓ Exported to {output_path}")
                    
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=f.read(),
                            file_name=f"incident_{timestamp}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"PDF export failed: {e}")
                    st.info("PDF export requires: pip install markdown weasyprint")
    
    else:
        # Initial state
        st.info("👈 Enter an incident report above and click 'Process Incident' to begin.")
        
        st.markdown("---")
        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. **Enter Incident Details**: Type or paste a description of the incident
        2. **Optional**: Load a demo scenario from the sidebar
        3. **Process**: Click the "Process Incident" button
        4. **Review**: Explore the generated artifacts, ICS forms, and citations
        5. **Export**: Download results in JSON, Markdown, or PDF format
        """)


if __name__ == "__main__":
    main()

