import json
import os
import sys
from openai import OpenAI

# =========================
# CONFIG
# =========================
MODEL = "gpt-4o-mini"   # cepat & cukup untuk semantic judgment
MAX_CLIPS = 5

# =========================
# VALIDATION
# =========================
if len(sys.argv) < 2:
    print("❌ Usage: python chatgpt_highlight.py segments.json")
    sys.exit(1)

SEGMENTS_FILE = sys.argv[1]
OUTPUT_FILE = "highlights.json"

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY not set")

client = OpenAI(api_key=api_key)

# =========================
# LOAD SEGMENTS
# =========================
with open(SEGMENTS_FILE, "r", encoding="utf-8") as f:
    segments = json.load(f)

if not isinstance(segments, list) or len(segments) == 0:
    print("⚠️ segments.json kosong")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)
    sys.exit(0)

# =========================
# BUILD PROMPT
# =========================
system_prompt = (
    "Kamu adalah editor profesional untuk konten video pendek "
    "(TikTok, Reels, Shorts)."
)

user_prompt = f"""
Aku akan memberimu daftar SEGMENTS hasil transkrip video.
Setiap segment memiliki:
- start (detik)
- end (detik)
- duration
- text

TUGASMU:
1. Pilih MAKSIMAL {MAX_CLIPS} bagian TERBAIK dari keseluruhan segmen.
2. Setiap klip harus berdurasi antara 60 sampai 180 detik.
3. Klip HARUS bisa berdiri sendiri (tidak butuh konteks panjang).
4. Prioritaskan insight, refleksi, emosi, kontras, atau punchline.
5. Hindari pembukaan basa-basi dan penutup formal.
6. Jika perlu, gabungkan beberapa segmen BERURUTAN selama satu topik.

OUTPUT:
Kembalikan JSON VALID SAJA, format:

[
  {{
    "start": <number>,
    "end": <number>,
    "duration": <number>,
    "reason": "<alasan singkat>",
    "category": ["insight","emotion","reflection","contrast"]
  }}
]

CATATAN:
- Jangan mengarang timestamp.
- Gunakan start segmen pertama dan end segmen terakhir jika digabung.
- Jika tidak ada klip layak, kembalikan [].

SEGMENTS:
{json.dumps(segments, ensure_ascii=False)}
"""

# =========================
# CALL CHATGPT
# =========================
print("🤖 Requesting ChatGPT for highlight detection...")

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    temperature=0.2
)

content = resp.choices[0].message.content.strip()

# =========================
# PARSE & SAVE
# =========================
try:
    highlights = json.loads(content)
except json.JSONDecodeError:
    print("❌ ChatGPT output bukan JSON valid:")
    print(content)
    sys.exit(1)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(highlights, f, ensure_ascii=False, indent=2)

print(f"✅ Highlight detection selesai: {len(highlights)} clip(s)")
print(f"📄 Output: {OUTPUT_FILE}")
