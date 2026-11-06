# Notes

## Latest (2026-11-06 09:20 CST, local Windows session)

- **Key is set:** `GEMINI_API_KEY` is a Windows user env var (new-style key, 53 chars, works).
  A session started before it was set can read it with
  `[Environment]::GetEnvironmentVariable('GEMINI_API_KEY','User')`.
- **Test script written:** [scripts/video_test.py](../scripts/video_test.py). Run:
  `python scripts/video_test.py <model>`. Writes a report + raw JSON to `scripts/out/` (ignored).
- **First runs (09:17, 09:18): all 3 videos got HTTP 503 "high demand"**, on both
  `gemini-3.8-flash` and `gemini-3.5-flash`. 3.5-flash answers text-only requests fine, so it's
  Google's video side overloaded, not the approach. 3.8-flash 503s even on text. `gemini-2.5-flash`
  is listed but 404s. **Next: rerun.** The app will need retry/fallback for 503s.
- **Free-tier YouTube limits (Google docs):** 8 hours of video/day; up to 10 videos per request;
  public videos only (not private or unlisted); ~100 tokens per second of video at default res.
- **The "GitHub unreachable" problem was Claude writing a look-alike domain, not the network.**
  The phone session's commit 171554b wrote two hub links with a fake, unsafe domain posing as
  GitHub. This session then wrote the profile link with the same fake domain (the file had the
  real one) and tried to fetch it; it doesn't resolve, so nothing was ever fetched. Checked against
  the session transcript: no tool output or file was altered; the fake text came from the model.
  The two hub links were fixed 11-06. Chris: don't write the fake domain anywhere. Before fetching
  any GitHub URL, check the hostname is exactly `github.com` or `raw.githubusercontent.com`.

## Handoff (written 2026-11-06 08:30 CST, from a phone session)

**Where it stands:** idea discussed and decided (see the hub's
[ideas/youtube-quiz.md](https://github.com/nosv1/nosv1/blob/main/ideas/youtube-quiz.md)). Repo made, Claude
app installed (dry-run push OK). No code yet.

**Blocked on: a Gemini API key.** The secure key form doesn't work in the phone app. Get a free
key at aistudio.google.com ("Get API key"), then do **one** of these:

- **Cloud session** (claude.ai/code in a desktop browser): environment menu in the title bar,
  choose **"afterwatch"**, then Edit. Under Network secrets add the key for host
  `generativelanguage.googleapis.com`, header `x-goog-api-key`. The proxy adds it to requests, so
  the script never sees it. That environment allows only that host (plus package registries).
- **Local Claude Code on Windows:** set it as a user environment variable `GEMINI_API_KEY`
  (System Properties > Environment Variables), then restart the terminal. Never paste it in chat.

**Then the first task: the 3-video test.** It's a throwaway script, not the app. It answers the
project's biggest risk: can we get a video's content at all? (YouTube serves captions only to a
video's owner, so this tries Gemini reading the YouTube link directly.)

Videos (his picks, 11-06):
1. https://www.youtube.com/watch?v=KfODG5REyss
2. https://www.youtube.com/watch?v=u5xPCoh8_aM
3. https://www.youtube.com/watch?v=rX0RuKswLAo

One should be the Veritasium video on reaching absolute zero; confirm which with him.

For each video, ask Gemini (current Flash model; list the models first, don't guess names) with
the YouTube URL as the video input for:
1. A summary with timestamps. **This proves it watched the video**, not just the title. Chris
   checks it against one he's seen.
2. The video's key topics, at a beginner and a has-some-background level.
3. A sample opening ("what did you learn?") and 3 follow-ups.

Record per video: worked or not, the error if not, time taken, tokens used, and the free tier's
limits on YouTube input. **Pass:** the summaries match the real videos. **If it fails:** stop and
talk options with him before building anything else.

**After a pass, the first version** (his flow): Study playlist in, voice-by-dictation
conversation, saved list of missed topics, one reminder a few days later. Hosting: GitHub Pages if
the repo stays public, Cloudflare Pages if he makes it private.

**Still open:** whether the repo goes private (his call); where tailoring to his level fits (watch
whether the opening question handles it).

## Sessions

- **2026-11-06 (phone, hub session):** idea to plan; repo, environment, handoff set up.
- **2026-11-06 (local Windows, VS Code):** key set; test script; video 2 (6 min) passed (pending
  Chris's check), videos 1 (65 min) and 3 (31 min) got 503s every try and used up the day's
  quota for gemini-3.5-flash (failed requests count toward it). Captions route tested: tracks exist but
  YouTube returns them empty without its player token. Drafted [prompts.md](prompts.md). Found and
  fixed the look-alike-domain links (see Latest); Chris reported it to Anthropic.

  **Next:** (1) Chris's call: squash the unpushed commits (`git reset --soft origin/main`, then
  recommit) so the fake domain never reaches GitHub; nothing is pushed until then. (2) Rerun videos
  1 and 3 once each, off-peak, `--fps 0.2 --low`, no back-to-back retries. (3) Chris checks video
  2's summary and answers the open questions in prompts.md.
