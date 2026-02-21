# save as pipeline/video_summarizer.py (replace the entire file)
from groq import Groq
import cv2
import base64
import json
import os
import sys
import numpy as np
from datetime import date
from prompts import VIDEO_SUMMARY_PROMPT, build_prompt_with_blueprint

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def extract_frames(video_path, max_frames=20):
    """Extract frames evenly spread across entire video."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_min = total / fps / 60 if fps > 0 else 0

    step = max(1, total // max_frames)
    frames = []

    for i in range(0, total, step):
        if len(frames) >= max_frames:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frames.append({
                "timestamp_min": round(i / fps / 60, 1),
                "b64": base64.b64encode(buf.tobytes()).decode()
            })

    cap.release()
    print(f"  Extracted {len(frames)} frames from {duration_min:.1f} min video")
    return frames, duration_min


def stitch_grid(frames, cols=2, rows=2):
    """Pack 4 frames into 1 grid image. Turns 20 frames into 5 images."""
    grids = []
    per_grid = cols * rows

    for i in range(0, len(frames), per_grid):
        batch = frames[i:i + per_grid]

        # Decode frames
        imgs = []
        for f in batch:
            raw = base64.b64decode(f["b64"])
            arr = np.frombuffer(raw, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            img = cv2.resize(img, (640, 360))
            imgs.append(img)

        # Pad if less than 4
        while len(imgs) < per_grid:
            imgs.append(np.zeros_like(imgs[0]))

        # Stitch: 2x2 grid
        top = np.hstack(imgs[:cols])
        bottom = np.hstack(imgs[cols:per_grid])
        grid = np.vstack([top, bottom])

        _, buf = cv2.imencode('.jpg', grid, [cv2.IMWRITE_JPEG_QUALITY, 85])
        timestamps = [f["timestamp_min"] for f in batch]
        grids.append({
            "b64": base64.b64encode(buf.tobytes()).decode(),
            "timestamps": timestamps
        })

    return grids


def call_vlm(frames, prompt):
    """Pack frames into grids and send to Groq (max 5 images)."""
    grids = stitch_grid(frames)
    print(f"  Packed {len(frames)} frames into {len(grids)} grid images")

    content = []
    for i, g in enumerate(grids):
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{g['b64']}"}
        })
        ts = ", ".join([f"{t} min" for t in g["timestamps"]])
        content.append({
            "type": "text",
            "text": f"[Grid {i+1}/{len(grids)} — frames at {ts}]"
        })

    content.append({
        "type": "text",
        "text": prompt + "\n\nEach grid image contains 4 frames (2x2). Analyze ALL frames across ALL grids. Return ONLY the JSON:"
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
        max_tokens=4096
    )

    raw_text = response.choices[0].message.content.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        raw_text = raw_text.rsplit("```", 1)[0]

    return json.loads(raw_text)


def summarize_video(video_path, blueprint_path=None):
    """Main entry point. Video -> structured JSON summary."""
    blueprint = None
    if blueprint_path:
        with open(blueprint_path) as f:
            blueprint = json.load(f)
        prompt = build_prompt_with_blueprint(blueprint)
    else:
        prompt = VIDEO_SUMMARY_PROMPT

    print("  Extracting frames...")
    frames, duration_min = extract_frames(video_path, max_frames=20)

    print(f"  Sending to Groq...")
    raw = call_vlm(frames, prompt)

    return {
        "project_name": blueprint["project_name"] if blueprint else "Unknown",
        "date": str(date.today()),
        "video_duration_minutes": round(duration_min, 1),
        "summary": raw
    }


if __name__ == "__main__":
    video_path = sys.argv[1]
    bp_path = sys.argv[2] if len(sys.argv) > 2 else None
    out_path = sys.argv[3] if len(sys.argv) > 3 else "data/output/video_summary.json"

    print("🎬 Ironsite Video Summarizer (Groq)")
    print("=" * 40)

    result = summarize_video(video_path, bp_path)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Saved to {out_path}")
    print(f"Tasks: {len(result['summary'].get('tasks_observed', []))}")
    print(f"Materials: {len(result['summary'].get('materials_observed_in_use', []))}")
    print(f"Crew: {result['summary'].get('crew_size_observed', 'N/A')}")
    print(f"\n{json.dumps(result, indent=2)}")