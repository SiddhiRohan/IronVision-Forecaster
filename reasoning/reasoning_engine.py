import json
from typing import Dict


def load_json(filepath: str) -> Dict:
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found -> {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format -> {filepath}")
        return {}


def save_json(data: Dict, filepath: str):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")


def generate_materials_text(materials: Dict) -> str:
    if not materials:
        return "No materials data available."

    material_list = []
    for key, value in materials.items():
        formatted_key = key.replace("_", " ").capitalize()
        material_list.append(f"{value} units of {formatted_key}")

    return ", ".join(material_list)


def estimate_material_cost(materials: Dict) -> float:
    """
    Simple mock cost estimator.
    Assumes average $50 per unit (hackathon simulation).
    """
    if not materials:
        return 0.0

    return round(sum(materials.values()) * 50, 2)


def generate_summary(detected_stage: str, next_stage: str, materials: Dict) -> str:
    materials_text = generate_materials_text(materials)

    return (
        f"The current construction stage is identified as '{detected_stage}'. "
        f"Based on the structured project blueprint, the next logical step is '{next_stage}'. "
        f"To proceed efficiently, the following materials will be required: {materials_text}."
    )


def generate_confidence_explanation(confidence: float) -> str:
    confidence_percent = round(confidence * 100, 2)

    if confidence >= 0.8:
        return (
            f"The model shows high confidence ({confidence_percent}%) "
            "based on strong visual indicators of stage completion."
        )
    elif confidence >= 0.6:
        return (
            f"The model shows moderate confidence ({confidence_percent}%). "
            "Some visual signals suggest partial completion."
        )
    else:
        return (
            f"The model shows low confidence ({confidence_percent}%). "
            "Visual ambiguity may exist, requiring manual verification."
        )


def generate_risk_flag(confidence: float) -> str:
    """
    Risk indicator based on confidence score.
    """
    if confidence >= 0.8:
        return "Low Risk"
    elif confidence >= 0.6:
        return "Medium Risk - Monitor Progress"
    else:
        return "High Risk - Manual Verification Recommended"


def generate_business_impact(next_stage: str, estimated_cost: float) -> str:
    return (
        f"By proactively preparing materials for '{next_stage}', "
        f"the system can reduce idle labor time and prevent supply shortages. "
        f"Estimated material preparation cost for next stage: ${estimated_cost}."
    )


def reasoning_pipeline(stage_file: str, prediction_file: str) -> Dict:
    stage_data = load_json(stage_file)
    prediction_data = load_json(prediction_file)

    detected_stage = prediction_data.get("current_stage", "Unknown Stage")
    next_stage = prediction_data.get("next_stage", "Unknown Next Stage")
    materials = prediction_data.get("materials_required", {})

    try:
        confidence = float(stage_data.get("confidence", 0.0))
    except (ValueError, TypeError):
        confidence = 0.0

    estimated_cost = estimate_material_cost(materials)
    risk_flag = generate_risk_flag(confidence)

    summary = generate_summary(detected_stage, next_stage, materials)
    confidence_explanation = generate_confidence_explanation(confidence)
    business_impact = generate_business_impact(next_stage, estimated_cost)

    final_output = {
        "summary": summary,
        "confidence_explanation": confidence_explanation,
        "risk_flag": risk_flag,
        "estimated_material_cost": estimated_cost,
        "business_impact": business_impact
    }

    return final_output


if __name__ == "__main__":
    stage_file = "data/stage_detection.json"
    prediction_file = "data/prediction_output.json"
    output_path = "data/final_reasoning.json"

    result = reasoning_pipeline(stage_file, prediction_file)
    save_json(result, output_path)

    print(" Reasoning successfully saved to data/final_reasoning.json")