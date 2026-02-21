# FrameForge

> **Text-to-animation powered by AI and Manim** — describe any mathematical concept, diagram, or motion in plain English and get a rendered MP4 in seconds.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)
![Manim](https://img.shields.io/badge/Manim-0.19.0-FF6B6B?style=flat-square)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama_3.3-F54F29?style=flat-square)
![Supabase](https://img.shields.io/badge/Storage-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)

---

## What is FrameForge?

FrameForge is a full-stack web application that converts natural language prompts into Manim animations. Type *"pythagorean theorem visualization"* and within 30–60 seconds you have a polished MP4. Share it to the community feed, download it, or inspect the generated Manim code.

The system uses a **dual-path architecture**: common prompts are served instantly from a template cache (with LLM intent verification), while novel prompts go through an AI code generation → auto-fix → validation → render pipeline.

---

## Features

- **Natural language to animation** — no Manim knowledge required
- **Template engine** — 9 built-in templates for instant renders on common prompts
- **LLM intent verification** — prevents template mismatches using a zero-cost classification call
- **Auto-fixer** — automatically patches common Manim errors before rendering (LaTeX substitution, deprecated APIs, missing waits, nested parenthesis bugs)
- **Community feed** — post animations publicly, browse and rate others' creations
- **LaTeX-free mode** — full functionality on systems without a LaTeX installation
- **Code viewer** — inspect and copy the generated Manim Python code for every animation
- **Download** — cross-origin safe MP4 download via blob URL

---

## Architecture

```
User Prompt
     │
     ▼
┌─────────────────────────────────────────────┐
│              Template Manager               │
│  keyword match → LLM confirms intent        │
│  (returns template or falls through)        │
└──────────────┬──────────────────────────────┘
               │ no match
               ▼
┌─────────────────────────────────────────────┐
│           LLM Code Generator               │
│  Groq Llama 3.3 70B → Manim Python code    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│              Auto Fixer                     │
│  8 targeted fix passes (LaTeX, paths,       │
│  include_numbers, move_along_path, etc.)    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│              Validator                      │
│  AST parse → scene detection → complexity   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│              Renderer                       │
│  manim CLI subprocess → MP4                 │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│           Supabase Storage                  │
│  async upload → public URL → frontend       │
└─────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Axios |
| Backend | FastAPI, Python 3.9 |
| LLM | Groq API — Llama 3.3 70B |
| Animation | Manim Community v0.19.0 |
| Storage | Supabase Storage |
| Database | Supabase (community posts) |

---

## Project Structure

```
FrameForge/
├── backend/
│   ├── main.py                  # FastAPI app, pipeline orchestration
│   ├── config.py                # Pydantic settings, env vars
│   ├── generator.py             # LLM code generation (Groq)
│   ├── code_fixer.py            # Auto-fix pass (8 targeted fixes)
│   ├── validator.py             # AST validation + complexity check
│   ├── renderer.py              # Manim subprocess runner
│   ├── code_writer.py           # Temp file management
│   ├── supabase_client.py       # Async video upload
│   └── templates/
│       ├── template_manager.py  # Rule engine + LLM intent check
│       ├── graph.py             # Sin, quadratic, generic graph templates
│       ├── equation.py          # Euler, quadratic formula templates
│       ├── geometry.py          # Circle, Pythagorean templates
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main UI — prompt, video, community feed
│   │   └── components/
│   │       ├── Navbar.jsx
│   │       ├── Footer.jsx
│   │       └── DotPattern.jsx
│   ├── package.json
│   └── vite.config.js
├── runtime/
│   ├── temp/                    # Generated scene files (auto-cleaned)
│   └── outputs/                 # Rendered MP4s
├── requirements.txt
└── .env
```

---

## Getting Started

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.9+ | Tested on 3.9 |
| Node.js 18+ | For the React frontend |
| FFmpeg | Required by Manim — `winget install Gyan.FFmpeg` |
| Groq API key | Free tier available at [console.groq.com](https://console.groq.com) |
| Supabase project | Free tier — for storage and community posts |

> **No LaTeX required.** FrameForge runs in LaTeX-free mode by default. Set `ALLOW_LATEX=true` only if MiKTeX is installed and you need `MathTex` rendering.

---

### 1. Clone

```bash
git clone https://github.com/yourname/frameforge.git
cd frameforge
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .anim
.anim\Scripts\activate        # Windows
# source .anim/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
# LLM
GROQ_API_KEY=gsk_...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=animations

# LaTeX
ALLOW_LATEX=false

# Render settings
RENDER_TIMEOUT=120
MANIM_QUALITY=l
```

Start the backend:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the dev server:

```bash
npm run dev
# → http://localhost:5173
```

### 4. Supabase Setup

1. Go to **Supabase Dashboard → Storage → New bucket**
2. Name it `animations` (or match your `SUPABASE_BUCKET` env var)
3. **Make the bucket public** — this is required for video URLs to be accessible in the browser
4. Create a `posts` table for the community feed:

```sql
create table posts (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  title text not null,
  rating integer not null check (rating between 1 and 5),
  video_url text not null,
  created_at timestamptz default now()
);
```

---

## Configuration Reference

All settings are loaded from environment variables via `config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | required | Groq API key for LLM generation |
| `SUPABASE_URL` | required | Your Supabase project URL |
| `SUPABASE_KEY` | required | Supabase anon/service key |
| `SUPABASE_BUCKET` | `animations` | Storage bucket name |
| `ALLOW_LATEX` | `false` | Enable LaTeX / MathTex rendering |
| `RENDER_TIMEOUT` | `120` | Max seconds for Manim to render |
| `MANIM_QUALITY` | `l` | Quality: `l` (480p), `m` (720p), `h` (1080p) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq model identifier |
| `LLM_MAX_TOKENS` | `2048` | Max tokens for code generation |

---

## What FrameForge Can Generate

| Category | Examples |
|----------|---------|
| **Geometry** | Growing circles, shape morphing, rotation, polygon creation |
| **Graphs & Functions** | sin(x), cos(x), parabolas, multi-curve plots, animated tracing |
| **Math & Equations** | Pythagorean proof, Euler's identity, quadratic formula reveal |
| **Animations & Motion** | Bouncing ball, path following, fade transitions, Write/Create |
| **Diagrams** | Neural networks, sorting algorithms, binary search, tree structures |

### Current Limitations

- No LaTeX by default (plain `Text()` rendering only unless MiKTeX installed)
- No 3D scenes or camera movement
- No external image or asset imports
- No audio
- Output fixed at 480p (`-ql` quality flag)

---

## API Reference

### `POST /generate-animation`

Generate an animation from a text prompt.

**Request:**
```json
{
  "prompt": "pythagorean theorem visualization",
  "quality": "l"
}
```

**Response (success):**
```json
{
  "status": "success",
  "video_url": "https://your-project.supabase.co/storage/v1/object/public/animations/SinPlotScene.mp4",
  "scene_name": "SinPlotScene",
  "code": "from manim import *\n...",
  "template_used": "sin_plot",
  "warnings": []
}
```

**Response (error):**
```json
{
  "status": "error",
  "stage": "rendering",
  "message": "Manim rendering failed.",
  "suggestion": "Try a simpler prompt.",
  "suggestions": ["blue circle that grows", "plot sin(x)"]
}
```

### `GET /posts`

Fetch all community posts.

### `POST /posts`

Submit a new community post.

```json
{
  "name": "Alex",
  "title": "Pythagorean Theorem",
  "rating": 5,
  "video_url": "https://..."
}
```

### `GET /health`

Returns system status including LaTeX availability and template count.

---

## How the Template Engine Works

The template engine prevents unnecessary LLM calls for common prompts while avoiding false matches on complex requests.

```
"plot sin(x)"              → keyword match → LLM says YES → template returned  ⚡ instant
"Taylor series of sin(x)"  → keyword match → LLM says NO  → falls through to LLM generation
"neural network diagram"   → no keyword match             → LLM generation
```

Each template rule is a Python function that checks the normalized prompt. When a keyword match fires, a lightweight Groq call (`max_tokens=5`, `temperature=0`) confirms intent before the template is returned. This adds ~300ms on matches but prevents silent mismatches.

---

## Development Notes

### Adding a New Template

1. Add the scene code to the relevant file in `backend/templates/`
2. Add a rule function in `template_manager.py` under `_build_rules()`
3. Restart the server — templates are validated at startup

```python
def _is_my_template(p: str) -> bool:
    COMPLEX_DISQUALIFIERS = ["series", "proof", "derive"]
    if any(kw in p for kw in COMPLEX_DISQUALIFIERS):
        return False
    return _has_any_word(p, ["my keyword", "another keyword"])

rules.append((_is_my_template, "my_key", MY_TEMPLATE_CODE, scene_name, "My template description"))
```

### Enabling LaTeX

Install MiKTeX on Windows, then set `ALLOW_LATEX=true` in `.env`. The generator system prompt will update automatically to allow `MathTex` and `Tex` objects, and the auto-fixer will stop replacing them with `Text()`.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with Manim, FastAPI, React, and Groq · Made by Rajat Singh</sub>
</div>