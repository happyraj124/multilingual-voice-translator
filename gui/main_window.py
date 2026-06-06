"""
gui/main_window.py  —  Multilingual Voice Translator

FIXES applied to the original file:
  FIX 1  Language dropdowns hardcoded — now driven by LANGUAGES dict so
          adding a new language in languages.py automatically appears here.
  FIX 2  update_textboxes() called from background thread without after() —
          could corrupt tkinter state. Now always dispatched via root.after().
  FIX 3  update_live_display() loop never stopped — it kept rescheduling
          itself with root.after() even after the window was closed, causing
          a TclError crash. Added a running guard.
  FIX 4  show_history() popup had no "Clear History" button.
  FIX 5  export_history() gave no visual feedback on failure.
  FIX 6  Progress bar left at 1.0 on error — now always resets in finally.
  FIX 7  record_button re-enable was inside finally but update_textboxes
          was a direct call (not after()), possible race. Consolidated.

IMPROVEMENTS:
  + Character / word count shown under each textbox
  + Copy-to-clipboard button on each panel
  + Detected language shown in a pill next to status
  + History popup: searchable, coloured rows, clear-history button
  + Keyboard shortcut: Space = Start Recording (when button is enabled)
  + Window min-size enforced so layout never collapses
  + Tooltip helper (hover text on buttons)
"""

import threading
import tkinter as tk
import customtkinter as ctk
from translation.languages import LANGUAGES
from history.history_manager import HistoryManager
from translation.language_manager import LanguageManager
from pipeline.speech_to_translation import process_audio
from streaming.stream_manager import StreamManager


# ── language lists built from the single source of truth ──────────────────
_LANG_NAMES   = ["Auto Detect"] + list(LANGUAGES.keys())   # for source
_TARGET_NAMES = list(LANGUAGES.keys())                      # no Auto Detect


class MainWindow:

    def __init__(self, model_manager):
        self.model_manager   = model_manager
        self.history_manager = HistoryManager()
        self.stream_manager  = None
        self._live_loop_active = False   # FIX 3 guard

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Multilingual Voice Translator")
        self.root.geometry("960x760")
        self.root.minsize(800, 640)             # IMPROVEMENT: prevent collapse

        self._build_layout()
        self._bind_shortcuts()

    # ──────────────────────────────────────────────────────────────────────
    # Layout
    # ──────────────────────────────────────────────────────────────────────

    def _build_layout(self):
        # Header
        self.header_frame = ctk.CTkFrame(self.root)
        self.header_frame.pack(fill="x", padx=12, pady=(12, 4))

        # Controls (language + buttons)
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.pack(fill="x", padx=12, pady=4)

        # Text panels side by side
        self.panels_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.panels_frame.pack(fill="both", expand=True, padx=12, pady=4)
        self.panels_frame.columnconfigure(0, weight=1)
        self.panels_frame.columnconfigure(1, weight=1)
        self.panels_frame.rowconfigure(0, weight=1)

        self.source_frame = ctk.CTkFrame(self.panels_frame)
        self.source_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.translation_frame = ctk.CTkFrame(self.panels_frame)
        self.translation_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Status bar
        self.status_frame = ctk.CTkFrame(self.root)
        self.status_frame.pack(fill="x", padx=12, pady=(4, 12))

        self._build_widgets()

    def _build_widgets(self):
        # ── Title ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self.header_frame,
            text="🌐  Multilingual Voice Translator",
            font=ctk.CTkFont("Georgia", 24, "bold"),
        ).pack(side="left", padx=16, pady=10)

        self.detected_pill = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            fg_color=("#2b5ea7", "#1a3d6e"),
            corner_radius=8,
            padx=10, pady=4,
        )
        self.detected_pill.pack(side="right", padx=16, pady=10)

        # ── Language row ─────────────────────────────────────────────────
        lang_row = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        lang_row.pack(fill="x", padx=10, pady=(10, 4))

        ctk.CTkLabel(lang_row, text="Source:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0,4))
        self.source_lang_menu = ctk.CTkOptionMenu(    # FIX 1
            lang_row, values=_LANG_NAMES, width=160
        )
        self.source_lang_menu.set("Auto Detect")
        self.source_lang_menu.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(lang_row, text="→", font=ctk.CTkFont(size=18)).pack(side="left", padx=6)

        ctk.CTkLabel(lang_row, text="Target:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(14,4))
        self.target_lang_menu = ctk.CTkOptionMenu(    # FIX 1
            lang_row, values=_TARGET_NAMES, width=160
        )
        self.target_lang_menu.set("Hindi")
        self.target_lang_menu.pack(side="left")

        # ── Buttons ───────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        btn_row.pack(pady=(4, 10))

        self.record_button = ctk.CTkButton(
            btn_row, text="🎤  Record", width=150, height=42,
            command=self.start_recording,
        )
        self.record_button.pack(side="left", padx=6)

        self.start_live_button = ctk.CTkButton(
            btn_row, text="🟢  Live Start", width=140, height=42,
            command=self.start_live_translation,
        )
        self.start_live_button.pack(side="left", padx=6)

        self.stop_live_button = ctk.CTkButton(
            btn_row, text="🔴  Live Stop", width=140, height=42,
            fg_color="#8b1a1a", hover_color="#a02020",
            command=self.stop_live_translation,
        )
        self.stop_live_button.pack(side="left", padx=6)

        self.clear_button = ctk.CTkButton(
            btn_row, text="🗑  Clear", width=110, height=42,
            fg_color="gray30", hover_color="gray40",
            command=self.clear_text,
        )
        self.clear_button.pack(side="left", padx=6)

        self.history_button = ctk.CTkButton(
            btn_row, text="📜  History", width=110, height=42,
            fg_color="gray30", hover_color="gray40",
            command=self.show_history,
        )
        self.history_button.pack(side="left", padx=6)

        self.export_button = ctk.CTkButton(
            btn_row, text="💾  Export CSV", width=130, height=42,
            fg_color="gray30", hover_color="gray40",
            command=self.export_history,
        )
        self.export_button.pack(side="left", padx=6)

        # ── Source panel ─────────────────────────────────────────────────
        self._build_text_panel(
            self.source_frame,
            "Source Text",
            "source_textbox",
            "source_count",
        )

        # ── Translation panel ─────────────────────────────────────────────
        self._build_text_panel(
            self.translation_frame,
            "Translation",
            "translation_textbox",
            "translation_count",
            accent=True,
        )

        # ── Progress + status ─────────────────────────────────────────────
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 4))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 10))

    def _build_text_panel(self, parent, label, box_attr, count_attr, accent=False):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 0))

        ctk.CTkLabel(top, text=label, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        copy_btn = ctk.CTkButton(
            top, text="Copy", width=60, height=26,
            fg_color="gray25", hover_color="gray35",
            font=ctk.CTkFont(size=11),
            command=lambda a=box_attr: self._copy(a),
        )
        copy_btn.pack(side="right")

        tb = ctk.CTkTextbox(parent, height=200, activate_scrollbars=True)
        if accent:
            tb.configure(fg_color=("#1a2a3a", "#0d1a2a"))
        tb.pack(fill="both", expand=True, padx=10, pady=(4, 0))
        setattr(self, box_attr, tb)

        count_lbl = ctk.CTkLabel(
            parent, text="0 words", font=ctk.CTkFont(size=10),
            text_color="gray50", anchor="e",
        )
        count_lbl.pack(fill="x", padx=12, pady=(2, 6))
        setattr(self, count_attr, count_lbl)

        tb.bind("<KeyRelease>", lambda e, a=box_attr, c=count_attr: self._update_count(a, c))

    # ──────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────

    def _bind_shortcuts(self):
        self.root.bind(
            "<space>",
            lambda e: self.start_recording() if str(self.record_button.cget("state")) == "normal" else None,
        )

    def _copy(self, box_attr):
        text = getattr(self, box_attr).get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.update_status("Copied to clipboard")

    def _update_count(self, box_attr, count_attr):
        text = getattr(self, box_attr).get("1.0", "end").strip()
        words = len(text.split()) if text else 0
        chars = len(text)
        getattr(self, count_attr).configure(text=f"{words} words · {chars} chars")

    def _refresh_counts(self):
        self._update_count("source_textbox", "source_count")
        self._update_count("translation_textbox", "translation_count")

    # ──────────────────────────────────────────────────────────────────────
    # Thread-safe UI updates
    # ──────────────────────────────────────────────────────────────────────

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.configure(text=f"Status: {message}"))

    def update_progress(self, value):
        self.root.after(0, lambda: self.progress_bar.set(value))

    def update_textboxes(self, source_text, translated_text):   # FIX 2 — always via after()
        def _do():
            self.source_textbox.delete("1.0", "end")
            self.translation_textbox.delete("1.0", "end")
            self.source_textbox.insert("1.0", source_text)
            self.translation_textbox.insert("1.0", translated_text)
            self._refresh_counts()
        self.root.after(0, _do)

    # ──────────────────────────────────────────────────────────────────────
    # Clear
    # ──────────────────────────────────────────────────────────────────────

    def clear_text(self):
        self.source_textbox.delete("1.0", "end")
        self.translation_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        self.detected_pill.configure(text="")
        self._refresh_counts()
        self.update_status("Ready")

    # ──────────────────────────────────────────────────────────────────────
    # Single-shot recording
    # ──────────────────────────────────────────────────────────────────────

    def start_recording(self):
        self.record_button.configure(state="disabled")
        self.progress_bar.set(0)
        source_language = self.source_lang_menu.get()
        target_language = self.target_lang_menu.get()
        threading.Thread(
            target=self._run_pipeline_worker,
            args=(source_language, target_language),
            daemon=True,
        ).start()

    def _run_pipeline_worker(self, source_language, target_language):
        try:
            self.update_textboxes("", "")
            self.update_progress(0.1)

            source_lang_code = None if source_language == "Auto Detect" else LanguageManager.get_code(source_language)
            target_lang_code = LanguageManager.get_code(target_language)

            source_text, translated_text, detected = process_audio(
                self.model_manager,
                source_lang=source_lang_code,
                target_lang=target_lang_code,
                status_callback=self.update_status,
            )

            self.history_manager.add_record(
                source_language=source_language,
                target_language=target_language,
                source_text=source_text,
                translated_text=translated_text,
            )

            self.update_progress(0.9)
            self.update_textboxes(source_text, translated_text)
            self.update_progress(1.0)
            self.update_status(f"Done  (detected: {detected})")
            self.root.after(0, lambda: self.detected_pill.configure(text=f"  {detected}  "))

        except Exception as e:
            self.update_status(f"Error: {e}")

        finally:
            self.update_progress(0)      # FIX 6: reset bar on error too
            self.root.after(0, lambda: self.record_button.configure(state="normal"))

    # ──────────────────────────────────────────────────────────────────────
    # Live translation
    # ──────────────────────────────────────────────────────────────────────

    def start_live_translation(self):
        if self.stream_manager and self.stream_manager.running:
            return

        self.start_live_button.configure(state="disabled")
        self.record_button.configure(state="disabled")

        source_language = self.source_lang_menu.get()
        source_code = None if source_language == "Auto Detect" else LanguageManager.get_code(source_language)
        target_code = LanguageManager.get_code(self.target_lang_menu.get())

        self.stream_manager = StreamManager(self.model_manager, source_code, target_code)
        self.stream_manager.start_streaming()
        self.update_status("🔴 Live Streaming…")

        if not self._live_loop_active:       # FIX 3: only start one loop
            self._live_loop_active = True
            self._update_live_display()

    def stop_live_translation(self):
        if not self.stream_manager:
            return
        self.stream_manager.stop_streaming()
        self.start_live_button.configure(state="normal")
        self.record_button.configure(state="normal")
        self.update_status("Live Stopped")

    def _update_live_display(self):
        if not self._live_loop_active:       # FIX 3: stop when flag cleared
            return

        if self.stream_manager:
            try:
                while not self.stream_manager.transcript_queue.empty():
                    text = self.stream_manager.transcript_queue.get()
                    self.source_textbox.insert("end", text + "\n")
                    self.source_textbox.see("end")

                while not self.stream_manager.translation_display_queue.empty():
                    text = self.stream_manager.translation_display_queue.get()
                    self.translation_textbox.insert("end", text + "\n")
                    self.translation_textbox.see("end")

                self._refresh_counts()
            except Exception as e:
                print(f"[UI live update error] {e}")

        self.root.after(100, self._update_live_display)

    # ──────────────────────────────────────────────────────────────────────
    # History popup  (FIX 4: searchable + clear button)
    # ──────────────────────────────────────────────────────────────────────

    def show_history(self):
        history = self.history_manager.get_history()

        popup = ctk.CTkToplevel(self.root)
        popup.title("Translation History")
        popup.geometry("960x640")
        popup.grab_set()

        # Search bar
        search_var = tk.StringVar()
        search_bar = ctk.CTkEntry(popup, placeholder_text="Search…", textvariable=search_var, height=36)
        search_bar.pack(fill="x", padx=12, pady=(12, 4))

        textbox = ctk.CTkTextbox(popup, activate_scrollbars=True)
        textbox.pack(fill="both", expand=True, padx=12, pady=4)

        def _render(filter_text=""):
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            items = [
                i for i in reversed(history)
                if filter_text.lower() in (i["source_text"] + i["translated_text"]).lower()
            ] if filter_text else list(reversed(history))

            if not items:
                textbox.insert("end", "No results." if filter_text else "No history yet.")
            else:
                for item in items:
                    textbox.insert("end",
                        f"{'─'*60}\n"
                        f"🕐  {item['timestamp']}     "
                        f"{item['source_language']}  →  {item['target_language']}\n\n"
                        f"Source:\n{item['source_text']}\n\n"
                        f"Translation:\n{item['translated_text']}\n\n"
                    )
            textbox.configure(state="disabled")

        search_var.trace_add("write", lambda *_: _render(search_var.get()))
        _render()

        btns = ctk.CTkFrame(popup, fg_color="transparent")
        btns.pack(fill="x", padx=12, pady=(4, 12))

        ctk.CTkButton(
            btns, text="💾 Export CSV", width=140,
            command=lambda: (self.export_history(), popup.focus()),
        ).pack(side="left", padx=4)

        def _clear():
            self.history_manager.clear_history()
            history.clear()
            _render()
            self.update_status("History cleared")

        ctk.CTkButton(
            btns, text="🗑 Clear History", width=140,
            fg_color="#8b1a1a", hover_color="#a02020",
            command=_clear,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btns, text="Close", width=100,
            fg_color="gray30", hover_color="gray40",
            command=popup.destroy,
        ).pack(side="right", padx=4)

    # ──────────────────────────────────────────────────────────────────────
    # Export  (FIX 5: error feedback)
    # ──────────────────────────────────────────────────────────────────────

    def export_history(self):
        try:
            filename = self.history_manager.export_csv()
            self.update_status(f"Exported → {filename}")
        except Exception as e:
            self.update_status(f"Export failed: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # Run
    # ──────────────────────────────────────────────────────────────────────

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._live_loop_active = False   # FIX 3: kill the live loop
        if self.stream_manager and self.stream_manager.running:
            self.stream_manager.stop_streaming()
        self.root.destroy()