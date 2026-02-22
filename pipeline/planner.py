
from groq import Groq
import json
import os
import sys
from datetime import date, timedelta
from planner_prompts import PLANNER_PROMPT

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"  # better reasoning than scout for planning


def generate_plan(blueprint_path, summary_path):
    """Take blueprint + video summary, produce next-day plan."""
    with open(blueprint_path) as f:
        blueprint = json.load(f)
    with open(summary_path) as f:
        summary = json.load(f)

    prompt = f"""{PLANNER_PROMPT}

--- PROJECT BLUEPRINT ---
{json.dumps(blueprint, indent=2)}

--- TODAY'S WORK SUMMARY ---
{json.dumps(summary, indent=2)}

Today's date is {date.today().isoformat()}.
Analyze the progress and generate the next-day plan. Return ONLY the JSON:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096
    )

    raw_text = response.choices[0].message.content.strip()

    # Clean markdown backticks if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        raw_text = raw_text.rsplit("```", 1)[0]

    prediction = json.loads(raw_text)
    prediction["generated_at"] = f"{date.today().isoformat()}T18:00:00Z"

    return prediction


def generate_forecast(blueprint_path, summary_path, days=5):
    """Generate multi-day forecast for remaining project."""
    with open(blueprint_path) as f:
        blueprint = json.load(f)
    with open(summary_path) as f:
        summary = json.load(f)

    prompt = f"""Based on the blueprint and today's progress, generate a {days}-day forecast.
For each day, predict which tasks will be worked on and what materials are needed.
Assume an 8-hour work day and the same crew size as observed today.

--- PROJECT BLUEPRINT ---
{json.dumps(blueprint, indent=2)}

--- TODAY'S WORK SUMMARY ---
{json.dumps(summary, indent=2)}

Today's date is {date.today().isoformat()}.

Return ONLY valid JSON, no markdown backticks:
{{
  "forecast": [
    {{
      "day": 1,
      "date": "YYYY-MM-DD",
      "tasks": ["task descriptions"],
      "materials_needed": [{{"name": "x", "quantity": 0, "unit": "y"}}],
      "expected_progress_percent": 0
    }}
  ],
  "total_materials_remaining": [{{"name": "x", "total_quantity": 0, "unit": "y"}}],
  "projected_completion": "YYYY-MM-DD"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096
    )

    raw_text = response.choices[0].message.content.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        raw_text = raw_text.rsplit("```", 1)[0]

    return json.loads(raw_text)


def fix_material_names(prediction, blueprint):
    """Map LLM's material names to exact blueprint names."""
    # Build lookup of blueprint materials (lowercase → exact name)
    bp_materials = {}
    for step in blueprint["steps"]:
        for mat in step.get("materials", []):
            # Store multiple lookup keys for each material
            exact = mat["name"]
            lower = exact.lower()
            bp_materials[lower] = exact
            # Add simplified keys: "CMU blocks (8x8x16)" → "cmu blocks", "blocks"
            for word in lower.replace("(", "").replace(")", "").split():
                bp_materials[word] = exact

    # Common aliases
    aliases = {
        "concrete_blocks": "blocks",
        "concrete blocks": "blocks",
        "mortar_bags": "mortar",
        "mortar bags": "mortar",
        "mortar": "mortar",
        "blocks": "blocks",
        "rebar": "rebar",
        "grout": "grout",
        "water": "water",
    }

    materials = prediction.get("next_day_plan", {}).get("materials_needed_tomorrow", [])
    for mat in materials:
        name = mat["name"].lower()
        # Direct match
        if name in bp_materials:
            mat["name"] = bp_materials[name]
            continue
        # Alias match
        if name in aliases:
            key = aliases[name]
            if key in bp_materials:
                mat["name"] = bp_materials[key]
                continue
        # Partial match — find blueprint material containing any word from LLM name
        for word in name.replace("_", " ").split():
            if len(word) < 3:
                continue
            for bp_key, bp_exact in bp_materials.items():
                if word in bp_key:
                    mat["name"] = bp_exact
                    break

    return prediction


def validate_plan(prediction, blueprint):
    """Check prediction for obvious errors."""
    warnings = []

    progress = prediction.get("current_progress", {})
    plan = prediction.get("next_day_plan", {})
    all_step_ids = [s["step_id"] for s in blueprint["steps"]]

    # Check step IDs are valid
    for sid in progress.get("completed_steps", []):
        if sid not in all_step_ids:
            warnings.append(f"Completed step {sid} not in blueprint")

    for ip in progress.get("in_progress_steps", []):
        if ip["step_id"] not in all_step_ids:
            warnings.append(f"In-progress step {ip['step_id']} not in blueprint")

    # Check overall progress is reasonable
    pct = progress.get("overall_percent_complete", 0)
    if pct < 0 or pct > 100:
        warnings.append(f"Overall progress {pct}% is out of range")

    # Check tomorrow's tasks have valid step IDs
    for task in plan.get("priority_tasks", []):
        if task.get("step_id") not in all_step_ids:
            warnings.append(f"Planned task step {task.get('step_id')} not in blueprint")

    # Check materials exist in blueprint
    bp_materials = set()
    for step in blueprint["steps"]:
        for mat in step.get("materials", []):
            bp_materials.add(mat["name"].lower())

    for mat in plan.get("materials_needed_tomorrow", []):
        if mat["name"].lower() not in bp_materials:
            warnings.append(f"Material '{mat['name']}' not found in blueprint")

    return warnings


if __name__ == "__main__":
    blueprint_path = sys.argv[1]
    summary_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else "data/output/prediction.json"
    do_forecast = "--forecast" in sys.argv

    print("🧠 Ironsite Planner (Groq)")
    print("=" * 40)

    # Generate next-day plan
    print("  Generating next-day plan...")
    plan = generate_plan(blueprint_path, summary_path)

    # Fix material names to match blueprint exactly
    with open(blueprint_path) as f:
        bp = json.load(f)
    plan = fix_material_names(plan, bp)

    # Validate
    warnings = validate_plan(plan, bp)
    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings:")
        for w in warnings:
            print(f"   - {w}")
    else:
        print("  ✅ Plan validated")

    # Save
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(plan, f, indent=2)

    progress = plan["current_progress"]
    next_tasks = plan["next_day_plan"]["priority_tasks"]
    materials = plan["next_day_plan"]["materials_needed_tomorrow"]

    print(f"\n✅ Saved to {out_path}")
    print(f"   Progress: {progress['overall_percent_complete']}%")
    print(f"   Schedule: {progress['ahead_or_behind_schedule']}")
    print(f"   Tomorrow's tasks: {len(next_tasks)}")
    print(f"   Materials needed: {len(materials)} items")
    print(f"\n{json.dumps(plan, indent=2)}")

    # Optional forecast
    if do_forecast:
        print("\n📈 Generating 5-day forecast...")
        forecast = generate_forecast(blueprint_path, summary_path)
        forecast_path = out_path.replace("prediction", "forecast")
        with open(forecast_path, "w") as f:
            json.dump(forecast, f, indent=2)
        print(f"  ✅ Forecast saved to {forecast_path}")
        print(json.dumps(forecast, indent=2))