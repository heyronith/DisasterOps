"""
DisasterOps Demo Script
Step 7: Showcase Scenarios

Runs predefined demo scenarios to showcase system capabilities.
"""

import json
from pathlib import Path
from datetime import datetime

from agents import run_pipeline
from output_generation import generate_from_agent_output, export_to_json, export_to_markdown


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
# Demo Runner
# ============================================================================

def run_demo_scenario(scenario: dict, output_dir: Path):
    """Run a single demo scenario and save outputs."""
    print(f"\n{'='*80}")
    print(f"Running Demo: {scenario['name']}")
    print(f"{'='*80}")
    print(f"Incident: {scenario['incident_name']} ({scenario['incident_number']})")
    print(f"Description: {scenario['description'][:100]}...")
    print()
    
    try:
        # Run pipeline
        print("Running 5-agent pipeline...")
        result = run_pipeline(scenario["description"])
        
        # Generate structured outputs
        print("Generating structured outputs...")
        all_outputs = generate_from_agent_output(
            result,
            scenario["incident_name"],
            scenario["incident_number"]
        )
        
        # Save outputs
        scenario_slug = scenario["name"].lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON export
        json_path = output_dir / f"{scenario_slug}_{timestamp}.json"
        export_to_json(all_outputs, json_path)
        print(f"✓ Saved JSON: {json_path}")
        
        # Markdown export
        md_path = output_dir / f"{scenario_slug}_{timestamp}.md"
        export_to_markdown(all_outputs, md_path)
        print(f"✓ Saved Markdown: {md_path}")
        
        # Print summary
        print("\n📊 Summary:")
        verification = result.get("final_output", {}).get("verification", {})
        print(f"  Confidence Score: {verification.get('confidence_score', 0):.2f}")
        print(f"  Citation Coverage: {verification.get('citation_coverage', 'unknown')}")
        print(f"  Evidence Chunks: {len(result.get('evidence', []))}")
        
        return {
            "scenario": scenario["name"],
            "success": True,
            "json_path": json_path,
            "md_path": md_path,
            "verification": verification
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "scenario": scenario["name"],
            "success": False,
            "error": str(e)
        }


def run_all_demos():
    """Run all demo scenarios."""
    print("\n" + "="*80)
    print("DisasterOps Demo - Showcase Scenarios")
    print("="*80)
    
    # Create output directory
    output_dir = Path("demo_outputs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nOutput directory: {output_dir.absolute()}")
    print(f"Scenarios to run: {len(DEMO_SCENARIOS)}\n")
    
    results = []
    
    for scenario in DEMO_SCENARIOS:
        result = run_demo_scenario(scenario, output_dir)
        results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("Demo Summary")
    print("="*80)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\n✓ Successful: {len(successful)}/{len(results)}")
    print(f"✗ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\n📁 Output Files:")
        for result in successful:
            print(f"  - {result['scenario']}:")
            print(f"    JSON: {result['json_path'].name}")
            print(f"    MD: {result['md_path'].name}")
    
    if failed:
        print("\n❌ Failed Scenarios:")
        for result in failed:
            print(f"  - {result['scenario']}: {result.get('error', 'Unknown error')}")
    
    # Save summary
    summary_path = output_dir / f"demo_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(DEMO_SCENARIOS),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f, indent=2)
    
    print(f"\n✓ Summary saved: {summary_path}")
    print("\n" + "="*80)
    print("Demo Complete!")
    print("="*80)


if __name__ == "__main__":
    run_all_demos()

