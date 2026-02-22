#!/usr/bin/env python3
"""End-to-end pipeline: Video → VLM Summary → LLM Plan → Dashboard-ready JSON"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add pipeline directory to path
sys.path.insert(0, str(Path(__file__).parent))

from video_summarizer import summarize_video
from planner import generate_plan, generate_forecast


def run_pipeline(video_path, blueprint_path, output_dir="data/output", forecast_days=0):
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("⚡ IRONSITE — FULL PIPELINE")
    print("=" * 60)

    # ─── Stage 1: Video → Summary ───
    print("\n📹 Stage 1: Analyzing video with VLM...")
    start = time.time()

    summary = summarize_video(video_path, blueprint_path)
    summary_path = os.path.join(output_dir, "video_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    t1 = time.time() - start
    print(f"   ✅ Summary generated in {t1:.1f}s")
    print(f"   📄 Saved to {summary_path}")

    # ─── Stage 2: Summary + Blueprint → Plan ───
    print("\n🧠 Stage 2: Generating next-day plan...")
    start = time.time()

    prediction = generate_plan(blueprint_path, summary_path)
    prediction_path = os.path.join(output_dir, "prediction.json")
    with open(prediction_path, "w") as f:
        json.dump(prediction, f, indent=2)

    t2 = time.time() - start
    print(f"   ✅ Plan generated in {t2:.1f}s")
    print(f"   📄 Saved to {prediction_path}")

    # ─── Optional: Forecast ───
    if forecast_days > 0:
        print(f"\n📈 Stage 3: Generating {forecast_days}-day forecast...")
        start = time.time()

        forecast = generate_forecast(blueprint_path, summary_path, forecast_days)
        forecast_path = os.path.join(output_dir, "forecast.json")
        with open(forecast_path, "w") as f:
            json.dump(forecast, f, indent=2)

        t3 = time.time() - start
        print(f"   ✅ Forecast generated in {t3:.1f}s")
        print(f"   📄 Saved to {forecast_path}")

    # ─── Results ───
    progress = prediction["current_progress"]
    plan = prediction["next_day_plan"]

    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print(f"   Progress:        {progress['overall_percent_complete']}%")
    print(f"   Schedule:        {progress['ahead_or_behind_schedule']}")
    print(f"   Tomorrow tasks:  {len(plan['priority_tasks'])}")
    print(f"   Materials needed: {len(plan['materials_needed_tomorrow'])} items")
    print(f"   Total time:      {t1 + t2:.1f}s")
    print("=" * 60)
    print(f"\n🖥️  Launch dashboard:")
    print(f"   python -m streamlit run dashboard/dashboard.py")

    return summary, prediction


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ironsite Full Pipeline")
    parser.add_argument("video", help="Path to construction site video")
    parser.add_argument("--blueprint", "-b", default="blueprint.json", help="Path to blueprint JSON")
    parser.add_argument("--output", "-o", default="data/output", help="Output directory")
    parser.add_argument("--forecast", type=int, default=0, help="Generate N-day forecast")

    args = parser.parse_args()
    run_pipeline(args.video, args.blueprint, args.output, args.forecast)