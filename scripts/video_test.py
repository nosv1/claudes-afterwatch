"""Throwaway 3-video test: can Gemini actually watch a YouTube video from its link?

Reads the key from the GEMINI_API_KEY environment variable. Writes one Markdown report plus the
raw API responses to scripts/out/ (git-ignored).

Usage: python scripts/video_test.py [model] [video numbers...] [--fps N] [--low]
  e.g. python scripts/video_test.py gemini-3.5-flash 1 3 --fps 0.2 --low
  --fps N  frames per second Gemini samples (default 1; audio is always used in full)
  --low    low media resolution per frame (fewer tokens)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ARGS = sys.argv[1:]
LOW = "--low" in ARGS
FPS = None
if "--fps" in ARGS:
    FPS = float(ARGS[ARGS.index("--fps") + 1])
    del ARGS[ARGS.index("--fps") : ARGS.index("--fps") + 2]
ARGS = [a for a in ARGS if a != "--low"]

MODEL = ARGS[0] if ARGS else "gemini-3.8-flash"
API = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

VIDEOS = [
    "https://www.youtube.com/watch?v=KfODG5REyss",
    "https://www.youtube.com/watch?v=u5xPCoh8_aM",
    "https://www.youtube.com/watch?v=rX0RuKswLAo",
]
PICK = [int(a) for a in ARGS[1:]] or list(range(1, len(VIDEOS) + 1))
RETRY_WAITS = [15, 30, 60]  # seconds to wait before each retry on a 503

PROMPT = """Watch this video and answer from what is actually shown and said in it.
If you cannot access the video's content, say so plainly instead of guessing.

## Video
The title and the channel, as shown.

## Summary with timestamps
A short summary, then 8-15 bullet points, each starting with an [mm:ss] timestamp of where that
part happens in the video.

## Key topics
Two lists of the ideas a viewer should come away understanding:
- **Beginner level:** for someone new to the subject.
- **Some background:** for someone who already knows the basics.

## Conversation
A natural, open opening question asking the viewer what they learned from this video, then three
follow-up questions that probe whether they really understood the key topics above.
"""

OUT = Path(__file__).parent / "out"


def ask_with_retry(key: str, url: str) -> tuple[dict | None, str | None, float, int]:
    """Retries only on 503 (overloaded). Returns (data, error, seconds of last try, tries)."""
    for attempt, wait in enumerate([0] + RETRY_WAITS, 1):
        if wait:
            print(f"    503, retrying in {wait}s ...", flush=True)
            time.sleep(wait)
        data, err, secs = ask(key, url)
        if not (err and err.startswith("HTTP 503")):
            break
    return data, err, secs, attempt


def ask(key: str, url: str) -> tuple[dict | None, str | None, float]:
    video = {"file_data": {"file_uri": url}}
    if FPS:
        video["video_metadata"] = {"fps": FPS}
    body = {"contents": [{"parts": [video, {"text": PROMPT}]}]}
    if LOW:
        body["generationConfig"] = {"mediaResolution": "MEDIA_RESOLUTION_LOW"}
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.load(resp), None, time.monotonic() - start
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode(errors='replace')}", time.monotonic() - start
    except Exception as e:  # network errors, timeouts
        return None, f"{type(e).__name__}: {e}", time.monotonic() - start


def main() -> None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set.")
    OUT.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    settings = f"fps {FPS or 'default (1)'}, resolution {'low' if LOW else 'default'}"
    lines = [f"# 3-video test: {MODEL}", "",
             f"Run {datetime.now():%Y-%m-%d %H:%M}. Settings: {settings}.", ""]

    for i, url in enumerate(VIDEOS, 1):
        if i not in PICK:
            continue
        print(f"[{i}/{len(VIDEOS)}] {url} ...", flush=True)
        data, err, secs, tries = ask_with_retry(key, url)
        (OUT / f"{stamp}_video{i}.json").write_text(
            json.dumps(data if data else {"error": err}, indent=2), encoding="utf-8"
        )
        lines += ["---", "", f"# Video {i}: {url}", ""]
        if tries > 1:
            lines += [f"_(Try {tries} of {len(RETRY_WAITS) + 1}; the ones before got 503s.)_", ""]
        if err:
            print(f"    FAILED after {secs:.0f}s: {err[:300]}", flush=True)
            lines += [f"**Failed** after {secs:.0f}s.", "", "```", err, "```", ""]
            continue
        usage = data.get("usageMetadata", {})
        text = "".join(
            p.get("text", "")
            for c in data.get("candidates", [])[:1]
            for p in c.get("content", {}).get("parts", [])
        )
        details = ", ".join(
            f"{d.get('modality')}: {d.get('tokenCount')}"
            for d in usage.get("promptTokensDetails", [])
        )
        print(f"    ok in {secs:.0f}s, tokens in/out/total "
              f"{usage.get('promptTokenCount')}/{usage.get('candidatesTokenCount')}/"
              f"{usage.get('totalTokenCount')}", flush=True)
        lines += [
            f"**Worked** in {secs:.0f}s. Tokens: prompt {usage.get('promptTokenCount')} "
            f"({details}), output {usage.get('candidatesTokenCount')}, "
            f"total {usage.get('totalTokenCount')}.",
            "",
            text or "_(empty response)_",
            "",
        ]

    report = OUT / f"{stamp}_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
