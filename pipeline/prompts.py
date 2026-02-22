# save as pipeline/prompts.py

VIDEO_SUMMARY_PROMPT = """You are a construction site analyst reviewing first-person hardhat camera footage.

You will see frames extracted at regular intervals from a construction site video.

Produce a structured JSON summary of ALL work observed across the frames.

Return ONLY valid JSON, no markdown backticks, no explanation. Exact structure:
{
  "overall_narrative": "2-3 sentence summary of work done",
  "tasks_observed": [
    {
      "task": "task name (use blueprint step names if provided)",
      "status": "completed | in_progress | not_started",
      "percent_complete": 0-100,
      "confidence": 0.0-1.0,
      "time_spent_estimate_hours": 0.0,
      "observations": "specific details of what you observed"
    }
  ],
  "materials_observed_in_use": [
    { "name": "material name", "estimated_quantity_used": 0 }
  ],
  "issues_or_blockers": ["any problems, delays, idle time"],
  "weather_conditions": "describe if visible",
  "crew_size_observed": 0
}

RULES:
- Count materials when visible (blocks placed, mortar bags used)
- Distinguish active work from travel, breaks, waiting
- Confidence below 0.7 if view is obstructed or brief
- Track changes across frames — early frames may show different work than later frames
- Return ONLY the JSON object, nothing else"""


def build_prompt_with_blueprint(blueprint: dict) -> str:
    step_list = ""
    for step in blueprint["steps"]:
        indicators = ", ".join(step.get("completion_indicators", [])[:2])
        step_list += f"  Step {step['step_id']}: {step['name']}\n"
        step_list += f"    Look for: {indicators}\n"

    return VIDEO_SUMMARY_PROMPT + f"""

PROJECT: {blueprint['project_name']}
Expected steps:
{step_list}
Map observations to these exact step names when possible."""