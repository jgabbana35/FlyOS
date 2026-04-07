"""
Fly OS — GUI v5.0
Dark, premium AI assistant interface.
Features:
  - "Fly is thinking..." animated indicator
  - Send → Stop button while streaming
  - Speed/mode picker (Fast / Balanced / Research / Creative / Engine switcher)
  - Big + attach button
  - Unlimited-height chat bubbles with copy
  - Video playback via VLC or system player
  - Inline image gallery
  - URL auto-detect and fetch
  - PPTX / XLSX export
  - Auto-update banner
  - Markdown rendering (bold, code, headers)
"""

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import os, subprocess, platform, shutil, threading, re
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
from PIL import Image, ImageTk

from app.config import *
from app.client import FlyClient

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Platform opener ────────────────────────────────────────────────────────────
def open_file(path: str):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception:
        pass

# ── Engine colors ──────────────────────────────────────────────────────────────
ENGINE_META = {
    "gemini":     ("#6C63FF", "Gemini 2.5 Flash",  "●"),
    "openrouter": (ORANGE,    "OpenRouter Qwen3",   "●"),
    "base44":     (GREEN,     "Base44 Agent",       "●"),
}

# ── Simple markdown renderer ───────────────────────────────────────────────────
def render_markdown_to_text(text: str) -> str:
    """Strip markdown to plain for the textbox (full renderer would need webview)."""
    # Remove code block fences but keep content
    text = re.sub(r"```\w*\n?", "", text)
    # Bold **text** → TEXT
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    # Italic *text* → text
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # Headers
    text = re.sub(r"^#{1,3}\s+", "  ▸ ", text, flags=re.MULTILINE)
    # Horizontal rules
    text = re.sub(r"^---+$", "─" * 48, text, flags=re.MULTILINE)
    return text


# ─────────────────────────────────────────────────────────────────────────────
# Full-size image viewer
# ─────────────────────────────────────────────────────────────────────────────
class ImageViewer(ctk.CTkToplevel):
    def __init__(self, parent, img_path: str):
        super().__init__(parent)
        self.title(Path(img_path).name)
        self.configure(fg_color=BG_BASE)
        self.resizable(True, True)
        try:
            pil   = Image.open(img_path)
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            ratio = min(int(sw * 0.82) / pil.width, int(sh * 0.82) / pil.height, 1.0)
            dw    = max(1, int(pil.width  * ratio))
            dh    = max(1, int(pil.height * ratio))
            pil_r = pil.resize((dw, dh), Image.LANCZOS)
            self.geometry(f"{dw + 40}x{dh + 90}")
            ctk_img = ctk.CTkImage(light_image=pil_r, dark_image=pil_r, size=(dw, dh))
            self._ref = ctk_img
            ctk.CTkLabel(self, image=ctk_img, text="", fg_color=BG_BASE
                         ).pack(padx=20, pady=(20, 8))
            row = ctk.CTkFrame(self, fg_color=BG_BASE)
            row.pack(pady=(0, 14))
            ctk.CTkButton(row, text="Open externally",
                          fg_color=ACCENT, hover_color=ACCENT_HOVER,
                          text_color=TEXT_PRIMARY, width=140, height=32, corner_radius=8,
                          command=lambda: open_file(img_path)).pack(side="left", padx=4)
            ctk.CTkButton(row, text="Save copy",
                          fg_color=BG_SURFACE, hover_color=BORDER,
                          text_color=TEXT_SECONDARY, width=100, height=32,
                          border_width=1, border_color=BORDER, corner_radius=8,
                          command=lambda: self._save(img_path)).pack(side="left", padx=4)
        except Exception as e:
            ctk.CTkLabel(self, text=f"Cannot load image:\n{e}",
                         text_color=RED, fg_color=BG_BASE).pack(pady=40, padx=20)

    def _save(self, src):
        dest = filedialog.asksaveasfilename(
            defaultextension=Path(src).suffix,
            initialfile=Path(src).name,
            filetypes=[("Image files", "*.png *.jpg *.gif *.webp"), ("All files", "*.*")]
        )
        if dest:
            shutil.copy2(src, dest)
            messagebox.showinfo("Saved", f"Saved to:\n{dest}")


# ─────────────────────────────────────────────────────────────────────────────
# Thinking indicator (animated dots)
# ─────────────────────────────────────────────────────────────────────────────
class ThinkingIndicator(ctk.CTkFrame):
    DOTS = ["Fly is thinking", "Fly is thinking.", "Fly is thinking..",
            "Fly is thinking..."]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=BG_SURFACE, corner_radius=16,
                         border_width=1, border_color=BORDER, **kwargs)
        self._idx  = 0
        self._job  = None          # always initialized so stop() is safe
        self._dead = False         # guard against double-destroy
        hdr = ctk.CTkFrame(self, fg_color=BG_SURFACE)
        hdr.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(hdr, text="Fly OS  •  Gemini 2.5 Flash",
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=ACCENT, fg_color=BG_SURFACE).pack(side="left")
        self._lbl = ctk.CTkLabel(self, text=self.DOTS[0],
                                 font=ctk.CTkFont(family="Segoe UI", size=14),
                                 text_color=THINKING_COLOR, fg_color=BG_SURFACE)
        self._lbl.pack(fill="x", padx=16, pady=(6, 14))
        self._animate()

    def _animate(self):
        if self._dead:
            return
        self._idx = (self._idx + 1) % len(self.DOTS)
        try:
            self._lbl.configure(text=self.DOTS[self._idx])
            self._job = self.after(500, self._animate)
        except Exception:
            pass

    def stop(self):
        if self._dead:
            return
        self._dead = True
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
        try:
            self.destroy()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Chat bubble (user or AI)
# ─────────────────────────────────────────────────────────────────────────────
class ChatBubble(ctk.CTkFrame):
    def __init__(self, parent, role: str, text: str = "",
                 images: list = None, engine: str = "gemini", **kwargs):
        is_user  = (role == "user")
        bg       = BG_USER_MSG if is_user else BG_AI_MSG
        border_c = "#2A4A7A" if is_user else BORDER

        super().__init__(parent, fg_color=bg, corner_radius=16,
                         border_width=1, border_color=border_c, **kwargs)
        self._full_text  = text
        self._image_refs = []
        self._role       = role

        # ── Header ──────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=bg)
        hdr.pack(fill="x", padx=16, pady=(12, 0))

        if is_user:
            name_color = ACCENT_2
            name_label = "You"
        else:
            color, label, dot = ENGINE_META.get(engine, ENGINE_META["gemini"])
            name_color = color
            name_label = f"Fly OS  ·  {label}"

        ctk.CTkLabel(hdr, text=name_label,
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=name_color, fg_color=bg).pack(side="left")

        if not is_user:
            action_row = ctk.CTkFrame(hdr, fg_color=bg)
            action_row.pack(side="right")
            self._copy_btn = ctk.CTkButton(
                action_row, text="Copy", width=54, height=24,
                font=ctk.CTkFont(size=11),
                fg_color=ACCENT_LIGHT, hover_color=BORDER,
                text_color=ACCENT, corner_radius=6,
                command=self._copy)
            self._copy_btn.pack(side="left", padx=2)

        # ── Image previews ───────────────────────────────────────────────────
        if images:
            img_row = ctk.CTkFrame(self, fg_color=bg)
            img_row.pack(fill="x", padx=16, pady=(8, 0))
            for img_path in images:
                try:
                    pil = Image.open(img_path)
                    pil.thumbnail((220, 220))
                    ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil,
                                           size=(pil.width, pil.height))
                    self._image_refs.append(ctk_img)
                    lbl = ctk.CTkLabel(img_row, image=ctk_img, text="",
                                       fg_color=bg, cursor="hand2")
                    lbl.pack(side="left", padx=(0, 8), pady=4)
                    lbl.bind("<Button-1>",
                             lambda e, p=img_path: ImageViewer(self.winfo_toplevel(), p))
                except Exception:
                    pass

        # ── Text body (unlimited height, no scroll lock) ─────────────────────
        self.textbox = ctk.CTkTextbox(
            self, fg_color=bg,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=TEXT_PRIMARY,
            wrap="word",
            activate_scrollbars=False,
            height=32,
            border_width=0,
        )
        self.textbox.pack(fill="x", padx=16, pady=(6, 14))
        self.textbox.configure(state="disabled")
        if text:
            self.set_text(text)

    def set_text(self, text: str):
        self._full_text = text
        display = render_markdown_to_text(text)
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", display)
        self.textbox.configure(state="disabled")
        self._auto_resize()

    def append_text(self, chunk: str):
        self._full_text += chunk
        display_chunk = render_markdown_to_text(chunk)
        self.textbox.configure(state="normal")
        self.textbox.insert("end", display_chunk)
        self.textbox.configure(state="disabled")
        self._auto_resize()

    def _auto_resize(self):
        """Grow the textbox to fit all text — no upper limit."""
        try:
            self.textbox.update_idletasks()
            line_count = int(self.textbox.index("end-1c").split(".")[0])
            new_h = max(line_count * 21 + 8, 32)
            self.textbox.configure(height=new_h)
        except Exception:
            pass

    def _copy(self):
        try:
            import pyperclip
            pyperclip.copy(self._full_text)
        except ImportError:
            self.clipboard_clear()
            self.clipboard_append(self._full_text)
        self._copy_btn.configure(text="✓ Copied")
        self.after(2000, lambda: self._copy_btn.configure(text="Copy"))


# ─────────────────────────────────────────────────────────────────────────────
# Attachment preview card
# ─────────────────────────────────────────────────────────────────────────────
class PreviewCard(ctk.CTkFrame):
    ICONS = {".pdf": "PDF", ".docx": "DOC", ".doc": "DOC",
             ".xlsx": "XLS", ".xls": "XLS", ".pptx": "PPT",
             ".py": "PY", ".csv": "CSV", ".mp4": "VID",
             ".mov": "VID", ".mp3": "AUD", ".txt": "TXT"}

    def __init__(self, parent, filepath: str, on_remove, **kwargs):
        super().__init__(parent, fg_color=BG_SURFACE2, corner_radius=12,
                         border_width=1, border_color=BORDER, **kwargs)
        self.filepath = filepath
        suffix = Path(filepath).suffix.lower()
        name   = Path(filepath).name

        if suffix in IMAGE_EXTENSIONS:
            try:
                pil = Image.open(filepath)
                pil.thumbnail((86, 86))
                self._thumb = ctk.CTkImage(light_image=pil, dark_image=pil,
                                           size=(pil.width, pil.height))
                lbl = ctk.CTkLabel(self, image=self._thumb, text="",
                                   fg_color=BG_SURFACE2, cursor="hand2")
                lbl.pack(padx=8, pady=(8, 2))
                lbl.bind("<Button-1>", lambda e: ImageViewer(self.winfo_toplevel(), filepath))
            except Exception:
                self._icon_label("IMG")
        else:
            self._icon_label(self.ICONS.get(suffix, "FILE"))

        disp = (name[:13] + "…") if len(name) > 13 else name
        ctk.CTkLabel(self, text=disp,
                     font=ctk.CTkFont(size=9),
                     text_color=TEXT_MUTED, fg_color=BG_SURFACE2,
                     wraplength=90).pack(padx=4)

        ctk.CTkButton(self, text="×", width=20, height=20,
                      fg_color=BG_SURFACE2, hover_color=RED_LIGHT,
                      text_color=RED, font=ctk.CTkFont(size=14),
                      corner_radius=10,
                      command=lambda: on_remove(self)).pack(pady=(2, 6))

    def _icon_label(self, text: str):
        ctk.CTkLabel(self, text=text,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=ACCENT, fg_color=BG_SURFACE2
                     ).pack(padx=8, pady=(12, 2))


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar history item
# ─────────────────────────────────────────────────────────────────────────────
class HistoryItem(ctk.CTkButton):
    def __init__(self, parent, session: dict, on_click, on_delete, **kwargs):
        self.session_id = session["id"]
        self._on_click  = on_click
        self._on_delete = on_delete
        title   = (session.get("title") or "Untitled")[:26]
        engine  = session.get("engine", "gemini")
        super().__init__(
            parent,
            text=f"  {title}",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=36, corner_radius=8,
            fg_color="transparent",
            hover_color=SIDEBAR_HOVER,
            text_color=TEXT_SIDEBAR,
            command=self._clicked,
            **kwargs,
        )
        self.bind("<Button-3>", self._right_click)

    def _clicked(self):
        self._on_click(self.session_id)

    def _right_click(self, event):
        menu = tk.Menu(self, tearoff=0,
                       bg=BG_SURFACE2, fg=TEXT_SIDEBAR,
                       activebackground=RED_LIGHT, activeforeground=TEXT_PRIMARY,
                       font=("Segoe UI", 11))
        menu.add_command(label="Load",   command=lambda: self._on_click(self.session_id))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self._on_delete(self.session_id))
        menu.tk_popup(event.x_root, event.y_root)

    def set_active(self, active: bool):
        self.configure(fg_color=SIDEBAR_ACTIVE if active else "transparent")


# ─────────────────────────────────────────────────────────────────────────────
# Mode pill button
# ─────────────────────────────────────────────────────────────────────────────
class ModePill(ctk.CTkButton):
    def __init__(self, parent, mode_key: str, on_select, active=False, **kwargs):
        self.mode_key   = mode_key
        self._on_select = on_select
        label = MODES.get(mode_key, mode_key.title())
        super().__init__(
            parent, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=30, corner_radius=15,
            fg_color=ACCENT if active else BG_SURFACE2,
            hover_color=ACCENT_LIGHT,
            text_color=TEXT_PRIMARY if active else TEXT_SECONDARY,
            border_width=1,
            border_color=ACCENT if active else BORDER,
            command=lambda: on_select(mode_key),
            **kwargs,
        )

    def set_active(self, active: bool):
        self.configure(
            fg_color=ACCENT if active else BG_SURFACE2,
            text_color=TEXT_PRIMARY if active else TEXT_SECONDARY,
            border_color=ACCENT if active else BORDER,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Speed/Engine picker popup
# ─────────────────────────────────────────────────────────────────────────────
class SpeedMenu(ctk.CTkToplevel):
    def __init__(self, parent, current_resp_mode, current_engine,
                 on_resp_mode, on_engine, **kwargs):
        super().__init__(parent, **kwargs)
        self.overrideredirect(True)
        self.configure(fg_color=BG_SURFACE)
        self.resizable(False, False)

        # Position near parent
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        self.geometry(f"220x320+{px - 80}+{py - 330}")

        ctk.CTkLabel(self, text="Response Mode",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_MUTED, fg_color=BG_SURFACE
                     ).pack(anchor="w", padx=14, pady=(12, 4))

        for key, meta in RESPONSE_MODES.items():
            btn = ctk.CTkButton(
                self, text=meta["label"],
                font=ctk.CTkFont(size=13), height=34, corner_radius=8,
                fg_color=ACCENT_LIGHT if key == current_resp_mode else BG_SURFACE2,
                hover_color=ACCENT_LIGHT,
                text_color=ACCENT if key == current_resp_mode else TEXT_PRIMARY,
                border_width=1 if key == current_resp_mode else 0,
                border_color=ACCENT,
                command=lambda k=key: (on_resp_mode(k), self._safe_close()),
            )
            btn.pack(fill="x", padx=10, pady=2)

        ctk.CTkFrame(self, height=1, fg_color=BORDER).pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(self, text="Switch Engine",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_MUTED, fg_color=BG_SURFACE
                     ).pack(anchor="w", padx=14, pady=(0, 4))

        engines = [("gemini", "⚡ Gemini"), ("openrouter", "🔀 OpenRouter"), ("base44", "🛡 Base44")]
        for eng_key, eng_label in engines:
            btn = ctk.CTkButton(
                self, text=eng_label,
                font=ctk.CTkFont(size=13), height=30, corner_radius=8,
                fg_color=ACCENT_LIGHT if eng_key == current_engine else BG_SURFACE2,
                hover_color=ACCENT_LIGHT,
                text_color=ACCENT if eng_key == current_engine else TEXT_PRIMARY,
                command=lambda k=eng_key: (on_engine(k), self._safe_close()),
            )
            btn.pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(self, text="Close", height=28, font=ctk.CTkFont(size=11),
                      fg_color="transparent", text_color=TEXT_MUTED,
                      hover_color=BG_SURFACE2,
                      command=self._safe_close).pack(pady=(6, 8))

        # FocusOut fires for child widgets too — only close when focus truly leaves
        self._closing = False
        self.bind("<FocusOut>", self._on_focus_out)
        self.focus_force()

    def _on_focus_out(self, event):
        if self._closing:
            return
        try:
            focused = self.focus_get()
            if focused and str(focused).startswith(str(self)):
                return  # focus moved to a child — stay open
        except Exception:
            pass
        self._safe_close()

    def _safe_close(self):
        if self._closing:
            return
        self._closing = True
        try:
            self.destroy()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Main Application Window
# ─────────────────────────────────────────────────────────────────────────────
class FlyOS(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION}  —  Triple Hybrid Engine")
        self.geometry(WINDOW_SIZE)
        self.minsize(1000, 660)
        self.configure(fg_color=BG_BASE)

        # State
        self.attachments       : list[str]         = []
        self.preview_cards     : list[PreviewCard] = []
        self.is_streaming      : bool              = False
        self.current_bubble    : ChatBubble | None = None
        self.thinking_widget   : ThinkingIndicator | None = None
        self.active_mode       : str               = "chat"
        self.resp_mode         : str               = "balanced"
        self.mode_pills        : dict              = {}
        self.history_items     : dict              = {}
        self.active_session    : str | None        = None
        self.use_search        : bool              = False
        self.use_code          : bool              = False
        self._welcome_visible  : bool              = True
        self._active_engine    : str               = "gemini"
        self._img_refs         : list              = []
        self._forced_engine    : str | None        = None

        self.client: FlyClient | None = None
        self._init_client()
        self._build_layout()
        self._load_history_sidebar()
        # Check for updates in background
        threading.Thread(target=self._check_update, daemon=True).start()

    # ── Init ──────────────────────────────────────────────────────────────────

    def _init_client(self):
        try:
            self.client = FlyClient()
        except Exception as e:
            messagebox.showerror("Startup Error", str(e))

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self):
        self._build_sidebar()
        main = ctk.CTkFrame(self, fg_color=BG_BASE, corner_radius=0)
        main.pack(side="right", fill="both", expand=True)
        self._build_topbar(main)
        self._build_chat_area(main)
        self._build_input_area(main)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0, width=268)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        self._sb = sb

        # Logo
        logo = ctk.CTkFrame(sb, fg_color=BG_SIDEBAR)
        logo.pack(fill="x", padx=20, pady=(22, 2))
        ctk.CTkLabel(logo, text="FLY",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     text_color=ACCENT, fg_color=BG_SIDEBAR).pack(side="left")
        ctk.CTkLabel(logo, text=" OS",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     text_color=TEXT_SIDEBAR, fg_color=BG_SIDEBAR).pack(side="left")

        ctk.CTkLabel(sb, text=f"v{APP_VERSION}  ·  Triple Hybrid Engine",
                     font=ctk.CTkFont(size=10),
                     text_color=TEXT_SIDEBAR_M,
                     fg_color=BG_SIDEBAR).pack(anchor="w", padx=20, pady=(0, 14))

        # Engine indicator
        eng_frame = ctk.CTkFrame(sb, fg_color=BG_SURFACE, corner_radius=10)
        eng_frame.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkLabel(eng_frame, text="ACTIVE ENGINE",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_MUTED, fg_color=BG_SURFACE
                     ).pack(anchor="w", padx=12, pady=(8, 0))
        self._engine_lbl = ctk.CTkLabel(
            eng_frame, text="● Gemini 2.5 Flash",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=ACCENT, fg_color=BG_SURFACE)
        self._engine_lbl.pack(anchor="w", padx=12, pady=(2, 8))

        # Action buttons
        ctk.CTkButton(sb, text="＋  New Chat",
                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                      height=42, corner_radius=12,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT_PRIMARY,
                      command=self._new_chat).pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkButton(sb, text="🎨  Generate Image",
                      font=ctk.CTkFont(size=12), height=36, corner_radius=10,
                      fg_color=BG_SURFACE, hover_color=SIDEBAR_HOVER,
                      text_color=TEXT_SIDEBAR,
                      command=self._image_gen_dialog).pack(fill="x", padx=14, pady=(0, 4))

        # Export row
        exp = ctk.CTkFrame(sb, fg_color=BG_SIDEBAR)
        exp.pack(fill="x", padx=14, pady=(0, 4))
        for fmt, label in [("docx","DOCX"), ("pdf","PDF"), ("pptx","PPTX"), ("xlsx","XLSX")]:
            ctk.CTkButton(exp, text=label,
                          font=ctk.CTkFont(size=10), height=30, corner_radius=8,
                          fg_color=BG_SURFACE, hover_color=SIDEBAR_HOVER,
                          text_color=TEXT_SECONDARY,
                          command=lambda f=fmt: self._export(f)
                          ).pack(side="left", fill="x", expand=True, padx=1)

        ctk.CTkButton(sb, text="📁  Open Workspace",
                      font=ctk.CTkFont(size=12), height=32, corner_radius=8,
                      fg_color=BG_SURFACE, hover_color=SIDEBAR_HOVER,
                      text_color=TEXT_SIDEBAR,
                      command=lambda: open_file(str(WORKSPACE_DIR))
                      ).pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", padx=10)

        # Search
        sr = ctk.CTkFrame(sb, fg_color=BG_SIDEBAR)
        sr.pack(fill="x", padx=10, pady=(8, 4))
        self._search_entry = ctk.CTkEntry(
            sr, placeholder_text="Search chats...",
            font=ctk.CTkFont(size=12), height=32, corner_radius=8,
            fg_color=BG_SURFACE, border_color=BORDER,
            text_color=TEXT_SIDEBAR)
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(4, 4))
        self._search_entry.bind("<Return>", self._search_history)
        ctk.CTkButton(sr, text="Go", width=34, height=32, corner_radius=8,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT_PRIMARY,
                      font=ctk.CTkFont(size=11),
                      command=self._search_history).pack(side="right", padx=(0, 4))

        ctk.CTkLabel(sb, text="RECENT CHATS",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_SIDEBAR_M,
                     fg_color=BG_SIDEBAR).pack(anchor="w", padx=18, pady=(4, 4))

        self._hist_scroll = ctk.CTkScrollableFrame(
            sb, fg_color=BG_SIDEBAR,
            scrollbar_button_color=SIDEBAR_HOVER,
            scrollbar_button_hover_color=SIDEBAR_ACTIVE)
        self._hist_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", padx=10)
        ctk.CTkLabel(sb, text=f"Today: {TODAY}",
                     font=ctk.CTkFont(size=9),
                     text_color=TEXT_SIDEBAR_M,
                     fg_color=BG_SIDEBAR).pack(anchor="w", padx=18, pady=(6, 12))

    # ── TOPBAR ────────────────────────────────────────────────────────────────

    def _build_topbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=BG_SURFACE, corner_radius=0, height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkFrame(bar, height=1, fg_color=BORDER).pack(side="bottom", fill="x")

        pills = ctk.CTkFrame(bar, fg_color=BG_SURFACE)
        pills.pack(side="left", padx=14, pady=12)
        for key in MODES:
            p = ModePill(pills, key, on_select=self._on_mode_change, active=(key == "chat"))
            p.pack(side="left", padx=2)
            self.mode_pills[key] = p

        right = ctk.CTkFrame(bar, fg_color=BG_SURFACE)
        right.pack(side="right", padx=14, pady=12)

        self._search_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(right, text="Web Search",
                        font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY,
                        variable=self._search_var, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        command=lambda: setattr(self, "use_search", self._search_var.get())
                        ).pack(side="left", padx=6)

        self._code_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(right, text="Code Exec",
                        font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY,
                        variable=self._code_var, fg_color=GREEN, hover_color=GREEN_HOVER,
                        command=lambda: setattr(self, "use_code", self._code_var.get())
                        ).pack(side="left", padx=6)

        ctk.CTkButton(right, text="Clear",
                      font=ctk.CTkFont(size=12), width=64, height=28, corner_radius=8,
                      fg_color=BG_SURFACE2, hover_color=BORDER,
                      text_color=TEXT_SECONDARY, border_width=1, border_color=BORDER,
                      command=self._clear_chat).pack(side="left", padx=4)

    # ── CHAT AREA ─────────────────────────────────────────────────────────────

    def _build_chat_area(self, parent):
        self._chat_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=BG_BASE,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT)
        self._chat_scroll.pack(fill="both", expand=True)
        self._show_welcome()

    def _show_welcome(self):
        self._welcome_visible = True
        frame = ctk.CTkFrame(self._chat_scroll, fg_color=BG_BASE)
        frame.pack(expand=True, pady=50)

        ctk.CTkLabel(frame, text="FLY OS",
                     font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
                     text_color=ACCENT, fg_color=BG_BASE).pack()
        ctk.CTkLabel(frame, text="Triple Hybrid AI  ·  Gemini + OpenRouter + Base44",
                     font=ctk.CTkFont(family="Segoe UI", size=14),
                     text_color=TEXT_MUTED, fg_color=BG_BASE).pack(pady=(4, 2))
        ctk.CTkLabel(frame, text=f"Today is {TODAY}",
                     font=ctk.CTkFont(size=11),
                     text_color=TEXT_MUTED, fg_color=BG_BASE).pack(pady=(0, 28))

        tiles = ctk.CTkFrame(frame, fg_color=BG_BASE)
        tiles.pack()
        actions = [
            ("💬 Chat",         "chat",     "What can you help me with today?"),
            ("💻 Write Code",   "code",     "Write a Python web scraper for news headlines"),
            ("🔍 Research",     "research", "Summarize the latest developments in AI agents"),
            ("🎨 Gen Image",    "chat",     "GENERATE_IMAGE:a glowing futuristic city at night"),
            ("📊 Data Analysis","data",     "Show me how to analyze a CSV with Python pandas"),
            ("📝 Write Doc",    "writing",  "Write a professional cover letter template"),
        ]
        row1 = ctk.CTkFrame(tiles, fg_color=BG_BASE)
        row1.pack()
        row2 = ctk.CTkFrame(tiles, fg_color=BG_BASE)
        row2.pack(pady=(8, 0))
        for i, (label, mode, prompt) in enumerate(actions):
            target = row1 if i < 3 else row2
            ctk.CTkButton(
                target, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                width=180, height=64, corner_radius=14,
                fg_color=BG_SURFACE, hover_color=ACCENT_LIGHT,
                text_color=TEXT_PRIMARY, border_width=1, border_color=BORDER,
                command=lambda m=mode, p=prompt: self._quick_prompt(m, p)
            ).pack(side="left", padx=5)

    def _clear_welcome(self):
        if self._welcome_visible:
            for w in self._chat_scroll.winfo_children():
                w.destroy()
            self._welcome_visible = False

    # ── INPUT AREA ────────────────────────────────────────────────────────────

    def _build_input_area(self, parent):
        outer = ctk.CTkFrame(parent, fg_color=BG_BASE, corner_radius=0)
        outer.pack(fill="x", padx=48, pady=(0, 20))
        ctk.CTkFrame(outer, height=1, fg_color=BORDER).pack(fill="x")

        # Attachment preview strip — hidden when empty, shown when cards arrive
        self._preview_strip = ctk.CTkFrame(outer, fg_color=BG_BASE)
        self._preview_strip.pack(fill="x")
        self._preview_strip.pack_forget()   # start hidden

        # Input card
        self._input_card = ctk.CTkFrame(outer, fg_color=BG_SURFACE, corner_radius=20,
                            border_width=1, border_color=BORDER)
        self._input_card.pack(fill="x", pady=(6, 0))
        card = self._input_card

        self._input = ctk.CTkTextbox(
            card, height=60,
            fg_color=BG_SURFACE, text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=0, wrap="word", border_width=0)
        self._input.pack(fill="x", padx=16, pady=(12, 0))
        self._input.bind("<Return>",     self._on_enter)
        self._input.bind("<KeyRelease>", self._on_key)
        self._input.bind("<<Paste>>",    self._on_key)
        self._input.bind("<Control-a>",  self._select_all)

        # Bottom toolbar
        btm = ctk.CTkFrame(card, fg_color=BG_SURFACE)
        btm.pack(fill="x", padx=12, pady=(4, 12))

        # BIG + attach button
        ctk.CTkButton(btm, text="＋",
                      width=46, height=38,
                      font=ctk.CTkFont(size=22, weight="bold"),
                      fg_color=BG_SURFACE2, hover_color=ACCENT_LIGHT,
                      text_color=ACCENT, corner_radius=10,
                      border_width=1, border_color=BORDER,
                      command=self._attach_files).pack(side="left", padx=(0, 6))

        # Speed/engine picker button
        self._speed_lbl = ctk.CTkButton(
            btm, text="⚖ Balanced",
            width=110, height=36, font=ctk.CTkFont(size=12),
            fg_color=BG_SURFACE2, hover_color=ACCENT_LIGHT,
            text_color=TEXT_SECONDARY, corner_radius=10,
            border_width=1, border_color=BORDER,
            command=self._open_speed_menu)
        self._speed_lbl.pack(side="left", padx=(0, 6))

        ctk.CTkButton(btm, text="🎨 Image",
                      width=88, height=36, font=ctk.CTkFont(size=12),
                      fg_color=ACCENT_LIGHT, hover_color=BORDER,
                      text_color=ACCENT, corner_radius=10,
                      border_width=1, border_color=ACCENT,
                      command=self._image_gen_dialog).pack(side="left", padx=(0, 8))

        self._char_lbl = ctk.CTkLabel(btm, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color=TEXT_MUTED,
                                       fg_color=BG_SURFACE)
        self._char_lbl.pack(side="left")

        # Send / Stop button
        self._send_btn = ctk.CTkButton(
            btm, text="Send  ↑",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=100, height=38, corner_radius=12,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT_PRIMARY,
            command=self._send_or_stop)
        self._send_btn.pack(side="right")

    # ── EVENT HANDLERS ────────────────────────────────────────────────────────

    def _on_enter(self, event):
        if not (event.state & 0x1):
            self._send_or_stop()
            return "break"

    def _on_key(self, event=None):
        txt = self._input.get("0.0", "end").strip()
        self._char_lbl.configure(text=f"{len(txt):,}" if txt else "")
        # Auto-grow input box (max 5 lines before scroll kicks in)
        line_count = int(self._input.index("end-1c").split(".")[0])
        new_h = max(60, min(line_count * 22 + 8, 130))
        self._input.configure(height=new_h)

    def _select_all(self, event=None):
        self._input.tag_add("sel", "1.0", "end")
        return "break"

    def _on_mode_change(self, mode: str):
        self.active_mode = mode
        for k, p in self.mode_pills.items():
            p.set_active(k == mode)
        if self.client:
            self.client.set_mode(mode)

    def _quick_prompt(self, mode: str, text: str):
        if text.startswith("GENERATE_IMAGE:"):
            self._image_gen_dialog(prefill=text[15:])
            return
        self._on_mode_change(mode)
        self._clear_welcome()
        self._input.delete("0.0", "end")
        self._input.insert("0.0", text)
        self._send()

    def _open_speed_menu(self):
        SpeedMenu(
            self._send_btn,
            current_resp_mode=self.resp_mode,
            current_engine=self._active_engine,
            on_resp_mode=self._set_resp_mode,
            on_engine=self._force_engine,
        )

    def _set_resp_mode(self, mode: str):
        self.resp_mode = mode
        if self.client:
            self.client.set_response_mode(mode)
        label = RESPONSE_MODES[mode]["label"]
        self._speed_lbl.configure(text=label)

    def _force_engine(self, engine: str):
        """Force a specific engine for the next message."""
        self._forced_engine = engine
        self._update_engine_badge(engine)
        if self.client:
            self.client.active_engine = engine

    # ── FILE ATTACHMENT ───────────────────────────────────────────────────────

    def _attach_files(self):
        exts = " ".join(f"*{e}" for e in sorted(ALL_EXTENSIONS))
        paths = filedialog.askopenfilenames(
            title="Attach files — Fly OS",
            filetypes=[
                ("All supported", exts),
                ("Images",   "*.jpg *.jpeg *.png *.gif *.webp *.bmp"),
                ("Documents","*.pdf *.txt *.md *.py *.docx *.xlsx *.pptx *.csv"),
                ("Videos",   "*.mp4 *.mov *.avi *.mkv *.webm"),
                ("All files","*.*"),
            ])
        for p in paths:
            if p not in self.attachments:
                self.attachments.append(p)
                card = PreviewCard(self._preview_strip, filepath=p,
                                   on_remove=self._remove_preview)
                card.pack(side="left", padx=(0, 8), pady=6)
                self.preview_cards.append(card)
        # Show strip if we have cards
        if self.preview_cards:
            self._preview_strip.pack(fill="x", pady=(6, 0), before=self._input_card)

    def _remove_preview(self, card: PreviewCard):
        if card.filepath in self.attachments:
            self.attachments.remove(card.filepath)
        card.destroy()
        if card in self.preview_cards:
            self.preview_cards.remove(card)
        # Hide strip when empty
        if not self.preview_cards:
            self._preview_strip.pack_forget()

    # ── IMAGE GENERATION ──────────────────────────────────────────────────────

    def _image_gen_dialog(self, prefill: str = ""):
        prompt = simpledialog.askstring(
            "Generate Image — Fly OS",
            "Describe the image:",
            initialvalue=prefill,
            parent=self)
        if not prompt or not prompt.strip():
            return
        if not self.client:
            return
        self._clear_welcome()
        self._add_bubble("user", f"🎨 Generate image: {prompt}")
        self.current_bubble = self._add_bubble("assistant", "Generating with Gemini Imagen 3...")
        self._set_busy(True)

        def on_done(fname, fpath):
            def _show():
                self._set_busy(False)
                if self.current_bubble:
                    self.current_bubble.set_text(f"✅ Image ready: {fname}")
                self._on_file_saved(fname, fpath)
                self._reload_history_sidebar()
            self.after(0, _show)

        def on_error(msg):
            def _err():
                self._set_busy(False)
                if self.current_bubble:
                    self.current_bubble.set_text(f"❌ Image error: {msg}")
            self.after(0, _err)

        self.client.generate_image(prompt, on_done=on_done, on_error=on_error)

    # ── EXPORT ────────────────────────────────────────────────────────────────

    def _export(self, fmt: str):
        if not self.client:
            return
        def on_done(fname, fpath):
            def _show():
                self._on_file_saved(fname, fpath)
                if messagebox.askyesno("Exported", f"Saved: {fname}\n\nOpen file now?"):
                    open_file(fpath)
            self.after(0, _show)
        def on_error(msg):
            self.after(0, lambda: messagebox.showerror("Export Error", msg))
        self.client.export_last_response(fmt, on_done=on_done, on_error=on_error)

    # ── SEND / STOP ───────────────────────────────────────────────────────────

    def _send_or_stop(self):
        if self.is_streaming:
            self._stop_generation()
        else:
            self._send()

    def _stop_generation(self):
        if self.client:
            self.client.stop()
        self._set_busy(False)
        if self.thinking_widget:
            try:
                self.thinking_widget.stop()
            except Exception:
                pass
            self.thinking_widget = None
        if self.current_bubble:
            self.current_bubble.append_text("\n\n[⏹ Stopped by user]")

    def _send(self):
        if self.is_streaming or not self.client:
            return
        text        = self._input.get("0.0", "end").strip()
        attachments = list(self.attachments)
        if not text and not attachments:
            return

        self._input.delete("0.0", "end")
        self._input.configure(height=60)   # reset to default height
        self._char_lbl.configure(text="")
        self.attachments.clear()
        for card in self.preview_cards:
            card.destroy()
        self.preview_cards.clear()
        self._preview_strip.pack_forget()  # hide strip after sending
        self._clear_welcome()

        imgs = [p for p in attachments if Path(p).suffix.lower() in IMAGE_EXTENSIONS]
        docs = [p for p in attachments if Path(p).suffix.lower() not in IMAGE_EXTENSIONS]
        disp = text
        if docs:
            disp += "\n\n[Files: " + ", ".join(Path(p).name for p in docs) + "]"
        self._add_bubble("user", disp, images=imgs)

        # Show thinking indicator
        self.thinking_widget = ThinkingIndicator(self._chat_scroll)
        self.thinking_widget.pack(fill="x", padx=40, pady=6)
        self._scroll_bottom()

        self._set_busy(True)

        self.client.set_mode(self.active_mode)
        self.client.set_response_mode(self.resp_mode)
        self.client.stream_response(
            user_text=text,
            attachments=attachments,
            on_token=self._on_token,
            on_done=self._on_done,
            on_error=self._on_error,
            on_file_saved=self._on_file_saved,
            on_engine_change=self._on_engine_change,
            use_search=self.use_search,
            use_code=self.use_code,
        )

    # ── STREAMING CALLBACKS ───────────────────────────────────────────────────

    def _on_token(self, chunk: str):
        def _do():
            # Remove thinking indicator on first real token
            if self.thinking_widget:
                try:
                    self.thinking_widget.stop()
                except Exception:
                    pass
                self.thinking_widget = None
                # Create the AI response bubble now
                self.current_bubble = self._add_bubble(
                    "assistant", "", engine=self._active_engine)

            if self.current_bubble:
                self.current_bubble.append_text(chunk)
            self._scroll_bottom()
        self.after(0, _do)

    def _on_done(self, _full):
        def _do():
            self._set_busy(False)
            if self.thinking_widget:
                try:
                    self.thinking_widget.stop()
                except Exception:
                    pass
                self.thinking_widget = None
                # Empty response (e.g., stopped early)
                if not self.current_bubble:
                    self.current_bubble = self._add_bubble("assistant", "(No response)",
                                                           engine=self._active_engine)
            self._reload_history_sidebar()
        self.after(0, _do)

    def _on_error(self, msg: str):
        def _show():
            self._set_busy(False)
            if self.thinking_widget:
                try:
                    self.thinking_widget.stop()
                except Exception:
                    pass
                self.thinking_widget = None
            bubble = self._add_bubble("assistant", f"❌ Error: {msg}", engine=self._active_engine)
        self.after(0, _show)

    def _on_engine_change(self, engine: str):
        self._active_engine = engine
        self.after(0, lambda: self._update_engine_badge(engine))

    def _on_file_saved(self, fname: str, fpath: str):
        def _notify():
            ext = Path(fpath).suffix.lower()
            # Green notification bar
            notif = ctk.CTkFrame(self._chat_scroll, fg_color=GREEN_LIGHT,
                                  corner_radius=12, border_width=1, border_color="#0D4A30")
            notif.pack(fill="x", padx=40, pady=4)
            ctk.CTkLabel(notif, text=f"📄  Saved: {fname}",
                         font=ctk.CTkFont(size=12, weight="bold"), text_color=GREEN,
                         fg_color=GREEN_LIGHT).pack(side="left", padx=12, pady=8)

            btn_row = ctk.CTkFrame(notif, fg_color=GREEN_LIGHT)
            btn_row.pack(side="right", padx=8)
            ctk.CTkButton(btn_row, text="Open",
                          font=ctk.CTkFont(size=11), width=60, height=28, corner_radius=8,
                          fg_color=GREEN, hover_color=GREEN_HOVER, text_color=TEXT_PRIMARY,
                          command=lambda: open_file(fpath)).pack(side="left", padx=2)
            ctk.CTkButton(btn_row, text="Save As",
                          font=ctk.CTkFont(size=11), width=68, height=28, corner_radius=8,
                          fg_color=BG_SURFACE, hover_color=BORDER,
                          text_color=TEXT_SECONDARY, border_width=1, border_color=BORDER,
                          command=lambda: self._save_file_as(fpath)).pack(side="left", padx=2)

            # Inline image display
            if ext in IMAGE_EXTENSIONS:
                try:
                    pil = Image.open(fpath)
                    pil.thumbnail((340, 340))
                    ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil,
                                           size=(pil.width, pil.height))
                    self._img_refs.append(ctk_img)
                    img_frame = ctk.CTkFrame(self._chat_scroll,
                                             fg_color=BG_AI_MSG, corner_radius=14,
                                             border_width=1, border_color=BORDER)
                    img_frame.pack(fill="x", padx=40, pady=4)
                    ctk.CTkLabel(img_frame,
                                 text="Fly OS  ·  Generated Image",
                                 font=ctk.CTkFont(size=11, weight="bold"),
                                 text_color=GREEN, fg_color=BG_AI_MSG
                                 ).pack(anchor="w", padx=16, pady=(10, 4))
                    lbl = ctk.CTkLabel(img_frame, image=ctk_img, text="",
                                       fg_color=BG_AI_MSG, cursor="hand2")
                    lbl.pack(padx=16, pady=(0, 14))
                    lbl.bind("<Button-1>", lambda e: ImageViewer(self, fpath))
                except Exception:
                    pass

            # Video: show play button
            elif ext in VIDEO_EXTENSIONS:
                vid_frame = ctk.CTkFrame(self._chat_scroll, fg_color=BG_SURFACE,
                                          corner_radius=12, border_width=1,
                                          border_color=BORDER)
                vid_frame.pack(fill="x", padx=40, pady=4)
                ctk.CTkLabel(vid_frame,
                             text=f"🎬  Video: {fname}",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=ACCENT_2, fg_color=BG_SURFACE
                             ).pack(side="left", padx=12, pady=10)
                ctk.CTkButton(vid_frame, text="▶ Play",
                              font=ctk.CTkFont(size=12), width=80, height=32,
                              fg_color=ACCENT, hover_color=ACCENT_HOVER,
                              text_color=TEXT_PRIMARY, corner_radius=8,
                              command=lambda: open_file(fpath)
                              ).pack(side="right", padx=12, pady=8)

            self._scroll_bottom()
        self.after(0, _notify)

    # ── HISTORY ───────────────────────────────────────────────────────────────

    def _load_history_sidebar(self, sessions=None):
        if not self.client:
            return
        for w in self._hist_scroll.winfo_children():
            w.destroy()
        self.history_items.clear()
        if sessions is None:
            sessions = self.client.db.get_sessions(60)
        if not sessions:
            ctk.CTkLabel(self._hist_scroll, text="No chats yet",
                         font=ctk.CTkFont(size=11), text_color=TEXT_SIDEBAR_M,
                         fg_color=BG_SIDEBAR).pack(pady=16)
            return
        for s in sessions:
            item = HistoryItem(self._hist_scroll, session=s,
                               on_click=self._load_session,
                               on_delete=self._delete_session)
            item.pack(fill="x", pady=1)
            item.set_active(s["id"] == self.active_session)
            self.history_items[s["id"]] = item

    def _reload_history_sidebar(self):
        self._load_history_sidebar()

    def _search_history(self, _event=None):
        query = self._search_entry.get().strip()
        if not query or not self.client:
            self._load_history_sidebar()
            return
        results = self.client.db.search_sessions(query)
        self._load_history_sidebar(sessions=results)

    def _load_session(self, session_id: str):
        if not self.client:
            return
        self.active_session = session_id
        self.client.load_session(session_id)
        for w in self._chat_scroll.winfo_children():
            w.destroy()
        self._welcome_visible = False
        for turn in self.client.history:
            role = "user" if turn["role"] == "user" else "assistant"
            self._add_bubble(role, turn["content"])
        for sid, item in self.history_items.items():
            item.set_active(sid == session_id)
        self._scroll_bottom()

    def _delete_session(self, session_id: str):
        if not self.client:
            return
        if messagebox.askyesno("Delete", "Delete this conversation?", parent=self):
            self.client.db.delete_session(session_id)
            if session_id == self.active_session:
                self._new_chat()
            self._load_history_sidebar()

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _add_bubble(self, role: str, text: str = "",
                    images: list = None, engine: str = None) -> ChatBubble:
        eng = engine or self._active_engine
        bubble = ChatBubble(self._chat_scroll, role=role, text=text,
                            images=images or [], engine=eng)
        bubble.pack(fill="x", padx=40, pady=6)
        # Two-pass scroll: once to trigger layout, once after paint
        self.after(60,  self._scroll_bottom)
        self.after(200, self._scroll_bottom)
        return bubble

    def _set_busy(self, busy: bool):
        self.is_streaming = busy
        if busy:
            self._send_btn.configure(
                text="■ Stop",
                fg_color=RED,
                hover_color="#C0392B",
            )
        else:
            self._send_btn.configure(
                text="Send  ↑",
                fg_color=ACCENT,
                hover_color=ACCENT_HOVER,
            )

    def _scroll_bottom(self):
        try:
            self._chat_scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _update_engine_badge(self, engine: str):
        color, label, dot = ENGINE_META.get(engine, ENGINE_META["gemini"])
        labels = {
            "gemini":     "● Gemini 2.5 Flash",
            "openrouter": "● OpenRouter  Qwen3",
            "base44":     "● Base44 Agent",
        }
        self._engine_lbl.configure(
            text=labels.get(engine, f"● {label}"),
            text_color=color,
        )
        self._active_engine = engine

    def _save_file_as(self, src: str):
        dest = filedialog.asksaveasfilename(
            defaultextension=Path(src).suffix,
            initialfile=Path(src).name,
            filetypes=[("All files", "*.*")],
            parent=self,
        )
        if dest:
            shutil.copy2(src, dest)
            messagebox.showinfo("Saved", f"File saved to:\n{dest}", parent=self)

    def _new_chat(self):
        for w in self._chat_scroll.winfo_children():
            w.destroy()
        self._welcome_visible = False
        self._show_welcome()
        if self.client:
            self.client.new_session()
        self.active_session = None
        self._update_engine_badge("gemini")
        for item in self.history_items.values():
            item.set_active(False)

    def _clear_chat(self):
        self._new_chat()

    def _check_update(self):
        if not self.client:
            return
        update = self.client.check_for_update()
        if update:
            def _show():
                banner = ctk.CTkFrame(self._chat_scroll,
                                       fg_color=ORANGE_LIGHT, corner_radius=12,
                                       border_width=1, border_color=ORANGE)
                banner.pack(fill="x", padx=40, pady=8)
                ctk.CTkLabel(banner,
                             text=f"🚀  Update available: v{update['version']}",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=ORANGE, fg_color=ORANGE_LIGHT
                             ).pack(side="left", padx=12, pady=8)
                if "url" in update:
                    ctk.CTkButton(banner, text="Download",
                                  font=ctk.CTkFont(size=11), width=90, height=28,
                                  fg_color=ORANGE, hover_color=ACCENT_HOVER,
                                  text_color=TEXT_PRIMARY, corner_radius=8,
                                  command=lambda: open_file(update["url"])
                                  ).pack(side="right", padx=12)
            self.after(2000, _show)
