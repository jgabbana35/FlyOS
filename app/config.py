"""
Fly OS — Configuration v5.0
Triple Hybrid Engine: Gemini → OpenRouter → Base44
"""
import os
from pathlib import Path
from datetime import date

TODAY = date.today().strftime("%A, %B %d, %Y")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
DB_PATH       = str(BASE_DIR / "fly_memory.db")
WORKSPACE_DIR.mkdir(exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY     = "AIzaSyA5geTuBZxaQO007WZOkXPTKcT5u6guggY"
OPENROUTER_API_KEY = "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"
BASE44_API_KEY     = "132c6e177fed46159968dee4c725a562"
BASE44_AGENT_ID    = "69d41c99ce92d7929b4ffa4b"
BASE44_CONVO_ID    = "69d41c9a6e1e12f63189d134"

# ── Models ─────────────────────────────────────────────────────────────────────
MODEL_GEMINI     = "gemini-2.5-flash"
MODEL_OPENROUTER = "qwen/qwen3-235b-a22b:free"
MAX_TOKENS       = 8192
TEMPERATURE      = 0.7

# ── File extensions ────────────────────────────────────────────────────────────
IMAGE_EXTENSIONS   = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"}
VIDEO_EXTENSIONS   = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}
AUDIO_EXTENSIONS   = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}
DOCUMENT_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".py", ".js", ".ts", ".html", ".htm",
    ".css", ".json", ".csv", ".xml", ".yaml", ".yml",
    ".sh", ".c", ".cpp", ".java", ".go", ".rs", ".rb",
    ".php", ".swift", ".kt", ".docx", ".xlsx", ".xls",
    ".pptx", ".ppt", ".doc", ".rtf", ".odt", ".epub",
    ".ipynb", ".toml", ".ini", ".cfg", ".env", ".log",
}
ALL_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

# ── App ────────────────────────────────────────────────────────────────────────
APP_TITLE   = "Fly OS"
APP_VERSION = "5.0"
WINDOW_SIZE = "1480x960"

# ── GitHub auto-update ─────────────────────────────────────────────────────────
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/jgabbana35/FlyOS/main/version.json"

# ── Modes ──────────────────────────────────────────────────────────────────────
MODES = {
    "chat":     "Chat",
    "code":     "Code",
    "research": "Research",
    "writing":  "Writing",
    "vision":   "Vision",
    "data":     "Data",
}

MODE_PROMPTS = {
    "chat": (
        f"You are Fly OS v5, an advanced AI assistant. Today is {TODAY}. "
        "Be conversational, helpful, and precise. Always use the current date. "
        "When the user pastes a URL, automatically fetch and summarize its content."
    ),
    "code": (
        f"You are Fly OS in Code mode. Today is {TODAY}. "
        "You are an elite senior software engineer. Write clean, production-quality code. "
        "Always use markdown code blocks with language tags. Identify bugs and edge cases proactively. "
        "Run code in background workers when possible and show execution results."
    ),
    "research": (
        f"You are Fly OS in Research mode. Today is {TODAY}. "
        "Provide thorough, evidence-based answers using web search. "
        "Use headers and bullet points. Distinguish facts from inference."
    ),
    "writing": (
        f"You are Fly OS in Writing mode. Today is {TODAY}. "
        "You are a skilled ghostwriter and editor. Help draft, refine, and polish content. "
        "Match the user's tone and audience. You can generate DOCX/PDF outputs on request."
    ),
    "vision": (
        f"You are Fly OS in Vision mode. Today is {TODAY}. "
        "Analyze images and video frames thoroughly: describe content, identify objects, "
        "read text (OCR), interpret charts, assess quality. Be specific and detailed."
    ),
    "data": (
        f"You are Fly OS in Data mode. Today is {TODAY}. "
        "You are an expert data analyst. Find patterns, compute statistics, provide insights. "
        "Use tables and structured formatting. Generate charts and visualizations when helpful. "
        "You can create Excel (.xlsx) and CSV files as outputs."
    ),
}

# ── Speed/Research mode ────────────────────────────────────────────────────────
RESPONSE_MODES = {
    "fast":       {"label": "⚡ Fast",       "max_tokens": 2048,  "temperature": 0.5},
    "balanced":   {"label": "⚖ Balanced",   "max_tokens": 4096,  "temperature": 0.7},
    "research":   {"label": "🔬 Research",   "max_tokens": 8192,  "temperature": 0.4},
    "creative":   {"label": "✨ Creative",   "max_tokens": 6144,  "temperature": 1.0},
}

# ── Color palette (dark + accent) ──────────────────────────────────────────────
BG_BASE        = "#0F1117"
BG_SURFACE     = "#1A1D27"
BG_SURFACE2    = "#222636"
BG_SIDEBAR     = "#0D0F18"
SIDEBAR_HOVER  = "#1A1D27"
SIDEBAR_ACTIVE = "#1E2235"
TEXT_SIDEBAR   = "#E2E8F0"
TEXT_SIDEBAR_M = "#64748B"

BG_USER_MSG    = "#1E3A5F"
BG_AI_MSG      = "#1A1D27"
BG_INPUT       = "#1A1D27"
BG_SURFACE2    = "#222636"

BORDER         = "#2D3748"
BORDER_FOCUS   = "#4A5568"

ACCENT         = "#6C63FF"
ACCENT_HOVER   = "#5A52E0"
ACCENT_LIGHT   = "#2D2B4E"
ACCENT_2       = "#00D4FF"

TEXT_PRIMARY   = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED     = "#475569"

GREEN          = "#10B981"
GREEN_HOVER    = "#059669"
GREEN_LIGHT    = "#0D2B1F"
RED            = "#EF4444"
RED_LIGHT      = "#2D1515"
ORANGE         = "#F59E0B"
ORANGE_LIGHT   = "#2D2010"

THINKING_COLOR = "#F59E0B"
