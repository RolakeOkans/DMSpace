# DMSpace 🟣
A culturally-informed space for mental wellness: anonymous chat reflections, personalized journaling, peer connection, and wellness mini-games.

## What it does
DMSpace helps users express emotions safely and privately, then supports reflection in three ways:
- **💭 Chat**: an empathetic AI reflection space with a basic crisis guardrail
- **📔 Journal**: personalized journaling prompts + a structured journal feed (mood + highlights)
- **🤝 Connect**: opt-in peer matching based on conversation themes (prototype/demo)
- **🎮 Wellness Games**: quick, calming activities (Word Detective, Gratitude Jar, Breathing Exercise)

## Key features
### 1) Culturally-informed reflections
Users choose a “Perspective” (Western, Collectivist, Spiritual, Balanced).  
This lens adjusts the assistant’s reflection style and journaling prompts.

### 2) Safety guardrail (basic)
A simple keyword-based check detects crisis-like language and shows a non-AI crisis response instead of calling the model.

> Note: This is not a clinical tool and does not replace professional support.

### 3) Journaling that builds self-awareness
- AI-generated prompts based on the **themes in recent chat**
- Mood emoji + “one thing to remember” highlight
- Private journal entries saved in-session and displayed as a feed

### 4) Wellness games
- **Word Detective**: unscramble wellness words
- **Gratitude Jar**: daily gratitude log + streak tracking
- **Breathing Exercise**: guided animated breathing patterns (4-7-8, 5-5-5, box)

### 5) Peer matching (prototype)
Opt-in matching uses lightweight theme extraction from user messages to suggest peers with similar topics/stage.

---

## Architecture

### High-level flow
```text
User
  |
  v
Streamlit UI (tabs)
  ├── Chat Tab
  |     ├── Crisis keyword check
  |     ├── Cultural lens added to SYSTEM_PROMPT
  |     └── OpenAI Chat Completions (stream=True) → assistant reply
  |
  ├── Journal Tab
  |     ├── Generates prompts from last ~5 emotion_log entries (OpenAI)
  |     └── Saves journal entries (mood + highlight + text) in session_state
  |
  ├── Connect Tab (prototype)
  |     ├── Extracts themes from messages
  |     ├── Builds lightweight “profile”
  |     └── Matches users + creates peer chat rooms (in session_state)
  |
  └── Games Tab
        ├── Word Detective (session_state score/progress)
        ├── Gratitude Jar (streak + jar entries)
        └── Breathing Exercise (animated timed cycles)
