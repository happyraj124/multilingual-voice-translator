import threading
import customtkinter as ctk

from pipeline.speech_to_translation import (
    process_audio
)


class MainWindow:

    def __init__(self, model_manager):

        self.model_manager = model_manager

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()

        self.root.title(
            "Multilingual Voice Translator"
        )

        self.root.geometry("900x700")

        self.create_layout()

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

        worker = threading.Thread(
            target=self.run_pipeline_worker,
            daemon=True
        )

        worker.start()

    # ==========================
    # BACKGROUND WORKER
    # ==========================

    def run_pipeline_worker(self):

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

            source_text, translated_text, language = (
                process_audio(
                    self.model_manager,
                    status_callback=self.update_status
                )
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

    def run(self):

        self.root.mainloop()