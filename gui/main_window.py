import threading
import customtkinter as ctk
from translation.languages import LANGUAGES

from history.history_manager import (
    HistoryManager
)

from translation.language_manager import (
    LanguageManager
)

from pipeline.speech_to_translation import (
    process_audio
)
from streaming.stream_manager import (
    StreamManager
)

class MainWindow:

    def __init__(self, model_manager):

        self.model_manager = model_manager
        self.history_manager = HistoryManager()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()

        self.root.title(
            "Multilingual Voice Translator"
        )

        self.root.geometry("900x700")

        self.create_layout()

        self.stream_manager = None

    def create_layout(self):

        # Header Frame

        self.header_frame = ctk.CTkFrame(
            self.root
        )

        self.header_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # Control Frame

        self.control_frame = ctk.CTkFrame(
            self.root
        )

        self.control_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # Source Frame

        self.source_frame = ctk.CTkFrame(
            self.root
        )

        self.source_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Translation Frame

        self.translation_frame = ctk.CTkFrame(
            self.root
        )

        self.translation_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Status Frame

        self.status_frame = ctk.CTkFrame(
            self.root
        )

        self.status_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.create_widgets()

    def create_widgets(self):

        # ==========================
        # Title
        # ==========================

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Multilingual Voice Translator",
            font=("Arial", 28, "bold")
        )

        self.title_label.pack(
            pady=10
        )

        # ==========================
        # Language Selection
        # ==========================

        self.language_frame = ctk.CTkFrame(
            self.control_frame
        )

        self.language_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.source_lang_menu = ctk.CTkOptionMenu(
            self.language_frame,
            values=[
                "Auto Detect",
                "Hindi",
                "English",
                "Urdu",
                "Spanish",
                "French"
            ]
        )
        self.source_lang_menu.set(
            "Auto Detect"
        )

        self.source_lang_menu.pack(
            side="left",
            padx=10,
            pady=10
        )

        self.target_lang_menu = ctk.CTkOptionMenu(
            self.language_frame,
            values=[
                "English",
                "Hindi",
                "Urdu",
                "Spanish",
                "French"
            ]
        )

        self.target_lang_menu.set(
            "English"
        )

        self.target_lang_menu.pack(
            side="left",
            padx=10,
            pady=10
        )

        # ==========================
        # Buttons
        # ==========================

        self.button_frame = ctk.CTkFrame(
            self.control_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(
            pady=10
        )

        self.record_button = ctk.CTkButton(
            self.button_frame,
            text="🎤 Start Recording",
            width=220,
            height=45,
            command=self.start_recording
        )

        self.record_button.pack(
            side="left",
            padx=10
        )
        self.start_live_button = (
            ctk.CTkButton(
                self.button_frame,
                text="🟢 Live Start",
                width=150,
                height=45,
                command=self.start_live_translation
            )
        )

        self.start_live_button.pack(
            side="left",
            padx=10
        )

        self.stop_live_button = (
            ctk.CTkButton(
                self.button_frame,
                text="🔴 Live Stop",
                width=150,
                height=45,
                command=self.stop_live_translation
            )
        )

        self.stop_live_button.pack(
            side="left",
            padx=10
        )

        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="🗑 Clear",
            width=120,
            height=45,
            command=self.clear_text
        )

        self.clear_button.pack(
            side="left",
            padx=10
        )
        self.history_button = ctk.CTkButton(
        self.button_frame,
        text="📜 History",
        width=120,
        height=45,
        command=self.show_history
    )

        self.history_button.pack(
            side="left",
            padx=10
    )

        self.export_button = ctk.CTkButton(
            self.button_frame,
            text="💾 Export",
            width=120,
            height=45,
            command=self.export_history
        )

        self.export_button.pack(
            side="left",
            padx=10
        )

        # ==========================
        # Source Text
        # ==========================

        self.source_label = ctk.CTkLabel(
            self.source_frame,
            text="Source Text"
        )

        self.source_label.pack(
            anchor="w",
            padx=10,
            pady=5
        )

        self.source_textbox = ctk.CTkTextbox(
            self.source_frame,
            height=120
        )

        self.source_textbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        # ==========================
        # Translation Text
        # ==========================

        self.translation_label = ctk.CTkLabel(
            self.translation_frame,
            text="Translation"
        )

        self.translation_label.pack(
            anchor="w",
            padx=10,
            pady=5
        )

        self.translation_textbox = ctk.CTkTextbox(
            self.translation_frame,
            height=120
        )

        self.translation_textbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        # ==========================
        # Progress Bar
        # ==========================

        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame
        )

        self.progress_bar.pack(
            fill="x",
            padx=10,
            pady=(10, 5)
        )

        self.progress_bar.set(0)

        # ==========================
        # Status Label
        # ==========================

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Ready"
        )

        self.status_label.pack(
            anchor="w",
            padx=10,
            pady=10
        )

    # ==========================
    # THREAD SAFE METHODS
    # ==========================

    def update_status(self, message):

        self.root.after(
            0,
            lambda:
            self.status_label.configure(
                text=f"Status: {message}"
            )
        )

    def update_progress(self, value):

        self.root.after(
            0,
            lambda:
            self.progress_bar.set(value)
        )

    def update_textboxes(
        self,
        source_text,
        translated_text
    ):

        self.source_textbox.delete(
            "1.0",
            "end"
        )

        self.translation_textbox.delete(
            "1.0",
            "end"
        )

        self.source_textbox.insert(
            "1.0",
            source_text
        )

        self.translation_textbox.insert(
            "1.0",
            translated_text
        )

    # ==========================
    # CLEAR BUTTON
    # ==========================

    def clear_text(self):

        self.source_textbox.delete(
            "1.0",
            "end"
        )

        self.translation_textbox.delete(
            "1.0",
            "end"
        )

        self.progress_bar.set(0)

        self.update_status(
            "Ready"
        )

    # ==========================
    # RECORD BUTTON
    # ==========================

    def start_recording(self):

        self.record_button.configure(
            state="disabled"
        )

        self.progress_bar.set(0)

        source_language = (
            self.source_lang_menu.get()
        )

        target_language = (
            self.target_lang_menu.get()
        )

        worker = threading.Thread(
            target=self.run_pipeline_worker,
            args=(
                source_language,
                target_language
            ),
            daemon=True
        )

        worker.start()

    # ==========================
    # BACKGROUND WORKER
    # ==========================

    def run_pipeline_worker(
    self,
    source_language,
    target_language
):

        try:

            self.root.after(
                0,
                lambda:
                self.update_textboxes(
                    "",
                    ""
                )
            )

            self.update_progress(0.1)

            # Auto Detect support

            if source_language == "Auto Detect":

                source_lang_code = None

            else:

                source_lang_code = (
                    LanguageManager.get_code(
                        source_language
                    )
                )

            target_lang_code = (
                LanguageManager.get_code(
                    target_language
                )
            )

            source_text, translated_text, language = (
                process_audio(
                    self.model_manager,
                    source_lang=source_lang_code,
                    target_lang=target_lang_code,
                    status_callback=self.update_status
                )
            )
            self.history_manager.add_record(
                source_language=source_language,
                target_language=target_language,
                source_text=source_text,
                translated_text=translated_text
            )

            self.update_progress(0.8)

            self.root.after(
                0,
                lambda:
                self.update_textboxes(
                    source_text,
                    translated_text
                )
            )

            self.update_progress(1.0)

            self.update_status(
                f"Completed ({language})"
            )

        except Exception as e:

            self.update_status(
                f"Error: {e}"
            )

        finally:

            self.root.after(
                0,
                lambda:
                self.record_button.configure(
                    state="normal"
                )
            )
    def show_history(self):

        popup = ctk.CTkToplevel(
            self.root
        )

        popup.title(
            "Translation History"
        )

        popup.geometry(
            "900x600"
        )

        textbox = ctk.CTkTextbox(
            popup
        )

        textbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        history = (
            self.history_manager.get_history()
        )

        if not history:

            textbox.insert(
                "end",
                "No history available."
            )

            textbox.configure(
                state="disabled"
            )

            return

        for item in history:

            textbox.insert(
                "end",
                f"""
    ==================================================

    Time:
    {item['timestamp']}

    {item['source_language']}
    →
    {item['target_language']}

    Source:
    {item['source_text']}

    Translation:
    {item['translated_text']}

    """
            )

        textbox.configure(
            state="disabled"
        )

    def export_history(self):

        filename = (
            self.history_manager.export_csv()
        )

        self.update_status(
            f"Exported: {filename}"
        )

    def start_live_translation(self):

        if self.stream_manager:
            return

        target_language = (
            self.target_lang_menu.get()
        )

        target_code = (
            LanguageManager.get_code(
                target_language
            )
        )

        self.stream_manager = (
            StreamManager(
                self.model_manager,
                target_code
            )
        )

        self.stream_manager.start_streaming()

        self.update_status(
            "Live Streaming"
        )

        self.update_live_display()


    def stop_live_translation(self):

        if not self.stream_manager:
            return

        self.stream_manager.stop_streaming()

        self.stream_manager = None

        self.update_status(
            "Live Stopped"
        )


    def update_live_display(self):

        if not self.stream_manager:
            return

        try:

            while (
                not self.stream_manager
                .transcript_queue.empty()
            ):

                text = (
                    self.stream_manager
                    .transcript_queue.get()
                )

                self.source_textbox.insert(
                    "end",
                    text + "\n"
                )

            while (
                not self.stream_manager
                .translation_display_queue
                .empty()
            ):

                text = (
                    self.stream_manager
                    .translation_display_queue
                    .get()
                )

                self.translation_textbox.insert(
                    "end",
                    text + "\n"
                )

        except:
            pass

        self.root.after(
            100,
            self.update_live_display
        )

    def run(self):

        self.root.mainloop()