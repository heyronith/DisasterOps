"""
DisasterOps Agent Framework
Multi-Agent Triage + Verified RAG for Disaster Response

This module contains the 5-agent pipeline:
- Intake Agent: Normalizes incident reports into structured schema
- Retriever Agent: Retrieves evidence from knowledge base using hybrid search
- Planner Agent: Generates operational objectives, tasks, and resource needs
- Comms Agent: Generates public-facing and internal messaging
- Verifier Agent: Validates claims, checks citations, enforces safety rules
"""

import json
import os
import re
import pickle
from pathlib import Path
from typing import TypedDict, List, Dict, Any, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END


# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(__file__).parent
CHUNKS_DIR = BASE_DIR / "Data" / "chunks"
EMBEDDINGS_DIR = BASE_DIR / "Data" / "embeddings"


# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """State that flows through all agents"""
    # Input
    incident_report: str
    
    # Intermediate outputs
    structured_incident: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    plan: Dict[str, Any]
    comms: Dict[str, Any]
    
    # Final output
    final_output: Dict[str, Any]


# Global Resources (loaded on module import or lazily)


_rag_resources = None
_llm = None
_embedding_model = None


def get_llm():
    """Get or create the LLM client"""
    global _llm
    if _llm is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _llm


def get_embedding_model():
    """Get or create the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def load_rag_resources():
    """Load RAG system resources (chunks, embeddings, BM25 index)"""
    global _rag_resources
    
    if _rag_resources is not None:
        return _rag_resources
    
    print("Loading RAG system...")
    
    # Load chunks
    with open(CHUNKS_DIR / "all_chunks.json", 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Load embeddings
    embeddings = np.load(EMBEDDINGS_DIR / "embeddings.npy")
    
    # Load BM25 index
    with open(EMBEDDINGS_DIR / "bm25_model.pkl", 'rb') as f:
        bm25 = pickle.load(f)
    
    chunk_texts = [chunk["text"] for chunk in chunks]
    
    _rag_resources = {
        "chunks": chunks,
        "embeddings": embeddings,
        "bm25": bm25,
        "chunk_texts": chunk_texts
    }
    
    print(f"✓ Loaded {len(chunks)} chunks")
    print(f"✓ Loaded embeddings: {embeddings.shape}")
    print(f"✓ Loaded BM25 index")
    
    return _rag_resources


# ============================================================================
# Helper Functions
# ============================================================================

def parse_json_from_llm(response_content: str) -> Dict[str, Any]:
    """Extract JSON from LLM response (handles markdown code blocks)"""
    content = response_content.strip()
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If parsing fails, try to fix common issues
        try:
            # Remove trailing commas
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            return json.loads(content)
        except:
            return {"error": "Failed to parse JSON", "raw": response_content}


def normalize_to_list(value, default=None):
    """Normalize a value to always be a list"""
    if default is None:
        default = []
    if isinstance(value, list):
        return value
    elif value is None:
        return default
    elif isinstance(value, str) and value.lower() in ["none", "n/a", "na", ""]:
        return []
    else:
        return [value] if value else default


def hybrid_search(query: str, top_k: int = 10, dense_weight: float = 0.5) -> List[Tuple[int, float]]:
    """Hybrid search combining dense (embeddings) and sparse (BM25) retrieval"""
    rag = load_rag_resources()
    embedding_model = get_embedding_model()
    
    # Dense search
    query_embedding = embedding_model.encode([query])[0]
    dense_scores = np.dot(rag["embeddings"], query_embedding)
    dense_scores = (dense_scores - dense_scores.min()) / (dense_scores.max() - dense_scores.min() + 1e-8)
    
    # Sparse search (BM25)
    tokenized_query = query.lower().split()
    sparse_scores = rag["bm25"].get_scores(tokenized_query)
    sparse_scores = (sparse_scores - sparse_scores.min()) / (sparse_scores.max() - sparse_scores.min() + 1e-8)
    
    # Combine scores
    hybrid_scores = dense_weight * dense_scores + (1 - dense_weight) * sparse_scores
    
    # Get top k
    top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
    results = [(int(idx), float(hybrid_scores[idx])) for idx in top_indices]
    
    return results


# ============================================================================
# Agent Definitions
# ============================================================================

def intake_agent(state: AgentState) -> AgentState:
    """
    Intake Agent: Normalizes incident report into structured schema
    """
    llm = get_llm()
    incident = state["incident_report"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an emergency response intake specialist. 
        Extract key information from incident reports and structure it.
        Return ONLY valid JSON (no markdown, no explanations) with these fields:
        - hazards: list of hazards present (always a list, even if empty: [])
        - injuries: list of injuries (always a list - use [] if none, not "none" or null)
        - infrastructure_status: list of infrastructure impacts (always a list)
        - weather: current/expected weather conditions (string)
        - available_responders: list of available responder types (always a list)
        - constraints: list of constraints or limitations (always a list)
        
        IMPORTANT: All list fields must be arrays [], never strings or null.
        
        Example: {{"hazards": ["flood"], "injuries": [], "infrastructure_status": ["buildings affected"], "weather": "rain continuing", "available_responders": [], "constraints": []}}"""),
        ("user", "Incident report: {incident}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"incident": incident})
    structured = parse_json_from_llm(response.content)
    
    # Normalize all list fields to ensure they are always lists
    if "hazards" in structured:
        structured["hazards"] = normalize_to_list(structured["hazards"])
    if "injuries" in structured:
        structured["injuries"] = normalize_to_list(structured["injuries"])
    if "infrastructure_status" in structured:
        structured["infrastructure_status"] = normalize_to_list(structured["infrastructure_status"])
    if "available_responders" in structured:
        structured["available_responders"] = normalize_to_list(structured["available_responders"])
    if "constraints" in structured:
        structured["constraints"] = normalize_to_list(structured["constraints"])
    
    state["structured_incident"] = structured
    return state


def retriever_agent(state: AgentState) -> AgentState:
    """
    Retriever Agent: Generates queries and retrieves evidence from knowledge base
    """
    rag = load_rag_resources()
    structured = state["structured_incident"]
    
    # Generate queries based on incident data
    queries = []
    
    # Query for hazards
    hazards = normalize_to_list(structured.get("hazards"))
    if hazards:
        hazard_str = ", ".join(str(h) for h in hazards)
        queries.append(f"{hazard_str} response procedures emergency management")
    
    # Query for medical/triage if injuries
    injuries = normalize_to_list(structured.get("injuries"))
    if injuries and injuries != ["none"]:
        queries.append("medical triage treatment procedures emergency")
    else:
        queries.append("medical triage setup procedures no injuries")
    
    # Query for infrastructure
    infra = normalize_to_list(structured.get("infrastructure_status"))
    if infra:
        infra_str = ", ".join(str(i) for i in infra)
        queries.append(f"infrastructure damage assessment {infra_str}")
    
    # Query for evacuation if needed
    if hazards:
        queries.append("evacuation procedures safety protocols")
    
    # Query for resource planning
    queries.append("resource allocation emergency response planning")
    
    # Retrieve evidence for each query
    all_evidence = []
    seen_citations = set()
    
    for query in queries:
        results = hybrid_search(query, top_k=5)
        
        for idx, score in results:
            chunk = rag["chunks"][idx]
            citation = chunk["citation_id"]
            
            # Avoid duplicates (keep highest score)
            if citation not in seen_citations:
                seen_citations.add(citation)
                all_evidence.append({
                    "query": query,
                    "citation_id": citation,
                    "text": chunk["text"],
                    "score": score,
                    "word_count": chunk.get("word_count", 0)
                })
    
    # Sort by score and take top 15
    all_evidence.sort(key=lambda x: x["score"], reverse=True)
    state["evidence"] = all_evidence[:15]
    
    return state


def planner_agent(state: AgentState) -> AgentState:
    """
    Planner Agent: Generates operational objectives, tasks, and resource needs
    """
    llm = get_llm()
    structured = state["structured_incident"]
    evidence = state["evidence"]
    
    # Format evidence for context (top 10 chunks)
    evidence_text = "\n\n".join([
        f"[Citation: {ev['citation_id']}]\n{ev['text'][:500]}"
        for ev in evidence[:10]
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an emergency response planner. Generate an operational plan based on incident data and evidence from authoritative sources.
        
        Return ONLY valid JSON with these fields:
        - objectives: list of operational objectives (prioritized)
        - tasks: list of specific tasks with priorities (1=highest, 3=lowest)
        - resource_needs: list of resources needed (type, quantity if known, priority)
        - assumptions: list of assumptions made
        - time_horizon: operational period focus (e.g., "0-2 hours", "2-6 hours")
        - safety_considerations: list of safety concerns
        
        Example format:
        {{"objectives": ["Ensure life safety", "Establish triage"], "tasks": [{{"task": "Set up triage area", "priority": 1}}], "resource_needs": [{{"type": "Medical supplies", "priority": 1}}], "assumptions": ["Weather will continue"], "time_horizon": "0-2 hours", "safety_considerations": ["Flooding may worsen"]}}"""),
        ("user", """Incident Data:
{incident_data}

Evidence from Knowledge Base:
{evidence}

Generate an operational plan based on this information. Use the evidence to support your recommendations. Prioritize life safety first.""")
    ])
    
    # Format incident data
    incident_summary = f"""Hazards: {structured.get('hazards', [])}
Injuries: {structured.get('injuries', [])}
Infrastructure Status: {structured.get('infrastructure_status', [])}
Weather: {structured.get('weather', 'Unknown')}
Available Responders: {structured.get('available_responders', [])}
Constraints: {structured.get('constraints', [])}"""
    
    chain = prompt | llm
    response = chain.invoke({
        "incident_data": incident_summary,
        "evidence": evidence_text
    })
    
    plan = parse_json_from_llm(response.content)
    
    # Add human-readable summary
    if isinstance(plan, dict) and "error" not in plan:
        objectives = plan.get('objectives', [])
        tasks = plan.get('tasks', [])
        resource_needs = plan.get('resource_needs', [])
        safety = plan.get('safety_considerations', [])
        assumptions = plan.get('assumptions', [])
        
        plan["human_readable"] = f"""Operational Plan

Time Horizon: {plan.get('time_horizon', 'Not specified')}

Objectives:
{chr(10).join(f"  - {obj}" for obj in objectives)}

Key Tasks (Priority 1):
{chr(10).join(f"  - {t.get('task', t) if isinstance(t, dict) else t}" for t in tasks if (isinstance(t, dict) and t.get('priority') == 1) or not isinstance(t, dict))}

Resource Needs (Priority 1):
{chr(10).join(f"  - {r.get('type', r) if isinstance(r, dict) else r}" for r in resource_needs if (isinstance(r, dict) and r.get('priority') == 1) or not isinstance(r, dict))}

Safety Considerations:
{chr(10).join(f"  - {sc}" for sc in safety)}

Assumptions:
{chr(10).join(f"  - {a}" for a in assumptions)}
"""
    
    state["plan"] = plan
    return state


def comms_agent(state: AgentState) -> AgentState:
    """
    Comms Agent: Generates public-facing and internal messaging
    """
    llm = get_llm()
    structured = state["structured_incident"]
    plan = state["plan"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a communications specialist for emergency management. Generate clear, accessible messaging for different audiences.
        
        Return ONLY valid JSON with these fields:
        - public_advisory: Public-facing message (clear, non-technical, actionable)
        - internal_coordination: Internal message for responder coordination (more technical)
        - volunteer_message: Message for volunteer coordination (if applicable)
        - key_points: List of key points to emphasize (3-5 items)
        
        Example format:
        {{"public_advisory": "Residents are advised to...", "internal_coordination": "Operations briefing: ...", "volunteer_message": "Volunteers needed for...", "key_points": ["Safety first", "Stay informed"]}}"""),
        ("user", """Incident Data:
Hazards: {hazards}
Injuries: {injuries}
Infrastructure: {infrastructure}
Weather: {weather}

Operational Plan:
Objectives: {objectives}
Key Tasks: {key_tasks}
Safety Considerations: {safety}

Generate messaging for public, internal coordination, and volunteers. Use clear, accessible language for public messages. Include actionable guidance.""")
    ])
    
    # Format plan data
    objectives = plan.get("objectives", []) if isinstance(plan, dict) else []
    tasks = plan.get("tasks", []) if isinstance(plan, dict) else []
    key_tasks = [t.get("task", t) if isinstance(t, dict) else str(t) for t in (tasks[:5] if isinstance(tasks, list) else [])]
    safety = plan.get("safety_considerations", []) if isinstance(plan, dict) else []
    
    chain = prompt | llm
    response = chain.invoke({
        "hazards": structured.get("hazards", []),
        "injuries": structured.get("injuries", []),
        "infrastructure": structured.get("infrastructure_status", []),
        "weather": structured.get("weather", "Unknown"),
        "objectives": objectives,
        "key_tasks": key_tasks,
        "safety": safety
    })
    
    comms = parse_json_from_llm(response.content)
    state["comms"] = comms
    return state


def verifier_agent(state: AgentState) -> AgentState:
    """
    Verifier Agent: Validates claims, checks citations, enforces safety rules
    """
    llm = get_llm()
    structured = state["structured_incident"]
    evidence = state["evidence"]
    plan = state["plan"]
    comms = state["comms"]
    
    # Build citation map from evidence
    unique_citations = set(ev.get("citation_id", "") for ev in evidence)
    
    # Detect high-risk topics - ensure both are lists
    hazards = normalize_to_list(structured.get("hazards"))
    injuries = normalize_to_list(structured.get("injuries"))
    
    high_risk_keywords = ["medical", "evacuation", "hazmat", "chemical", "fire", "explosion", "collapse"]
    all_items = hazards + injuries
    is_high_risk = any(
        any(keyword in str(h).lower() for keyword in high_risk_keywords) 
        for h in all_items
    )
    
    # Check for immediate danger scenarios
    immediate_danger_keywords = ["active shooter", "bomb", "explosion", "structural collapse", "critical injury", "mass casualty"]
    incident_text = state["incident_report"].lower()
    has_immediate_danger = any(keyword in incident_text for keyword in immediate_danger_keywords)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a verification specialist for emergency operations. Validate operational plans and flag issues.
        
        Return ONLY valid JSON with these fields:
        - verified_plan: The operational plan (copy if valid, flag issues if not)
        - verified_comms: The communications (copy if valid, flag issues if not)
        - citation_coverage: Assessment of citation coverage (e.g., "all_claims_cited", "some_missing", "insufficient")
        - confidence_score: Overall confidence (0.0-1.0)
        - flagged_issues: List of issues found (e.g., "missing_citation", "low_confidence", "contradiction")
        - multi_source_status: For high-risk topics, check if 2+ independent sources exist ("validated", "insufficient_sources", "not_applicable")
        - safety_override: If immediate danger detected, set to "CALL_911_IMMEDIATELY", else null
        - known_claims: List of claims with citations (what we know)
        - unknown_claims: List of claims without sufficient evidence (what we don't know)
        - safe_next_steps: Recommended safe actions even with uncertainty
        
        Example format:
        {{"verified_plan": {{...}}, "verified_comms": {{...}}, "citation_coverage": "all_claims_cited", "confidence_score": 0.85, "flagged_issues": [], "multi_source_status": "validated", "safety_override": null, "known_claims": ["..."], "unknown_claims": ["..."], "safe_next_steps": ["..."]}}"""),
        ("user", """Incident Data:
Hazards: {hazards}
Injuries: {injuries}
Infrastructure: {infrastructure}

Operational Plan:
{plan}

Communications:
{comms}

Evidence Citations Available: {num_citations} unique sources
Unique Citations: {citation_list}

High-Risk Topic Detected: {is_high_risk}
Immediate Danger Detected: {immediate_danger}

Validate the plan and communications.""")
    ])
    
    citation_list = list(unique_citations)[:10]
    
    chain = prompt | llm
    response = chain.invoke({
        "hazards": hazards,
        "injuries": injuries,
        "infrastructure": structured.get("infrastructure_status", []),
        "plan": json.dumps(plan, indent=2) if isinstance(plan, dict) else str(plan),
        "comms": json.dumps(comms, indent=2) if isinstance(comms, dict) else str(comms),
        "num_citations": len(unique_citations),
        "citation_list": ", ".join(citation_list),
        "is_high_risk": is_high_risk,
        "immediate_danger": has_immediate_danger
    })
    
    verification_result = parse_json_from_llm(response.content)
    
    # Build final output
    final_output = {
        "verified_plan": verification_result.get("verified_plan", plan),
        "verified_comms": verification_result.get("verified_comms", comms),
        "verification": {
            "citation_coverage": verification_result.get("citation_coverage", "unknown"),
            "confidence_score": verification_result.get("confidence_score", 0.5),
            "flagged_issues": verification_result.get("flagged_issues", []),
            "multi_source_status": verification_result.get("multi_source_status", "not_applicable"),
            "safety_override": verification_result.get("safety_override"),
            "known_claims": verification_result.get("known_claims", []),
            "unknown_claims": verification_result.get("unknown_claims", []),
            "safe_next_steps": verification_result.get("safe_next_steps", [])
        },
        "structured_incident": structured,
        "evidence_summary": {
            "total_chunks": len(evidence),
            "unique_citations": len(unique_citations),
            "citation_ids": list(unique_citations)[:20]
        }
    }
    
    state["final_output"] = final_output
    return state


# Graph Construction


def build_graph() -> StateGraph:
    """Build and return the compiled agent graph"""
    graph = StateGraph(AgentState)
    
    # Add all agent nodes
    graph.add_node("intake", intake_agent)
    graph.add_node("retriever", retriever_agent)
    graph.add_node("planner", planner_agent)
    graph.add_node("comms", comms_agent)
    graph.add_node("verifier", verifier_agent)
    
    # Define the flow
    graph.set_entry_point("intake")
    graph.add_edge("intake", "retriever")
    graph.add_edge("retriever", "planner")
    graph.add_edge("planner", "comms")
    graph.add_edge("comms", "verifier")
    graph.add_edge("verifier", END)
    
    return graph.compile()


# Pipeline Runner

def run_pipeline(incident_report: str) -> Dict[str, Any]:
    """
    Run the complete 5-agent pipeline on an incident report.
    
    Args:
        incident_report: Free-text description of the incident
        
    Returns:
        Complete result including verified plan, comms, and verification metrics
    """
    app = build_graph()
    
    initial_state = {
        "incident_report": incident_report,
        "structured_incident": {},
        "evidence": [],
        "plan": {},
        "comms": {},
        "final_output": {}
    }
    
    result = app.invoke(initial_state)
    return result


def print_result_summary(result: Dict[str, Any]):
    """Print a formatted summary of pipeline results"""
    print("=" * 80)
    print("PIPELINE RESULT SUMMARY")
    print("=" * 80)
    
    print("\n📋 Structured Incident:")
    print(json.dumps(result["structured_incident"], indent=2))
    
    print(f"\n📚 Evidence: {len(result['evidence'])} chunks retrieved")
    unique_citations = len(set(ev.get('citation_id', '') for ev in result['evidence']))
    print(f"   Unique citations: {unique_citations}")
    
    print("\n📝 Operational Plan:")
    if isinstance(result["plan"], dict):
        print(f"   Objectives: {len(result['plan'].get('objectives', []))}")
        print(f"   Tasks: {len(result['plan'].get('tasks', []))}")
        print(f"   Time Horizon: {result['plan'].get('time_horizon', 'N/A')}")
    
    print("\n📣 Communications:")
    if isinstance(result["comms"], dict) and "error" not in result["comms"]:
        public = result['comms'].get('public_advisory', '')[:150]
        print(f"   Public Advisory: {public}...")
    
    print("\n✅ Verification:")
    if isinstance(result["final_output"], dict) and "verification" in result["final_output"]:
        verif = result["final_output"]["verification"]
        print(f"   Citation Coverage: {verif.get('citation_coverage', 'N/A')}")
        print(f"   Confidence Score: {verif.get('confidence_score', 0):.2f}")
        print(f"   Multi-Source Status: {verif.get('multi_source_status', 'N/A')}")
        if verif.get("safety_override"):
            print(f"   ⚠️  SAFETY OVERRIDE: {verif['safety_override']}")
        print(f"   Flagged Issues: {len(verif.get('flagged_issues', []))}")
        print(f"   Known Claims: {len(verif.get('known_claims', []))}")
        print(f"   Unknown Claims: {len(verif.get('unknown_claims', []))}")


# Test Scenarios
  
TEST_SCENARIOS = [
    {
        "name": "Urban Flooding",
        "description": "Flood in downtown area. Water level rising. Multiple buildings affected. No injuries reported yet. Rain expected to continue.",
        "expected_hazards": ["flood"],
        "risk_level": "medium"
    },
    {
        "name": "Wildfire Smoke",
        "description": "Wildfire approaching residential area. Heavy smoke visible. Air quality deteriorating. Residents reporting breathing difficulties. Evacuation ordered for zones 3-5.",
        "expected_hazards": ["wildfire", "smoke"],
        "risk_level": "high"
    },
    {
        "name": "Earthquake with Aftershocks",
        "description": "Magnitude 6.5 earthquake struck downtown. Multiple buildings damaged. Several injuries reported. Aftershocks continuing. Power outages in affected areas.",
        "expected_hazards": ["earthquake", "aftershocks"],
        "risk_level": "high"
    },
    {
        "name": "Hurricane Landfall",
        "description": "Hurricane making landfall. High winds and storm surge expected. Mandatory evacuation for coastal areas. Emergency shelters opening. Residents advised to stay indoors.",
        "expected_hazards": ["hurricane", "high winds"],
        "risk_level": "high"
    },
    {
        "name": "Chemical Spill",
        "description": "Chemical spill at industrial facility. Hazmat team responding. Downwind area evacuated. Unknown chemical composition. Multiple responders on scene.",
        "expected_hazards": ["chemical spill"],
        "risk_level": "high"
    },
    {
        "name": "Tornado Touchdown",
        "description": "Tornado touched down in residential neighborhood. Multiple homes destroyed. Injuries reported. Search and rescue operations underway. Power lines down.",
        "expected_hazards": ["tornado"],
        "risk_level": "high"
    },
    {
        "name": "Winter Storm",
        "description": "Severe winter storm. Heavy snow and ice. Multiple road closures. Power outages affecting 5000+ homes. Emergency services responding to downed lines.",
        "expected_hazards": ["winter storm", "snow", "ice"],
        "risk_level": "medium"
    },
    {
        "name": "Multi-Hazard: Flood + Landslide",
        "description": "Heavy rainfall causing flooding and triggering landslides in hilly terrain. Several roads blocked. Homes at risk. Evacuation recommended for affected slopes.",
        "expected_hazards": ["flood", "landslide"],
        "risk_level": "high"
    }
]


def run_test_suite(scenarios: List[Dict] = None):
    """Run the pipeline on test scenarios"""
    import time
    
    if scenarios is None:
        scenarios = TEST_SCENARIOS
    
    results = []
    start_time = time.time()
    
    print("=" * 80)
    print("COMPREHENSIVE PIPELINE TEST: 5-AGENT SYSTEM")
    print("=" * 80)
    print(f"Testing {len(scenarios)} scenarios...")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] Processing: {scenario['name']}")
        print("-" * 80)
        
        try:
            scenario_start = time.time()
            result = run_pipeline(scenario["description"])
            scenario_time = time.time() - scenario_start
            
            # Extract metrics
            hazards = result["structured_incident"].get("hazards", [])
            evidence_count = len(result["evidence"])
            unique_citations = len(set(ev.get("citation_id", "") for ev in result["evidence"]))
            
            verif = result.get("final_output", {}).get("verification", {})
            confidence = verif.get("confidence_score", 0)
            coverage = verif.get("citation_coverage", "unknown")
            
            print(f"  ✓ Processed in {scenario_time:.2f}s")
            print(f"  Hazards: {', '.join(str(h) for h in hazards[:3])}")
            print(f"  Evidence: {evidence_count} chunks, {unique_citations} citations")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Citation Coverage: {coverage}")
            
            results.append({
                "name": scenario["name"],
                "success": True,
                "time": scenario_time,
                "hazards": hazards,
                "evidence": evidence_count,
                "citations": unique_citations,
                "confidence": confidence,
                "coverage": coverage
            })
            
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            results.append({
                "name": scenario["name"],
                "success": False,
                "error": str(e)
            })
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    successful = sum(1 for r in results if r.get("success"))
    print(f"Total: {len(scenarios)} | Successful: {successful} | Failed: {len(scenarios) - successful}")
    print(f"Total time: {total_time:.2f}s | Avg per scenario: {total_time/len(scenarios):.2f}s")
    
    return results




if __name__ == "__main__":
    # Example usage
    print("DisasterOps Agent Framework")
    print("=" * 80)
    
    # Run a single test
    test_incident = "Flood in downtown area. Water level rising. Multiple buildings affected. No injuries reported yet. Rain expected to continue."
    
    print(f"\nTest Incident: {test_incident}\n")
    
    result = run_pipeline(test_incident)
    print_result_summary(result)

 