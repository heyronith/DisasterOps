# DisasterOps: Multi-Agent Disaster Response Assistant

A portfolio-ready multi-agent system for disaster response planning using verified RAG (Retrieval-Augmented Generation). The system transforms incident reports into structured operational outputs, including ICS forms, action plans, and communications.

## 🎯 Overview

DisasterOps is a complete 7-step project that implements:

1. **Knowledge Corpus Collection & Processing** - Curated, citation-ready knowledge base
2. **RAG Pipeline** - Hybrid retrieval (dense + sparse search) with citation mapping
3. **Agent Orchestration** - 5-agent workflow (Intake, Retriever, Planner, Comms, Verifier)
4. **Verification Layer** - Grounding, safety checks, and uncertainty handling
5. **Structured Output Generation** - ICS forms and operational artifacts
6. **Evaluation Harness** - Comprehensive metrics and benchmarks
7. **Demo Interface** - Streamlit web UI for portfolio demonstration

## 🚀 Quick Start

### Option 1: Try the Live Demo (Recommended)

🌐 **Live Application:** [https://YOUR_APP_NAME.streamlit.app](https://YOUR_APP_NAME.streamlit.app)

*(Update this URL after deploying to Streamlit Cloud)*

### Option 2: Run Locally

**Prerequisites:**
- Python 3.9+
- OpenAI API key (for LLM functionality)

**Installation:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DisasterOps.git
   cd DisasterOps
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

**Launch the Streamlit app:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Running Demo Scenarios

**Run all showcase scenarios:**
```bash
python demo.py
```

This will process 3 demo scenarios and save outputs to `demo_outputs/`.

### Running Evaluation

**Run the evaluation harness:**
```bash
python evaluation.py
```

This runs comprehensive metrics on 20 test scenarios and generates reports in `evaluation_results/`.

## 📖 Usage

### Web Interface

1. **Enter Incident Details**: Type or paste a description of the incident
2. **Optional**: Load a demo scenario from the sidebar
3. **Process**: Click "Process Incident" to run the 5-agent pipeline
4. **Review**: Explore generated artifacts, ICS forms, and citations
5. **Export**: Download results in JSON, Markdown, or PDF format

### Programmatic Usage

```python
from agents import run_pipeline
from output_generation import generate_from_agent_output

# Run pipeline
result = run_pipeline("Wildfire approaching residential area...")

# Generate structured outputs
all_outputs = generate_from_agent_output(
    result,
    incident_name="Pine Valley Wildfire",
    incident_number="WV-2024-001"
)

# Export to JSON
from output_generation import export_to_json
from pathlib import Path

export_to_json(all_outputs, Path("output.json"))
```

## 📁 Project Structure

```
DisasterOps/
├── app.py                    # Streamlit demo interface
├── agents.py                 # 5-agent pipeline implementation
├── output_generation.py      # ICS forms and artifact generation
├── evaluation.py             # Evaluation harness and metrics
├── demo.py                   # Demo scenario runner
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── Data/
│   ├── raw/                  # Source PDF documents
│   ├── processed/            # Processed document metadata
│   ├── chunks/               # Text chunks and citation index
│   └── embeddings/           # Vector embeddings and BM25 model
├── outputs/                  # Generated outputs (created at runtime)
├── demo_outputs/             # Demo scenario outputs (created at runtime)
└── evaluation_results/       # Evaluation reports (created at runtime)
```

## 🔧 System Architecture

### Agents

1. **Intake Agent**: Extracts structured data from incident reports
2. **Retriever Agent**: Generates queries and retrieves evidence using hybrid search
3. **Planner Agent**: Generates operational objectives, tasks, and resource needs
4. **Comms Agent**: Drafts public-facing and internal communications
5. **Verifier Agent**: Validates claims, checks citations, enforces safety rules

### Outputs Generated

- **Situation Brief**: Comprehensive incident summary
- **Triage + Priorities**: Medical triage categorization
- **Mini-IAP**: Incident Action Plan with objectives and tasks
- **Resource Requests**: Structured resource needs
- **Communications Drafts**: Public advisories and internal briefings
- **ICS Forms**: ICS-201, ICS-202, ICS-205, ICS-206

### Export Formats

- **JSON**: Complete structured data
- **Markdown**: Human-readable formatted output
- **PDF**: Professional document export (requires `weasyprint`)

## 📊 Evaluation Metrics

The evaluation harness measures:

- **Retrieval**: Recall@5, MRR, Citation Coverage
- **Plan Quality**: Completeness, Safety, Grounding, Calibration
- **Agent Reliability**: Tool-call success rate, Contradiction rate, Unknown detection

## 🛠️ Development

### Running Tests

The system includes comprehensive evaluation scenarios. Run the evaluation harness:

```bash
python evaluation.py
```

### Adding New Scenarios

Add scenarios to `demo.py` or `evaluation.py`:

```python
DEMO_SCENARIOS.append({
    "name": "Your Scenario Name",
    "description": "Incident description...",
    "incident_name": "Incident Name",
    "incident_number": "XX-2024-XXX"
})
```

## 📝 Notes

- The knowledge base is pre-processed and stored in `Data/`
- RAG resources (embeddings, BM25) are loaded lazily on first use
- The system uses OpenAI GPT-4o for LLM functionality
- PDF export requires additional dependencies: `pip install markdown weasyprint`

## 🔒 Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

## 📄 License

This project is part of a portfolio demonstration.

## 🙏 Acknowledgments

- FEMA ICS forms and documentation
- Ready.gov disaster preparedness guides
- CERT training materials

---

## 🌐 Deployment

This app is deployed on **Streamlit Community Cloud**.

### Deploy Your Own Copy

1. Fork this repository
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select this repository
5. Set main file: `app.py`
6. Add secret: `OPENAI_API_KEY`
7. Deploy!

See `DEPLOYMENT.md` for detailed deployment instructions.

---

**Status**: Portfolio-ready demo ✅

**Live Demo**: [https://YOUR_APP_NAME.streamlit.app](https://YOUR_APP_NAME.streamlit.app)

For questions or issues, refer to `PROJECT_PLAN.md` for detailed project documentation.

