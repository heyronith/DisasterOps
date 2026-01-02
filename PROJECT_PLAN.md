# DisasterOps: 7-Step Build Plan

## Executive Summary
Multi-agent disaster response assistant with verified RAG + operational outputs (ICS forms, IAPs, comms drafts). No model training—pure orchestration of pre-trained LLMs with verification discipline.

---

## Step 1: Knowledge Corpus Collection & Processing
**Goal:** Build curated, citation-ready knowledge base

**Tasks:**
- Scrape/download: CERT manuals, FEMA ICS forms (201, 202, 205, 206), Ready.gov guides
- Clean & structure: Remove noise, preserve section headers, add metadata (source, section, page)
- Store: Raw + processed versions with stable citation IDs (e.g., `fema_ics201_section3_p12`)

**Deliverables:**
- 10–20 authoritative documents processed
- Citation schema defined
- Data pipeline scripted and reproducible

**Duration:** 3–4 days

---

## Step 2: RAG Pipeline (Embedding + Hybrid Retrieval)
**Goal:** Build retrieval system that returns high-quality, cited evidence

**Tasks:**
- Chunking: Hierarchical (section → subsection → paragraph), preserve context
- Embeddings: Generate dense embeddings (OpenAI text-embedding-3-large or BGE-large)
- Sparse search: Build BM25 index for keyword matching
- Hybrid retrieval: Combine dense + sparse, rerank with Cohere/cross-encoder
- Citation mapping: Every chunk links back to source doc/section/page

**Validation:**
- Test on 50 sample queries before proceeding
- Target: Recall@5 > 0.8 for known scenarios

**Duration:** 4–5 days

---

## Step 3: Agent Orchestration (Multi-Agent State Machine)
**Goal:** Build agent workflow that transforms incident → structured outputs

**Tasks:**
- Set up LangGraph (or custom state machine)
- Build 4 core agents:
  - **Intake Agent**: Normalize incident report → structured schema `{hazards, injuries, infrastructure, weather, responders, constraints}`
  - **Retriever Agent**: Generate targeted queries per subproblem, fetch evidence bundles
  - **Planner Agent**: Generate objectives, tasks, resource needs → structured JSON + natural language
  - **Comms Agent**: Draft public/internal messaging with clarity checks
- Wire agents: Define state transitions, error handling, retry logic

**Deliverables:**
- Working agent pipeline (can generate basic plans from incident input)
- State schema defined

**Duration:** 5–7 days

---

## Step 4: Verification Layer (Grounding + Safety)
**Goal:** Enforce claim-level citations and safety rules

**Tasks:**
- **Verifier Agent**: Gate between Planner → Final Output
  - Check: Every operational claim has ≥1 citation
  - Flag: Low confidence, contradictions, missing evidence
  - Escalation: If immediate danger detected → "Call 911" override
- **Multi-source validation**: For high-risk topics (medical, evacuation, hazmat), require 2+ independent sources or downgrade confidence
- **Uncertainty protocol**: System must output "known" (with citations), "unknown", and "safe next steps"

**Deliverables:**
- Verification rules engine
- Confidence scoring + uncertainty handling

**Duration:** 3–4 days

---

## Step 5: Structured Output Generation (ICS Forms + Artifacts)
**Goal:** Transform agent outputs into operational paperwork

**Tasks:**
- **Templates:**
  - Situation Brief (structured JSON + markdown)
  - Triage + Priorities (prioritized list with assumptions)
  - Mini-IAP (objectives, assignments, safety message)
  - Resource Requests (quantities, staging, alternates)
  - Comms Drafts (public advisory, volunteer coordination, internal notes)
- **ICS Form Generation**: Start with ICS-201 (Incident Briefing), expand to 202/205/206
- **Export formats**: JSON (API), markdown (human-readable), PDF (printable)

**Deliverables:**
- All output templates implemented
- ICS-201 form generator working

**Duration:** 3–4 days

---

## Step 6: Evaluation Harness (Metrics + Benchmarks)
**Goal:** Quantify system reliability and plan quality

**Tasks:**
- **Build scenario test set**: Start with 30 scenarios, expand to 200
  - Realistic incident descriptions
  - Ground-truth checklists (required steps, expected outputs)
- **Metrics:**
  - **Retrieval**: Recall@5, MRR (Mean Reciprocal Rank), citation coverage
  - **Plan quality**: Completeness (% required steps included), Safety (unsafe instruction detection), Grounding (% claims with valid citations), Calibration (confidence vs evidence quality)
  - **Agent reliability**: Tool-call success rate, contradiction rate, "unknown-when-unknown" behavior
- **Automated eval runner**: Run on every major change

**Deliverables:**
- Evaluation framework scripted
- Baseline metrics established

**Duration:** 4–5 days

---

## Step 7: Demo Interface (UI + Presentation)
**Goal:** Ship portfolio-ready demo

**Tasks:**
- **Web UI**: Streamlit (fast) or FastAPI + React (more polished)
- **Input**: Incident description (text box, optional structured fields)
- **Output**: 
  - Expandable sections for each artifact (Brief, Triage, IAP, etc.)
  - Clickable citations (show source text)
  - Confidence indicators, "unknowns" section
  - Export options (JSON, PDF)
- **Demo script**: Prepare 2–3 showcase scenarios

**Deliverables:**
- Working demo deployed (local or cloud)
- README with setup instructions

**Duration:** 2–3 days

---

## Timeline Summary

| Step | Duration | Cumulative |
|------|----------|------------|
| 1. Corpus | 3–4 days | Week 1 |
| 2. RAG | 4–5 days | Week 1–2 |
| 3. Agents | 5–7 days | Week 2–3 |
| 4. Verification | 3–4 days | Week 3 |
| 5. Outputs | 3–4 days | Week 3–4 |
| 6. Eval | 4–5 days | Week 4–5 |
| 7. Demo | 2–3 days | Week 5 |

**Total: ~4–5 weeks** (solo, focused work)

---

## Success Criteria

✅ Retrieval: Recall@5 > 0.8  
✅ Plan completeness: >85% required steps included  
✅ Grounding: >90% claims have valid citations  
✅ Safety: Zero unsafe instructions in eval set  
✅ Demo: Can handle 5+ incident types with structured outputs  

---

## Tech Stack (Recommended)

- **Orchestration:** LangGraph
- **LLM:** OpenAI GPT-4o / Anthropic Claude (or open-source via LiteLLM)
- **Embeddings:** OpenAI text-embedding-3-large (or BGE-large)
- **Vector DB:** Chroma / Qdrant (local) or Pinecone (cloud)
- **Sparse Search:** rank-bm25
- **Reranker:** Cohere rerank-v3 (or cross-encoder)
- **Evaluation:** LlamaIndex evals or custom harness
- **UI:** Streamlit (MVP) or FastAPI + React (production)

---

## Notes

- Start with **one incident type** (e.g., floods) for MVP, expand later
- **Verification is non-negotiable**—don't skip Step 4
- **Evaluation drives iteration**—run evals frequently
- Focus on **operational artifacts** (ICS forms) as differentiator

