"""
DisasterOps Structured Output Generation
Step 5: ICS Forms + Operational Artifacts

Generates structured operational outputs from agent pipeline results:
- Situation Brief
- Triage + Priorities
- Mini-IAP (Incident Action Plan)
- Resource Requests
- Communications Drafts
- ICS Forms (201, 202, 205, 206)
- Export formats (JSON, Markdown, PDF)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def generate_situation_brief(final_output: Dict[str, Any], incident_name: str = "Incident") -> Dict[str, Any]:
    """Generate Situation Brief from final output."""
    structured = final_output.get("structured_incident", {})
    plan = final_output.get("verified_plan", {})
    evidence_summary = final_output.get("evidence_summary", {})
    verification = final_output.get("verification", {})
    
    hazards = structured.get("hazards", [])
    injuries = structured.get("injuries", [])
    infrastructure = structured.get("infrastructure_status", [])
    weather = structured.get("weather", "")
    
    if isinstance(hazards, str):
        hazards = [hazards] if hazards else []
    if isinstance(injuries, str):
        injuries = [injuries] if injuries else []
    if isinstance(infrastructure, str):
        infrastructure = [infrastructure] if infrastructure else []
    
    brief = {
        "incident_name": incident_name,
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "situation_summary": {
            "hazards": hazards,
            "injuries_reported": injuries,
            "infrastructure_status": infrastructure,
            "weather_conditions": weather if isinstance(weather, str) else ", ".join(weather) if isinstance(weather, list) else "",
            "available_responders": structured.get("available_responders", []),
            "constraints": structured.get("constraints", [])
        },
        "current_status": {
            "objectives_count": len(plan.get("objectives", [])),
            "tasks_count": len(plan.get("tasks", [])) if isinstance(plan.get("tasks"), list) else 0,
            "time_horizon": plan.get("time_horizon", "Not specified"),
            "evidence_sources": evidence_summary.get("unique_citations", 0),
            "confidence_score": verification.get("confidence_score", 0.0)
        },
        "key_objectives": plan.get("objectives", [])[:5],
        "safety_considerations": plan.get("safety_considerations", [])[:5] if isinstance(plan.get("safety_considerations"), list) else [],
        "verification_status": {
            "citation_coverage": verification.get("citation_coverage", "unknown"),
            "flagged_issues_count": len(verification.get("flagged_issues", [])),
            "multi_source_status": verification.get("multi_source_status", "not_applicable"),
            "safety_override": verification.get("safety_override")
        }
    }
    
    return brief


def generate_triage_priorities(final_output: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Triage + Priorities document."""
    structured = final_output.get("structured_incident", {})
    plan = final_output.get("verified_plan", {})
    
    objectives = plan.get("objectives", [])
    tasks = plan.get("tasks", [])
    resource_needs = plan.get("resource_needs", [])
    
    if isinstance(objectives, str):
        objectives = [objectives]
    if isinstance(tasks, str):
        tasks = [tasks]
    if isinstance(resource_needs, str):
        resource_needs = [resource_needs]
    
    # Extract priority information from tasks
    priority_1_tasks = []
    priority_2_tasks = []
    other_tasks = []
    
    if isinstance(tasks, list):
        for task in tasks:
            task_str = task if isinstance(task, str) else task.get("task", "") if isinstance(task, dict) else str(task)
            task_lower = task_str.lower()
            if "priority 1" in task_lower or "immediate" in task_lower or "critical" in task_lower:
                priority_1_tasks.append(task_str)
            elif "priority 2" in task_lower or "urgent" in task_lower:
                priority_2_tasks.append(task_str)
            else:
                other_tasks.append(task_str)
    
    if not priority_1_tasks and tasks:
        priority_1_tasks = tasks[:3] if len(tasks) >= 3 else tasks
    
    triage = {
        "prioritized_objectives": objectives[:5] if isinstance(objectives, list) else [],
        "priority_1_tasks": priority_1_tasks[:5],
        "priority_2_tasks": priority_2_tasks[:5],
        "other_tasks": other_tasks[:10],
        "critical_resource_needs": resource_needs[:5] if isinstance(resource_needs, list) else [],
        "assumptions": plan.get("assumptions", [])[:5] if isinstance(plan.get("assumptions"), list) else [],
        "time_horizon": plan.get("time_horizon", "Not specified"),
        "constraints": structured.get("constraints", [])[:5] if isinstance(structured.get("constraints"), list) else []
    }
    
    return triage


def generate_mini_iap(final_output: Dict[str, Any], incident_name: str = "Incident") -> Dict[str, Any]:
    """Generate Mini Incident Action Plan."""
    structured = final_output.get("structured_incident", {})
    plan = final_output.get("verified_plan", {})
    
    objectives = plan.get("objectives", [])
    tasks = plan.get("tasks", [])
    resource_needs = plan.get("resource_needs", [])
    assumptions = plan.get("assumptions", [])
    safety = plan.get("safety_considerations", [])
    
    if isinstance(objectives, str):
        objectives = [objectives]
    if isinstance(tasks, str):
        tasks = [tasks]
    if isinstance(resource_needs, str):
        resource_needs = [resource_needs]
    if isinstance(assumptions, str):
        assumptions = [assumptions]
    if isinstance(safety, str):
        safety = [safety]
    
    mini_iap = {
        "incident_name": incident_name,
        "operational_period": plan.get("time_horizon", "0-24 hours"),
        "objectives": objectives[:10] if isinstance(objectives, list) else [],
        "tasks_by_priority": {
            "priority_1": [t for t in (tasks[:5] if isinstance(tasks, list) else []) if "priority 1" in str(t).lower() or "immediate" in str(t).lower()],
            "priority_2": [t for t in (tasks[:5] if isinstance(tasks, list) else []) if "priority 2" in str(t).lower()],
            "other": [t for t in (tasks[:10] if isinstance(tasks, list) else []) if not ("priority" in str(t).lower())]
        },
        "resource_assignments": {
            "requested": resource_needs[:10] if isinstance(resource_needs, list) else [],
            "available": structured.get("available_responders", [])[:10]
        },
        "safety_message": safety[0] if safety and isinstance(safety, list) else (safety if isinstance(safety, str) else "Follow standard safety protocols"),
        "assumptions": assumptions[:5] if isinstance(assumptions, list) else [],
        "constraints": structured.get("constraints", [])[:5] if isinstance(structured.get("constraints"), list) else []
    }
    
    return mini_iap


def generate_resource_requests(final_output: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Resource Requests document."""
    plan = final_output.get("verified_plan", {})
    structured = final_output.get("structured_incident", {})
    
    resource_needs = plan.get("resource_needs", [])
    
    if isinstance(resource_needs, str):
        resource_needs = [resource_needs]
    
    resources = []
    for i, need in enumerate(resource_needs[:20] if isinstance(resource_needs, list) else [], 1):
        need_str = need if isinstance(need, str) else str(need)
        resources.append({
            "request_id": f"REQ-{i:03d}",
            "resource_type": need_str,
            "quantity": "TBD",
            "priority": "Priority 1" if i <= 5 else "Priority 2",
            "staging_location": "Incident Staging Area",
            "alternate_options": [],
            "justification": f"Required for {plan.get('time_horizon', 'operational period')}"
        })
    
    requests = {
        "incident_name": "Incident",
        "request_date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_requests": len(resources),
        "resources": resources,
        "available_local": structured.get("available_responders", [])[:10],
        "coordination_notes": "All requests subject to availability and approval"
    }
    
    return requests


def generate_comms_drafts(final_output: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Communications Drafts from verified comms."""
    comms = final_output.get("verified_comms", {})
    
    if isinstance(comms, str):
        comms = {"public_advisory": comms}
    
    drafts = {
        "public_advisory": comms.get("public_advisory", "Public advisory pending"),
        "internal_coordination": comms.get("internal_coordination", "Internal coordination message pending"),
        "volunteer_message": comms.get("volunteer_message", "Volunteer coordination message pending"),
        "key_talking_points": comms.get("key_points", [])[:5] if isinstance(comms.get("key_points"), list) else [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return drafts


def generate_ics201(final_output: Dict[str, Any], incident_name: str = "Incident", incident_number: str = "001") -> Dict[str, Any]:
    """Generate ICS 201 - Incident Briefing form."""
    structured = final_output.get("structured_incident", {})
    plan = final_output.get("verified_plan", {})
    
    hazards = structured.get("hazards", [])
    injuries = structured.get("injuries", [])
    infrastructure = structured.get("infrastructure_status", [])
    
    if isinstance(hazards, str):
        hazards = [hazards] if hazards else []
    if isinstance(injuries, str):
        injuries = [injuries] if injuries else []
    if isinstance(infrastructure, str):
        infrastructure = [infrastructure] if infrastructure else []
    
    now = datetime.now()
    
    # Situation summary
    situation_summary_parts = []
    if hazards:
        situation_summary_parts.append(f"Hazards: {', '.join(hazards)}")
    if injuries:
        situation_summary_parts.append(f"Injuries: {', '.join(injuries)}")
    if infrastructure:
        situation_summary_parts.append(f"Infrastructure: {', '.join(infrastructure)}")
    
    situation_summary = " ".join(situation_summary_parts) if situation_summary_parts else "Initial incident assessment in progress."
    
    health_safety = ", ".join(plan.get("safety_considerations", [])[:3]) if isinstance(plan.get("safety_considerations"), list) else (plan.get("safety_considerations", "") if isinstance(plan.get("safety_considerations"), str) else "Standard safety protocols apply.")
    
    # Objectives
    objectives = plan.get("objectives", [])
    if isinstance(objectives, str):
        objectives = [objectives]
    objectives_text = "\n".join([f"- {obj}" for obj in objectives[:5]]) if objectives else "Initial objectives pending"
    
    # Actions
    tasks = plan.get("tasks", [])
    if isinstance(tasks, str):
        tasks = [tasks]
    actions_text = "\n".join([f"{now.strftime('%H%M')} - {task}" for task in tasks[:5]]) if tasks else "Actions pending"
    
    ics201 = {
        "form_number": "ICS 201",
        "form_title": "INCIDENT BRIEFING",
        "block_1_incident_name": incident_name,
        "block_2_incident_number": incident_number,
        "block_3_date_time_initiated": {
            "date": now.strftime("%m/%d/%Y"),
            "time": now.strftime("%H%M")
        },
        "block_4_map_sketch": "[Map/Sketch area - to be completed with incident area details]",
        "block_5_situation_summary": situation_summary,
        "block_5_health_safety_briefing": health_safety,
        "block_6_prepared_by": {
            "name": "[Name]",
            "position_title": "Incident Commander",
            "signature": "[Signature]",
            "date_time": now.strftime("%m/%d/%Y %H%M")
        },
        "block_7_current_planned_objectives": objectives_text,
        "block_8_current_planned_actions": {
            "time": now.strftime("%H%M"),
            "actions": actions_text
        },
        "block_9_current_organization": "[Organization chart - to be completed with ICS structure]",
        "block_10_resource_summary": [
            {
                "resource": "[Resource type]",
                "resource_identifier": "TBD",
                "date_time_ordered": now.strftime("%m/%d/%Y %H%M"),
                "eta": "TBD",
                "arrived": False,
                "notes": "Resource request pending"
            }
        ]
    }
    
    return ics201


def generate_ics202(final_output: Dict[str, Any], incident_name: str = "Incident") -> Dict[str, Any]:
    """Generate ICS 202 - Incident Objectives form."""
    plan = final_output.get("verified_plan", {})
    
    now = datetime.now()
    operational_period_start = now
    operational_period_end = now.replace(hour=(now.hour + 12) % 24) if now.hour < 12 else now.replace(hour=(now.hour + 12) % 24, day=now.day + 1)
    
    objectives = plan.get("objectives", [])
    if isinstance(objectives, str):
        objectives = [objectives]
    
    objectives_text = "\n".join([f"{i+1}. {obj}" for i, obj in enumerate(objectives[:10])]) if objectives else "1. Ensure life safety\n2. Stabilize incident\n3. Protect property and environment"
    
    command_emphasis = plan.get("time_horizon", "Focus on immediate life safety and stabilization")
    
    safety_considerations = plan.get("safety_considerations", [])
    if isinstance(safety_considerations, str):
        safety_considerations = [safety_considerations]
    
    general_situational_awareness = "; ".join(safety_considerations[:3]) if safety_considerations else "Monitor conditions and maintain situational awareness"
    
    ics202 = {
        "form_number": "ICS 202",
        "form_title": "INCIDENT OBJECTIVES",
        "block_1_incident_name": incident_name,
        "block_2_operational_period": {
            "date_from": operational_period_start.strftime("%m/%d/%Y"),
            "time_from": operational_period_start.strftime("%H%M"),
            "date_to": operational_period_end.strftime("%m/%d/%Y"),
            "time_to": operational_period_end.strftime("%H%M")
        },
        "block_3_objectives": objectives_text,
        "block_4_operational_period_command_emphasis": command_emphasis,
        "block_4_general_situational_awareness": general_situational_awareness,
        "block_5_site_safety_plan_required": True,
        "block_5_approved_site_safety_plan_location": "Incident Safety Plan - See ICS 208",
        "block_6_iap_components": {
            "ics_203": True,
            "ics_204": True,
            "ics_205": True,
            "ics_205a": False,
            "ics_206": True,
            "ics_207": False,
            "ics_208": True,
            "map_chart": True,
            "weather_forecast": True,
            "other_attachments": []
        },
        "block_7_prepared_by": {
            "name": "[Name]",
            "position_title": "Planning Section Chief",
            "signature": "[Signature]",
            "date_time": now.strftime("%m/%d/%Y %H%M")
        },
        "block_8_approved_by_incident_commander": {
            "name": "[Name]",
            "signature": "[Signature]",
            "date_time": now.strftime("%m/%d/%Y %H%M")
        }
    }
    
    return ics202


def generate_ics205(final_output: Dict[str, Any], incident_name: str = "Incident") -> Dict[str, Any]:
    """Generate ICS 205 - Incident Radio Communications Plan."""
    now = datetime.now()
    operational_period_start = now
    operational_period_end = now.replace(hour=(now.hour + 12) % 24) if now.hour < 12 else now.replace(hour=(now.hour + 12) % 24, day=now.day + 1)
    
    ics205 = {
        "form_number": "ICS 205",
        "form_title": "INCIDENT RADIO COMMUNICATIONS PLAN",
        "block_1_incident_name": incident_name,
        "block_2_date_time_prepared": {
            "date": now.strftime("%m/%d/%Y"),
            "time": now.strftime("%H%M")
        },
        "block_3_operational_period": {
            "date_from": operational_period_start.strftime("%m/%d/%Y"),
            "time_from": operational_period_start.strftime("%H%M"),
            "date_to": operational_period_end.strftime("%m/%d/%Y"),
            "time_to": operational_period_end.strftime("%H%M")
        },
        "block_4_basic_radio_channel_use": [
            {
                "channel_number": "1",
                "function": "Command",
                "channel_name": "Command Net",
                "assignment": "Incident Command",
                "rx_freq": "TBD",
                "rx_tone_nac": "",
                "tx_freq": "TBD",
                "tx_tone_nac": "",
                "mode": "A",
                "remarks": "Primary command frequency"
            },
            {
                "channel_number": "2",
                "function": "Tactical",
                "channel_name": "Tactical 1",
                "assignment": "Operations",
                "rx_freq": "TBD",
                "rx_tone_nac": "",
                "tx_freq": "TBD",
                "tx_tone_nac": "",
                "mode": "A",
                "remarks": "Operations channel"
            },
            {
                "channel_number": "3",
                "function": "Support",
                "channel_name": "Support Net",
                "assignment": "Logistics/Planning",
                "rx_freq": "TBD",
                "rx_tone_nac": "",
                "tx_freq": "TBD",
                "tx_tone_nac": "",
                "mode": "A",
                "remarks": "Support operations"
            }
        ],
        "block_5_special_instructions": "Use standard ICS radio procedures. Maintain clear, concise communications.",
        "block_6_prepared_by": {
            "name": "[Name]",
            "position_title": "Communications Unit Leader",
            "signature": "[Signature]",
            "date_time": now.strftime("%m/%d/%Y %H%M")
        }
    }
    
    return ics205


def generate_ics206(final_output: Dict[str, Any], incident_name: str = "Incident") -> Dict[str, Any]:
    """Generate ICS 206 - Medical Plan."""
    structured = final_output.get("structured_incident", {})
    
    now = datetime.now()
    operational_period_start = now
    operational_period_end = now.replace(hour=(now.hour + 12) % 24) if now.hour < 12 else now.replace(hour=(now.hour + 12) % 24, day=now.day + 1)
    
    injuries = structured.get("injuries", [])
    if isinstance(injuries, str):
        injuries = [injuries] if injuries else []
    
    has_injuries = len(injuries) > 0 and injuries[0].lower() not in ["none", "no injuries", ""]
    
    ics206 = {
        "form_number": "ICS 206",
        "form_title": "MEDICAL PLAN",
        "block_1_incident_name": incident_name,
        "block_2_operational_period": {
            "date_from": operational_period_start.strftime("%m/%d/%Y"),
            "time_from": operational_period_start.strftime("%H%M"),
            "date_to": operational_period_end.strftime("%m/%d/%Y"),
            "time_to": operational_period_end.strftime("%H%M")
        },
        "block_3_medical_aid_stations": [
            {
                "name": "Primary Aid Station",
                "location": "Incident Staging Area",
                "contact_number_frequency": "TBD",
                "paramedics_on_site": has_injuries
            }
        ],
        "block_4_transportation": [
            {
                "ambulance_service": "Local EMS",
                "location": "TBD",
                "contact_number_frequency": "911 / Local Dispatch",
                "level_of_service": "ALS"
            }
        ],
        "block_5_hospitals": [
            {
                "hospital_name": "Nearest Trauma Center",
                "address_latitude_longitude": "TBD",
                "contact_number_frequency": "TBD",
                "travel_time_air": "TBD",
                "travel_time_ground": "TBD",
                "trauma_center": True,
                "trauma_level": "Level I/II",
                "burn_center": False,
                "helipad": True
            }
        ],
        "block_6_special_medical_emergency_procedures": "For medical emergencies: 1) Contact Medical Unit Leader immediately, 2) Request EMS response via 911, 3) Provide location and nature of emergency, 4) Follow standard medical protocols",
        "block_6_aviation_assets_utilized": False,
        "block_7_prepared_by": {
            "name": "[Name]",
            "position_title": "Medical Unit Leader",
            "signature": "[Signature]",
            "date_time": now.strftime("%m/%d/%Y %H%M")
        },
        "block_8_approved_by": {
            "name": "[Name]",
            "position_title": "Safety Officer",
            "signature": "[Signature]",
            "date_time": now.strftime("%m/%d/%Y %H%M")
        }
    }
    
    return ics206


def generate_all_outputs(final_output: Dict[str, Any], incident_name: str = "Incident", incident_number: str = "001") -> Dict[str, Any]:
    """Generate all structured outputs from final_output."""
    all_outputs = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "incident_name": incident_name,
            "incident_number": incident_number
        },
        "artifacts": {
            "situation_brief": generate_situation_brief(final_output, incident_name),
            "triage_priorities": generate_triage_priorities(final_output),
            "mini_iap": generate_mini_iap(final_output, incident_name),
            "resource_requests": generate_resource_requests(final_output),
            "comms_drafts": generate_comms_drafts(final_output)
        },
        "ics_forms": {
            "ics_201": generate_ics201(final_output, incident_name, incident_number),
            "ics_202": generate_ics202(final_output, incident_name),
            "ics_205": generate_ics205(final_output, incident_name),
            "ics_206": generate_ics206(final_output, incident_name)
        }
    }
    
    return all_outputs


def export_to_json(all_outputs: Dict[str, Any], output_path: Path) -> None:
    """Export all outputs to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_outputs, f, indent=2, ensure_ascii=False)
    print(f"✓ Exported JSON to {output_path}")


def export_to_markdown(all_outputs: Dict[str, Any], output_path: Path) -> None:
    """Export all outputs to Markdown file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    md_lines = []
    
    # Header
    metadata = all_outputs.get("metadata", {})
    md_lines.append(f"# {metadata.get('incident_name', 'Incident')} - Operational Outputs")
    md_lines.append(f"\n**Generated:** {metadata.get('generated_at', 'Unknown')}")
    md_lines.append(f"**Incident Number:** {metadata.get('incident_number', 'N/A')}\n")
    
    # Situation Brief
    md_lines.append("## 1. Situation Brief\n")
    brief = all_outputs.get("artifacts", {}).get("situation_brief", {})
    md_lines.append(f"**Date/Time:** {brief.get('date_time', 'N/A')}\n")
    
    situation = brief.get("situation_summary", {})
    md_lines.append("### Situation Summary")
    md_lines.append(f"- **Hazards:** {', '.join(situation.get('hazards', []))}")
    md_lines.append(f"- **Injuries:** {', '.join(situation.get('injuries_reported', []))}")
    md_lines.append(f"- **Infrastructure:** {', '.join(situation.get('infrastructure_status', []))}")
    md_lines.append(f"- **Weather:** {situation.get('weather_conditions', 'N/A')}\n")
    
    status = brief.get("current_status", {})
    md_lines.append("### Current Status")
    md_lines.append(f"- Objectives: {status.get('objectives_count', 0)}")
    md_lines.append(f"- Tasks: {status.get('tasks_count', 0)}")
    md_lines.append(f"- Time Horizon: {status.get('time_horizon', 'N/A')}")
    md_lines.append(f"- Confidence Score: {status.get('confidence_score', 0.0):.2f}\n")
    
    # Triage + Priorities
    md_lines.append("## 2. Triage + Priorities\n")
    triage = all_outputs.get("artifacts", {}).get("triage_priorities", {})
    
    md_lines.append("### Priority 1 Tasks")
    for task in triage.get("priority_1_tasks", [])[:5]:
        md_lines.append(f"- {task}")
    md_lines.append("")
    
    md_lines.append("### Priority 2 Tasks")
    for task in triage.get("priority_2_tasks", [])[:5]:
        md_lines.append(f"- {task}")
    md_lines.append("")
    
    # Mini-IAP
    md_lines.append("## 3. Mini Incident Action Plan\n")
    iap = all_outputs.get("artifacts", {}).get("mini_iap", {})
    md_lines.append(f"**Operational Period:** {iap.get('operational_period', 'N/A')}\n")
    
    md_lines.append("### Objectives")
    for obj in iap.get("objectives", [])[:5]:
        md_lines.append(f"- {obj}")
    md_lines.append("")
    
    # Resource Requests
    md_lines.append("## 4. Resource Requests\n")
    resources = all_outputs.get("artifacts", {}).get("resource_requests", {})
    md_lines.append(f"**Total Requests:** {resources.get('total_requests', 0)}\n")
    
    for resource in resources.get("resources", [])[:10]:
        md_lines.append(f"- **{resource.get('request_id')}:** {resource.get('resource_type')} ({resource.get('priority')})")
    md_lines.append("")
    
    # Communications
    md_lines.append("## 5. Communications Drafts\n")
    comms = all_outputs.get("artifacts", {}).get("comms_drafts", {})
    
    md_lines.append("### Public Advisory")
    md_lines.append(comms.get("public_advisory", "N/A")[:500])
    md_lines.append("")
    
    md_lines.append("### Key Talking Points")
    for point in comms.get("key_talking_points", [])[:5]:
        md_lines.append(f"- {point}")
    md_lines.append("")
    
    # ICS Forms Summary
    md_lines.append("## 6. ICS Forms Summary\n")
    
    ics201 = all_outputs.get("ics_forms", {}).get("ics_201", {})
    md_lines.append(f"### ICS 201 - Incident Briefing")
    md_lines.append(f"- Incident Name: {ics201.get('block_1_incident_name', 'N/A')}")
    md_lines.append(f"- Incident Number: {ics201.get('block_2_incident_number', 'N/A')}")
    md_lines.append("")
    
    ics202 = all_outputs.get("ics_forms", {}).get("ics_202", {})
    md_lines.append(f"### ICS 202 - Incident Objectives")
    md_lines.append(f"- Objectives: {len(ics202.get('block_3_objectives', '').split(chr(10))) if isinstance(ics202.get('block_3_objectives'), str) else 0} objectives defined")
    md_lines.append("")
    
    ics205 = all_outputs.get("ics_forms", {}).get("ics_205", {})
    md_lines.append(f"### ICS 205 - Radio Communications Plan")
    md_lines.append(f"- Channels: {len(ics205.get('block_4_basic_radio_channel_use', []))} channels configured")
    md_lines.append("")
    
    ics206 = all_outputs.get("ics_forms", {}).get("ics_206", {})
    md_lines.append(f"### ICS 206 - Medical Plan")
    md_lines.append(f"- Medical aid stations: {len(ics206.get('block_3_medical_aid_stations', []))} station(s)")
    md_lines.append("")
    
    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    
    print(f"✓ Exported Markdown to {output_path}")


def generate_from_agent_output(agent_final_state: Dict[str, Any], incident_name: str = "Incident", incident_number: str = "001") -> Dict[str, Any]:
    """Convenience function to generate all outputs from agent pipeline final state."""
    final_output = agent_final_state.get("final_output", agent_final_state)
    return generate_all_outputs(final_output, incident_name, incident_number)


def export_to_pdf(all_outputs: Dict[str, Any], output_path: Path) -> None:
    """Export all outputs to PDF file using markdown conversion."""
    try:
        import markdown
        from weasyprint import HTML
        from pathlib import Path as PathLib
        import tempfile
        
        # First generate markdown to temp file
        temp_md = PathLib(tempfile.gettempdir()) / "disasterops_temp.md"
        export_to_markdown(all_outputs, temp_md)
        
        with open(temp_md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # Create full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #1a1a1a; border-bottom: 3px solid #333; padding-bottom: 10px; }}
                h2 {{ color: #333; margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
                h3 {{ color: #555; margin-top: 20px; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-left: 3px solid #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #333; color: white; }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=full_html).write_pdf(output_path)
        print(f"✓ Exported PDF to {output_path}")
        
    except ImportError:
        # Fallback: just save markdown and inform user
        print("⚠ PDF export requires: pip install markdown weasyprint")
        print(f"   Falling back to Markdown export")
        md_path = output_path.with_suffix('.md')
        export_to_markdown(all_outputs, md_path)
    except Exception as e:
        print(f"⚠ PDF export failed: {e}")
        print(f"   Falling back to Markdown export")
        md_path = output_path.with_suffix('.md')
        export_to_markdown(all_outputs, md_path)

