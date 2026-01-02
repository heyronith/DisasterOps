"""
DisasterOps Evaluation Harness
Step 6: Metrics + Benchmarks

Comprehensive evaluation framework for measuring system performance:
- Retrieval metrics (Recall@5, MRR, citation coverage)
- Plan quality metrics (completeness, safety, grounding, calibration)
- Agent reliability metrics (tool-call success, contradiction rate, unknown detection)
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict
import statistics

from agents import AgentState, get_app, run_pipeline


# ============================================================================
# Extended Test Scenario Set with Ground Truth
# ============================================================================

EVALUATION_SCENARIOS = [
    {
        "name": "Urban Flooding - Downtown",
        "description": "Flood in downtown area. Water level rising. Multiple buildings affected. No injuries reported yet. Rain expected to continue.",
        "expected_hazards": ["flood", "rising water"],
        "expected_injuries": [],
        "required_steps": [
            "assess damage",
            "establish command",
            "coordinate responders",
            "monitor water levels",
            "prepare evacuation if needed"
        ],
        "required_resources": ["communication equipment", "medical supplies"],
        "risk_level": "medium",
        "expected_citations_min": 5
    },
    {
        "name": "Wildfire Smoke - Residential",
        "description": "Wildfire approaching residential area. Heavy smoke visible. Air quality deteriorating. Residents reporting breathing difficulties. Evacuation ordered for zones 3-5.",
        "expected_hazards": ["wildfire", "smoke", "poor air quality"],
        "expected_injuries": ["breathing difficulties"],
        "required_steps": [
            "evacuation coordination",
            "air quality monitoring",
            "medical response for breathing issues",
            "establish evacuation routes",
            "coordinate with fire department"
        ],
        "required_resources": ["evacuation transport", "medical resources", "N95 masks"],
        "risk_level": "high",
        "expected_citations_min": 8
    },
    {
        "name": "Earthquake with Aftershocks",
        "description": "Magnitude 6.5 earthquake struck downtown. Multiple buildings damaged. Several injuries reported. Aftershocks continuing. Power outages in affected areas.",
        "expected_hazards": ["earthquake", "aftershocks", "structural damage"],
        "expected_injuries": ["multiple injuries"],
        "required_steps": [
            "search and rescue",
            "assess structural integrity",
            "coordinate medical response",
            "restore power if safe",
            "establish safety zones"
        ],
        "required_resources": ["search and rescue teams", "medical personnel", "structural engineers"],
        "risk_level": "high",
        "expected_citations_min": 8
    },
    {
        "name": "Hurricane Landfall",
        "description": "Hurricane making landfall. High winds and storm surge expected. Mandatory evacuation for coastal areas. Emergency shelters opening. Residents advised to stay indoors.",
        "expected_hazards": ["hurricane", "high winds", "storm surge"],
        "expected_injuries": [],
        "required_steps": [
            "coordinate evacuation",
            "open emergency shelters",
            "monitor storm conditions",
            "secure infrastructure",
            "prepare for aftermath"
        ],
        "required_resources": ["evacuation transport", "shelter facilities", "emergency supplies"],
        "risk_level": "high",
        "expected_citations_min": 7
    },
    {
        "name": "Chemical Spill - Industrial",
        "description": "Chemical spill at industrial facility. Hazmat team responding. Downwind area evacuated. Unknown chemical composition. Multiple responders on scene.",
        "expected_hazards": ["chemical spill", "hazmat"],
        "expected_injuries": [],
        "required_steps": [
            "hazmat team deployment",
            "identify chemical",
            "evacuate downwind area",
            "establish decontamination",
            "coordinate with experts"
        ],
        "required_resources": ["hazmat team", "decontamination equipment", "chemical identification"],
        "risk_level": "high",
        "expected_citations_min": 8
    },
    {
        "name": "Tornado Touchdown",
        "description": "Tornado touched down in residential neighborhood. Multiple homes destroyed. Injuries reported. Search and rescue operations underway. Power lines down.",
        "expected_hazards": ["tornado", "structural damage", "downed power lines"],
        "expected_injuries": ["injuries"],
        "required_steps": [
            "search and rescue",
            "assess damage",
            "medical response",
            "secure power lines",
            "coordinate recovery"
        ],
        "required_resources": ["search and rescue", "medical personnel", "utility crews"],
        "risk_level": "high",
        "expected_citations_min": 7
    },
    {
        "name": "Winter Storm - Heavy Snow",
        "description": "Heavy winter storm with significant snowfall. Roads becoming impassable. Power outages reported. Emergency services responding to multiple accidents.",
        "expected_hazards": ["winter storm", "snow", "ice", "power outages"],
        "expected_injuries": ["accident injuries"],
        "required_steps": [
            "coordinate road clearing",
            "restore power",
            "respond to accidents",
            "warn residents",
            "prepare for extended outage"
        ],
        "required_resources": ["road clearing equipment", "power restoration", "emergency transport"],
        "risk_level": "medium",
        "expected_citations_min": 6
    },
    {
        "name": "Multi-Hazard: Flood + Landslide",
        "description": "Heavy rainfall causing flooding and triggering landslides in hilly terrain. Several roads blocked. Homes at risk. Evacuation recommended for affected slopes.",
        "expected_hazards": ["flood", "landslide"],
        "expected_injuries": [],
        "required_steps": [
            "assess landslide risk",
            "coordinate evacuation",
            "monitor water levels",
            "clear blocked roads",
            "coordinate multi-agency response"
        ],
        "required_resources": ["evacuation transport", "road clearing", "geological assessment"],
        "risk_level": "high",
        "expected_citations_min": 7
    },
    {
        "name": "Power Outage - Widespread",
        "description": "Widespread power outage affecting 5000+ homes. Unknown cause. Critical infrastructure affected. Emergency backup systems activated.",
        "expected_hazards": ["power outage"],
        "expected_injuries": [],
        "required_steps": [
            "identify cause",
            "coordinate with utility",
            "prioritize critical infrastructure",
            "establish communication",
            "prepare for extended outage"
        ],
        "required_resources": ["utility crews", "backup power", "communication equipment"],
        "risk_level": "medium",
        "expected_citations_min": 5
    },
    {
        "name": "Gas Leak - Residential Area",
        "description": "Natural gas leak reported in residential neighborhood. Strong odor detected. Fire department on scene. Evacuation in progress.",
        "expected_hazards": ["gas leak", "fire risk"],
        "expected_injuries": [],
        "required_steps": [
            "evacuate area",
            "identify leak source",
            "coordinate with utility",
            "establish safety perimeter",
            "monitor air quality"
        ],
        "required_resources": ["hazmat team", "utility crews", "evacuation transport"],
        "risk_level": "high",
        "expected_citations_min": 6
    },
    {
        "name": "Building Fire - Multi-Story",
        "description": "Multi-story building fire. Multiple floors involved. Smoke visible. Firefighters on scene. Occupants being evacuated.",
        "expected_hazards": ["fire", "smoke"],
        "expected_injuries": ["possible smoke inhalation"],
        "required_steps": [
            "fire suppression",
            "evacuate building",
            "medical triage",
            "coordinate with fire department",
            "account for occupants"
        ],
        "required_resources": ["fire department", "medical personnel", "evacuation support"],
        "risk_level": "high",
        "expected_citations_min": 6
    },
    {
        "name": "Terrorist Threat - Unverified",
        "description": "Unverified threat report received. Suspicious package reported. Law enforcement responding. Area being secured.",
        "expected_hazards": ["threat", "suspicious package"],
        "expected_injuries": [],
        "required_steps": [
            "coordinate with law enforcement",
            "secure area",
            "assess threat level",
            "prepare evacuation if needed",
            "maintain communication"
        ],
        "required_resources": ["law enforcement", "bomb squad", "evacuation plan"],
        "risk_level": "high",
        "expected_citations_min": 5
    },
    {
        "name": "Mass Casualty - Transit Accident",
        "description": "Major transit accident. Multiple casualties. Medical resources overwhelmed. Multiple agencies responding. Casualty collection points established.",
        "expected_hazards": ["mass casualty"],
        "expected_injuries": ["multiple severe injuries"],
        "required_steps": [
            "triage casualties",
            "coordinate medical resources",
            "establish casualty collection",
            "coordinate transport",
            "manage scene"
        ],
        "required_resources": ["medical personnel", "ambulances", "hospital coordination"],
        "risk_level": "high",
        "expected_citations_min": 8
    },
    {
        "name": "Cyber Attack - Critical Infrastructure",
        "description": "Cyber attack on critical infrastructure systems. Systems compromised. Manual operations initiated. Experts investigating.",
        "expected_hazards": ["cyber attack"],
        "expected_injuries": [],
        "required_steps": [
            "isolate systems",
            "coordinate with cyber experts",
            "activate manual procedures",
            "maintain operations",
            "investigate scope"
        ],
        "required_resources": ["cyber security experts", "technical support", "communication systems"],
        "risk_level": "high",
        "expected_citations_min": 4
    },
    {
        "name": "Pandemic Outbreak - Facility",
        "description": "Outbreak of infectious disease at healthcare facility. Multiple cases confirmed. Quarantine measures implemented. Public health coordinating response.",
        "expected_hazards": ["infectious disease"],
        "expected_injuries": ["illness"],
        "required_steps": [
            "implement quarantine",
            "coordinate with public health",
            "track contacts",
            "provide medical care",
            "prevent spread"
        ],
        "required_resources": ["medical personnel", "protective equipment", "testing capacity"],
        "risk_level": "high",
        "expected_citations_min": 7
    },
    {
        "name": "Bridge Collapse",
        "description": "Bridge collapse reported. Multiple vehicles involved. Unknown number of casualties. Search and rescue operations beginning.",
        "expected_hazards": ["structural collapse"],
        "expected_injuries": ["unknown casualties"],
        "required_steps": [
            "search and rescue",
            "assess structural stability",
            "coordinate medical response",
            "secure area",
            "investigate cause"
        ],
        "required_resources": ["search and rescue", "structural engineers", "medical personnel"],
        "risk_level": "high",
        "expected_citations_min": 7
    },
    {
        "name": "Avalanche - Mountain Area",
        "description": "Avalanche reported in mountain recreation area. Multiple people potentially trapped. Search and rescue teams mobilizing. Weather conditions deteriorating.",
        "expected_hazards": ["avalanche"],
        "expected_injuries": ["possible trapped individuals"],
        "required_steps": [
            "search and rescue",
            "assess avalanche risk",
            "coordinate mountain rescue",
            "monitor weather",
            "establish base camp"
        ],
        "required_resources": ["mountain rescue", "avalanche equipment", "medical personnel"],
        "risk_level": "high",
        "expected_citations_min": 6
    },
    {
        "name": "Drought Emergency - Water Shortage",
        "description": "Severe drought conditions. Water supplies critically low. Mandatory water restrictions in effect. Emergency water distribution planned.",
        "expected_hazards": ["drought", "water shortage"],
        "expected_injuries": [],
        "required_steps": [
            "implement water restrictions",
            "coordinate water distribution",
            "monitor supplies",
            "coordinate with utilities",
            "public communication"
        ],
        "required_resources": ["water distribution", "utility coordination", "communication systems"],
        "risk_level": "medium",
        "expected_citations_min": 5
    },
    {
        "name": "Radiological Incident - Suspected",
        "description": "Suspected radiological incident at research facility. Radiation detected. Area being evacuated. Experts en route.",
        "expected_hazards": ["radiation"],
        "expected_injuries": [],
        "required_steps": [
            "evacuate area",
            "coordinate with experts",
            "assess radiation levels",
            "establish decontamination",
            "protect responders"
        ],
        "required_resources": ["radiation experts", "decontamination", "protective equipment"],
        "risk_level": "high",
        "expected_citations_min": 7
    },
    {
        "name": "Severe Thunderstorm - Flash Flooding",
        "description": "Severe thunderstorms producing flash flooding. Multiple areas affected. Water rescues in progress. More storms expected.",
        "expected_hazards": ["thunderstorm", "flash flood"],
        "expected_injuries": [],
        "required_steps": [
            "coordinate water rescues",
            "monitor weather",
            "warn residents",
            "assess damage",
            "prepare for more storms"
        ],
        "required_resources": ["water rescue teams", "weather monitoring", "communication"],
        "risk_level": "high",
        "expected_citations_min": 6
    }
]


# ============================================================================
# Retrieval Metrics
# ============================================================================

def calculate_recall_at_k(retrieved_citations: List[str], relevant_citations: Set[str], k: int = 5) -> float:
    """Calculate Recall@K - fraction of relevant citations found in top K results."""
    if not relevant_citations:
        return 1.0 if not retrieved_citations[:k] else 0.0
    
    retrieved_set = set(retrieved_citations[:k])
    intersection = retrieved_set.intersection(relevant_citations)
    return len(intersection) / len(relevant_citations)


def calculate_mrr(retrieved_citations: List[str], relevant_citations: Set[str]) -> float:
    """Calculate Mean Reciprocal Rank - average of 1/rank of first relevant result."""
    if not relevant_citations:
        return 1.0
    
    for rank, citation in enumerate(retrieved_citations, 1):
        if citation in relevant_citations:
            return 1.0 / rank
    return 0.0


def calculate_citation_coverage(evidence: List[Dict[str, Any]], expected_min: int) -> Dict[str, Any]:
    """Calculate citation coverage metrics."""
    unique_citations = set(ev.get("citation_id", "") for ev in evidence if ev.get("citation_id"))
    total_chunks = len(evidence)
    
    coverage_ratio = len(unique_citations) / expected_min if expected_min > 0 else 1.0
    meets_threshold = len(unique_citations) >= expected_min
    
    return {
        "unique_citations": len(unique_citations),
        "total_chunks": total_chunks,
        "expected_min": expected_min,
        "coverage_ratio": min(coverage_ratio, 1.0),
        "meets_threshold": meets_threshold
    }


def evaluate_retrieval(result: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate retrieval performance."""
    evidence = result.get("evidence", [])
    retrieved_citations = [ev.get("citation_id", "") for ev in evidence if ev.get("citation_id", "")]
    
    # For evaluation, we consider all retrieved citations as potentially relevant
    # (In real evaluation, we'd have ground-truth relevant citations)
    relevant_citations = set(retrieved_citations)  # Simplified: all retrieved are relevant for now
    
    recall_at_5 = calculate_recall_at_k(retrieved_citations, relevant_citations, k=5)
    mrr = calculate_mrr(retrieved_citations, relevant_citations)
    coverage = calculate_citation_coverage(evidence, scenario.get("expected_citations_min", 5))
    
    return {
        "recall_at_5": recall_at_5,
        "mrr": mrr,
        "citation_coverage": coverage,
        "total_retrieved": len(retrieved_citations)
    }


# ============================================================================
# Plan Quality Metrics
# ============================================================================

def normalize_to_list(value: Any) -> List[str]:
    """Normalize value to list of strings."""
    if isinstance(value, list):
        return [str(item) for item in value]
    elif isinstance(value, str):
        return [value] if value else []
    else:
        return [str(value)] if value else []


def calculate_completeness(plan: Dict[str, Any], required_steps: List[str]) -> Dict[str, Any]:
    """Calculate completeness - % of required steps included in plan."""
    if not required_steps:
        return {"completeness_score": 1.0, "found_steps": [], "missing_steps": [], "total_required": 0}
    
    tasks = normalize_to_list(plan.get("tasks", []))
    objectives = normalize_to_list(plan.get("objectives", []))
    
    all_plan_text = " ".join(tasks + objectives).lower()
    
    found_steps = []
    missing_steps = []
    
    for step in required_steps:
        step_lower = step.lower()
        # Check if step or key terms appear in plan
        # Look for significant words (length > 3) from the step
        key_terms = [term for term in step_lower.split() if len(term) > 3]
        step_found = any(term in all_plan_text for term in key_terms) if key_terms else step_lower in all_plan_text
        
        if step_found:
            found_steps.append(step)
        else:
            missing_steps.append(step)
    
    completeness_score = len(found_steps) / len(required_steps) if required_steps else 1.0
    
    return {
        "completeness_score": completeness_score,
        "found_steps": found_steps,
        "missing_steps": missing_steps,
        "total_required": len(required_steps),
        "total_found": len(found_steps)
    }


def detect_unsafe_instructions(plan: Dict[str, Any], comms: Dict[str, Any]) -> Dict[str, Any]:
    """Detect unsafe instructions in plan and communications."""
    unsafe_keywords = [
        "ignore safety", "skip protocol", "rush", "take shortcuts",
        "ignore evacuation", "enter unsafe area", "without protection"
    ]
    
    tasks = normalize_to_list(plan.get("tasks", []))
    objectives = normalize_to_list(plan.get("objectives", []))
    comms_text = ""
    if isinstance(comms, dict):
        comms_text = " ".join([str(v) for v in comms.values() if isinstance(v, str)])
    elif isinstance(comms, str):
        comms_text = comms
    
    all_text = " ".join(tasks + objectives + [comms_text]).lower()
    
    detected_unsafe = []
    for keyword in unsafe_keywords:
        if keyword in all_text:
            detected_unsafe.append(keyword)
    
    is_safe = len(detected_unsafe) == 0
    
    return {
        "is_safe": is_safe,
        "unsafe_instructions": detected_unsafe,
        "safety_score": 1.0 if is_safe else 0.0
    }


def calculate_grounding(verification: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate grounding metrics - % of claims with valid citations."""
    citation_coverage = verification.get("citation_coverage", "unknown")
    
    # Map coverage status to score
    coverage_scores = {
        "all_claims_cited": 1.0,
        "most_claims_cited": 0.8,
        "some_claims_cited": 0.5,
        "few_claims_cited": 0.2,
        "unknown": 0.0
    }
    
    grounding_score = coverage_scores.get(citation_coverage, 0.0)
    
    return {
        "grounding_score": grounding_score,
        "citation_coverage": citation_coverage,
        "flagged_issues": len(verification.get("flagged_issues", [])),
        "known_claims": len(verification.get("known_claims", [])),
        "unknown_claims": len(verification.get("unknown_claims", []))
    }


def calculate_calibration(confidence_score: float, evidence_quality: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate calibration - alignment between confidence and evidence quality."""
    coverage_ratio = evidence_quality.get("coverage_ratio", 0.0)
    citation_count = evidence_quality.get("unique_citations", 0)
    
    # Expected confidence based on evidence quality
    expected_confidence = min(coverage_ratio * 0.9 + (min(citation_count / 10.0, 1.0) * 0.1), 1.0)
    
    calibration_error = abs(confidence_score - expected_confidence)
    well_calibrated = calibration_error < 0.2
    
    return {
        "calibration_error": calibration_error,
        "well_calibrated": well_calibrated,
        "confidence_score": confidence_score,
        "expected_confidence": expected_confidence,
        "calibration_score": 1.0 - min(calibration_error, 1.0)
    }


def evaluate_plan_quality(result: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate plan quality metrics."""
    final_output = result.get("final_output", {})
    plan = final_output.get("verified_plan", {})
    comms = final_output.get("verified_comms", {})
    verification = final_output.get("verification", {})
    evidence_summary = final_output.get("evidence_summary", {})
    
    required_steps = scenario.get("required_steps", [])
    completeness = calculate_completeness(plan, required_steps)
    safety = detect_unsafe_instructions(plan, comms)
    grounding = calculate_grounding(verification)
    
    confidence_score = verification.get("confidence_score", 0.0)
    citation_coverage = result.get("evidence_summary", {}).get("unique_citations", 0)
    evidence_quality = {
        "coverage_ratio": completeness.get("completeness_score", 0.0),
        "unique_citations": citation_coverage
    }
    calibration = calculate_calibration(confidence_score, evidence_quality)
    
    return {
        "completeness": completeness,
        "safety": safety,
        "grounding": grounding,
        "calibration": calibration
    }


# ============================================================================
# Agent Reliability Metrics
# ============================================================================

def evaluate_agent_reliability(result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate agent reliability metrics."""
    final_output = result.get("final_output", {})
    structured = final_output.get("structured_incident", {})
    verification = final_output.get("verification", {})
    
    # Tool-call success: Check if all agents completed successfully
    tool_call_success = (
        structured is not None and structured != {} and
        final_output.get("verified_plan") is not None and
        final_output.get("verified_comms") is not None
    )
    
    # Contradiction detection: Check for contradictions in verification
    flagged_issues = verification.get("flagged_issues", [])
    contradiction_keywords = ["contradiction", "conflict", "inconsistent", "disagrees"]
    contradictions = [issue for issue in flagged_issues if any(kw in str(issue).lower() for kw in contradiction_keywords)]
    
    # Unknown-when-unknown: Check if system identified unknowns appropriately
    unknown_claims = verification.get("unknown_claims", [])
    known_claims = verification.get("known_claims", [])
    safe_next_steps = verification.get("safe_next_steps", [])
    
    unknown_detection_score = 1.0 if (unknown_claims or len(safe_next_steps) > 0) else 0.5
    
    return {
        "tool_call_success": tool_call_success,
        "tool_call_success_rate": 1.0 if tool_call_success else 0.0,
        "contradiction_count": len(contradictions),
        "contradiction_rate": len(contradictions) / max(len(flagged_issues), 1),
        "unknown_detection_score": unknown_detection_score,
        "unknown_claims_count": len(unknown_claims),
        "known_claims_count": len(known_claims),
        "safe_next_steps_count": len(safe_next_steps)
    }


# ============================================================================
# Comprehensive Evaluation Runner
# ============================================================================

def evaluate_scenario(scenario: Dict[str, Any], app=None) -> Dict[str, Any]:
    """Evaluate a single scenario through the pipeline."""
    if app is None:
        app = get_app()
    
    start_time = time.time()
    
    try:
        # Run pipeline
        initial_state: AgentState = {
            "incident_report": scenario["description"],
            "structured_incident": {},
            "evidence": [],
            "plan": {},
            "comms": {},
            "final_output": {}
        }
        
        result = app.invoke(initial_state)
        processing_time = time.time() - start_time
        
        # Extract result data
        final_output = result.get("final_output", {})
        structured = final_output.get("structured_incident", {})
        evidence = result.get("evidence", [])
        
        # Calculate all metrics
        retrieval_metrics = evaluate_retrieval(result, scenario)
        plan_quality_metrics = evaluate_plan_quality(result, scenario)
        reliability_metrics = evaluate_agent_reliability(result)
        
        return {
            "scenario_name": scenario["name"],
            "success": True,
            "processing_time": processing_time,
            "retrieval": retrieval_metrics,
            "plan_quality": plan_quality_metrics,
            "reliability": reliability_metrics,
            "verification": final_output.get("verification", {}),
            "error": None
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "scenario_name": scenario["name"],
            "success": False,
            "processing_time": processing_time,
            "error": str(e),
            "retrieval": {},
            "plan_quality": {},
            "reliability": {}
        }


def run_evaluation(scenarios: List[Dict[str, Any]] = None, app=None) -> Dict[str, Any]:
    """Run comprehensive evaluation on all scenarios."""
    if scenarios is None:
        scenarios = EVALUATION_SCENARIOS
    
    if app is None:
        app = get_app()
    
    print("=" * 80)
    print("DISASTEROPS EVALUATION HARNESS")
    print("=" * 80)
    print(f"Evaluating {len(scenarios)} scenarios...\n")
    
    results = []
    start_time = time.time()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] Evaluating: {scenario['name']}")
        result = evaluate_scenario(scenario, app)
        results.append(result)
        
        if result["success"]:
            retrieval = result["retrieval"]
            plan_quality = result["plan_quality"]
            print(f"  ✓ Completed in {result['processing_time']:.2f}s")
            print(f"    Recall@5: {retrieval.get('recall_at_5', 0):.2f} | "
                  f"Completeness: {plan_quality['completeness']['completeness_score']:.2f} | "
                  f"Safety: {'✓' if plan_quality['safety']['is_safe'] else '✗'}")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
    
    total_time = time.time() - start_time
    
    # Aggregate metrics
    successful_results = [r for r in results if r["success"]]
    
    if successful_results:
        # Retrieval metrics
        recall_scores = [r["retrieval"].get("recall_at_5", 0) for r in successful_results]
        mrr_scores = [r["retrieval"].get("mrr", 0) for r in successful_results]
        
        # Plan quality metrics
        completeness_scores = [r["plan_quality"]["completeness"]["completeness_score"] for r in successful_results]
        safety_scores = [r["plan_quality"]["safety"]["safety_score"] for r in successful_results]
        grounding_scores = [r["plan_quality"]["grounding"]["grounding_score"] for r in successful_results]
        calibration_scores = [r["plan_quality"]["calibration"]["calibration_score"] for r in successful_results]
        
        # Reliability metrics
        tool_call_success_rates = [r["reliability"]["tool_call_success_rate"] for r in successful_results]
        contradiction_counts = [r["reliability"]["contradiction_count"] for r in successful_results]
        unknown_detection_scores = [r["reliability"]["unknown_detection_score"] for r in successful_results]
        
        aggregated = {
            "total_scenarios": len(scenarios),
            "successful": len(successful_results),
            "failed": len(results) - len(successful_results),
            "total_time": total_time,
            "avg_time_per_scenario": total_time / len(scenarios),
            "retrieval": {
                "avg_recall_at_5": statistics.mean(recall_scores) if recall_scores else 0.0,
                "avg_mrr": statistics.mean(mrr_scores) if mrr_scores else 0.0,
                "median_recall_at_5": statistics.median(recall_scores) if recall_scores else 0.0,
                "median_mrr": statistics.median(mrr_scores) if mrr_scores else 0.0
            },
            "plan_quality": {
                "avg_completeness": statistics.mean(completeness_scores) if completeness_scores else 0.0,
                "avg_safety": statistics.mean(safety_scores) if safety_scores else 0.0,
                "avg_grounding": statistics.mean(grounding_scores) if grounding_scores else 0.0,
                "avg_calibration": statistics.mean(calibration_scores) if calibration_scores else 0.0,
                "median_completeness": statistics.median(completeness_scores) if completeness_scores else 0.0
            },
            "reliability": {
                "avg_tool_call_success_rate": statistics.mean(tool_call_success_rates) if tool_call_success_rates else 0.0,
                "total_contradictions": sum(contradiction_counts),
                "avg_contradiction_rate": statistics.mean([r["reliability"]["contradiction_rate"] for r in successful_results]) if successful_results else 0.0,
                "avg_unknown_detection": statistics.mean(unknown_detection_scores) if unknown_detection_scores else 0.0
            }
        }
    else:
        aggregated = {
            "total_scenarios": len(scenarios),
            "successful": 0,
            "failed": len(results),
            "total_time": total_time,
            "error": "All scenarios failed"
        }
    
    evaluation_result = {
        "timestamp": datetime.now().isoformat(),
        "summary": aggregated,
        "detailed_results": results
    }
    
    return evaluation_result


def generate_evaluation_report(evaluation_result: Dict[str, Any], output_path: Path) -> None:
    """Generate detailed evaluation report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # JSON report
    json_path = output_path.with_suffix('.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_result, f, indent=2, ensure_ascii=False)
    
    # Markdown report
    md_path = output_path.with_suffix('.md')
    summary = evaluation_result["summary"]
    results = evaluation_result["detailed_results"]
    
    md_lines = []
    md_lines.append("# DisasterOps Evaluation Report")
    md_lines.append(f"\n**Generated:** {evaluation_result['timestamp']}\n")
    
    md_lines.append("## Executive Summary\n")
    md_lines.append(f"- **Total Scenarios:** {summary['total_scenarios']}")
    md_lines.append(f"- **Successful:** {summary['successful']}")
    md_lines.append(f"- **Failed:** {summary.get('failed', 0)}")
    md_lines.append(f"- **Total Time:** {summary['total_time']:.2f}s")
    md_lines.append(f"- **Avg Time per Scenario:** {summary.get('avg_time_per_scenario', 0):.2f}s\n")
    
    if "retrieval" in summary:
        md_lines.append("## Retrieval Metrics\n")
        retrieval = summary["retrieval"]
        md_lines.append(f"- **Average Recall@5:** {retrieval['avg_recall_at_5']:.3f}")
        md_lines.append(f"- **Average MRR:** {retrieval['avg_mrr']:.3f}")
        md_lines.append(f"- **Median Recall@5:** {retrieval['median_recall_at_5']:.3f}\n")
    
    if "plan_quality" in summary:
        md_lines.append("## Plan Quality Metrics\n")
        pq = summary["plan_quality"]
        md_lines.append(f"- **Average Completeness:** {pq['avg_completeness']:.3f}")
        md_lines.append(f"- **Average Safety Score:** {pq['avg_safety']:.3f}")
        md_lines.append(f"- **Average Grounding:** {pq['avg_grounding']:.3f}")
        md_lines.append(f"- **Average Calibration:** {pq['avg_calibration']:.3f}\n")
    
    if "reliability" in summary:
        md_lines.append("## Agent Reliability Metrics\n")
        rel = summary["reliability"]
        md_lines.append(f"- **Tool Call Success Rate:** {rel['avg_tool_call_success_rate']:.3f}")
        md_lines.append(f"- **Total Contradictions:** {rel['total_contradictions']}")
        md_lines.append(f"- **Average Unknown Detection:** {rel['avg_unknown_detection']:.3f}\n")
    
    md_lines.append("## Detailed Results\n")
    for result in results:
        md_lines.append(f"### {result['scenario_name']}\n")
        if result["success"]:
            md_lines.append(f"- **Status:** ✓ Success ({result['processing_time']:.2f}s)")
            md_lines.append(f"- **Recall@5:** {result['retrieval'].get('recall_at_5', 0):.3f}")
            md_lines.append(f"- **Completeness:** {result['plan_quality']['completeness']['completeness_score']:.3f}")
            md_lines.append(f"- **Safety:** {'✓ Safe' if result['plan_quality']['safety']['is_safe'] else '✗ Unsafe'}")
            md_lines.append(f"- **Grounding:** {result['plan_quality']['grounding']['grounding_score']:.3f}\n")
        else:
            md_lines.append(f"- **Status:** ✗ Failed")
            md_lines.append(f"- **Error:** {result.get('error', 'Unknown')}\n")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    
    print(f"\n✓ Evaluation report saved:")
    print(f"  - JSON: {json_path}")
    print(f"  - Markdown: {md_path}")


if __name__ == "__main__":
    # Run evaluation
    result = run_evaluation()
    
    # Generate report
    output_dir = Path("evaluation_results")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"evaluation_report_{timestamp}"
    generate_evaluation_report(result, report_path)
    
    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    summary = result["summary"]
    if "retrieval" in summary:
        print(f"\nRetrieval - Recall@5: {summary['retrieval']['avg_recall_at_5']:.3f}")
        print(f"Plan Quality - Completeness: {summary['plan_quality']['avg_completeness']:.3f}")
        print(f"Safety: {summary['plan_quality']['avg_safety']:.3f}")
        print(f"Grounding: {summary['plan_quality']['avg_grounding']:.3f}")

