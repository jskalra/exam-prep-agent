# ⚡ Exam Prep Agent

AI-powered prep tool for competitive exams (F=ma, AMC 10, and more).

## Features
- 🧠 **Tutor tab** — ask anything, get Feynman-style explanations
- 🎯 **Practice tab** — AI-generated problems with hints + answer checking
- 📋 **Exam tab** — topic breakdown, formulas, past paper links
- 🔥 Score, streaks, and weak-topic tracking

## Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/exam-prep-agent
cd exam-prep-agent
pip install -r requirements.txt
cp .env.example .env          # add your Anthropic API key
streamlit run app.py
```

## Adding a New Exam
Drop a YAML file in `/exams/` — it appears automatically in the selector.
See `exams/fma.yaml` for the schema.

## Project Structure
```
exam-prep-agent/
├── app.py                  # Streamlit UI
├── exams/
│   └── fma.yaml            # F=ma config (add more here)
├── modules/
│   ├── llm_client.py       # LLM abstraction (Claude / future Ollama)
│   ├── tutor.py            # Concept explanation + feedback
│   ├── problem_gen.py      # Problem generation + validation
│   ├── session.py          # In-memory session state
│   └── exam_loader.py      # YAML config loader
└── prompts/
    └── templates.py        # All system prompts
```

## Roadmap
- [ ] Week 2: Past paper fetcher + PDF parser
- [ ] Week 3: SQLite progress tracking + weak topic detection
- [ ] Week 4: Engagement layer (XP, streaks, leaderboard)
- [ ] Later: React Native mobile app
- [ ] Later: Local model support via Ollama

## Deploy to Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set `ANTHROPIC_API_KEY` in secrets
4. Done — shareable URL in 2 minutes
