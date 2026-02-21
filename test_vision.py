# save as test_vision.py
from groq import Groq
import cv2
import base64
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])
VIDEO_PATH = "data/sample_videos/masonry.mp4"  # ← your video

# Extract 3 frames (start, middle, end)
cap = cv2.VideoCapture(VIDEO_PATH)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frames_b64 = []

for pos in [0, total // 2, total - 100]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    ret, frame = cap.read()
    if ret:
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frames_b64.append(base64.b64encode(buf.tobytes()).decode())
cap.release()

print(f"Extracted {len(frames_b64)} frames")

# Send to Groq with vision
content = []
for i, b64 in enumerate(frames_b64):
    content.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
    })
    content.append({"type": "text", "text": f"[Frame {i+1} of {len(frames_b64)}]"})

content.append({"type": "text", "text": "What construction work do you see across these frames? 3 sentences."})

response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[{"role": "user", "content": content}]
)
print(response.choices[0].message.content)