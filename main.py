"""
Audiobook Generator Pro
An open-source, unlimited Text-to-Speech (TTS) desktop application that converts
PDF files and raw text into high-quality neural MP3 audiobooks using Edge-TTS.

Author: StructuralSensei
License: MIT
"""

import asyncio
import logging
import os
import threading
from typing import Dict, Optional

import customtkinter as ctk
import edge_tts
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from tkinter import filedialog, messagebox

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
APP_TITLE = "Audiobook Generator Pro"
WINDOW_SIZE = "720x680"
THEME_MODE = "System"  # Options: "System", "Dark", "Light"
COLOR_THEME = "blue"  # Options: "blue", "green", "dark-blue"

# Curated list of high-quality Microsoft Azure Neural Voices via Edge-TTS
NEURAL_VOICES: Dict[str, str] = {
    "Aria (US - Female)": "en-US-AriaNeural",
    "Guy (US - Male)": "en-US-GuyNeural",
    "Jenny (US - Female)": "en-US-JennyNeural",
    "Sonia (UK - Female)": "en-GB-SoniaNeural",
    "Ryan (UK - Male)": "en-GB-RyanNeural",
    "Natasha (Australia - Female)": "en-AU-NatashaNeural",
    "William (Australia - Male)": "en-AU-WilliamNeural"
}

# Configure logging for professional debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


class AudioBookApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        # Initialize internal application state tracking
        self.file_path: Optional[str] = None
        self.is_generating: bool = False

        # Configure window settings
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        ctk.set_appearance_mode(THEME_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        # Build the user interface
        self._setup_ui()
        logging.info("Application initialized successfully.")

    def _setup_ui(self) -> None:
        """Constructs the layout components of the application UI."""
        # Top Header Section
        self.title_label = ctk.CTkLabel(
            self,
            text=APP_TITLE,
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title_label.pack(pady=(25, 5))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Convert documents to premium audiobooks instantly",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 15))

        # Main Navigation Tab Container
        self.tabview = ctk.CTkTabview(self, width=620, height=260)
        self.tabview.pack(pady=10)

        self.tab_pdf = self.tabview.add("From PDF Document")
        self.tab_text = self.tabview.add("From Raw Text")

        # Layout inside 'From PDF Document' Tab
        self.select_btn = ctk.CTkButton(
            self.tab_pdf,
            text="Browse PDF File",
            command=self.select_file,
            height=35
        )
        self.select_btn.pack(pady=45)

        self.file_label = ctk.CTkLabel(
            self.tab_pdf,
            text="No source document selected",
            text_color="gray",
            font=ctk.CTkFont(slant="italic")
        )
        self.file_label.pack()

        # Layout inside 'From Raw Text' Tab
        self.text_input = ctk.CTkTextbox(self.tab_text, width=580, height=190)
        self.text_input.pack(pady=10)
        self.text_input.insert("0.0", "Paste or compose text directly here to test voice generation...")

        # Operational Settings Control Deck
        self.settings_frame = ctk.CTkFrame(self, width=620)
        self.settings_frame.pack(pady=15, fill="x", padx=50)

        # Voice Selector Dropdown
        self.voice_label = ctk.CTkLabel(self.settings_frame, text="Neural Voice profile:")
        self.voice_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.voice_dropdown = ctk.CTkComboBox(
            self.settings_frame,
            values=list(NEURAL_VOICES.keys()),
            width=220
        )
        self.voice_dropdown.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        self.voice_dropdown.set(list(NEURAL_VOICES.keys())[0])

        # Playback/Reading Speed Slider Controls
        self.speed_label = ctk.CTkLabel(self.settings_frame, text="Pacing Modulation:")
        self.speed_label.grid(row=0, column=2, padx=15, pady=15, sticky="e")

        # Edge-TTS shifts speech rate natively by percentages (-50% to +50%)
        self.speed_slider = ctk.CTkSlider(self.settings_frame, from_=-50, to=50, number_of_steps=20)
        self.speed_slider.set(0)
        self.speed_slider.grid(row=0, column=3, padx=15, pady=15, sticky="e")

        # Primary Trigger Action Engine Button
        self.generate_btn = ctk.CTkButton(
            self,
            text="Compile to Studio-Quality MP3",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_generation
        )
        self.generate_btn.pack(pady=20)

        # App Status Feed Footer Bar
        self.status_label = ctk.CTkLabel(
            self,
            text="Engine status: Standby • Cloud Access Active",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 15))

    def select_file(self) -> None:
        """Handles selection of filesystem PDF sources safely with explicit type validations."""
        try:
            chosen_path = filedialog.askopenfilename(filetypes=[("PDF Documents", "*.pdf")])
            if chosen_path:
                self.file_path = chosen_path
                filename = os.path.basename(self.file_path)
                self.file_label.configure(text=f"Target: {filename}", text_color=("#1F6AA5", "#A9CDEE"))
                logging.info(f"Target document set to: {self.file_path}")
        except Exception as err:
            logging.error(f"Error accessing system file manager: {err}")
            self.handle_runtime_error(f"Could not open file explorer. Context: {err}")

    def start_generation(self) -> None:
        """Validates current state constraints and triggers backend generation threads safely."""
        if self.is_generating:
            return

        self.status_label.configure(
            text="Pipeline Processing: Extracting text metrics...",
            text_color="#E67E22"
        )
        self.generate_btn.configure(state="disabled")
        self.is_generating = True

        # Decouple text processing and API requests from main GUI event loop
        threading.Thread(target=self._generation_worker, daemon=True).start()

    def _generation_worker(self) -> None:
        """Core background runner isolating heavy text extractions and network I/O blockages."""
        try:
            active_tab = self.tabview.get()
            raw_text = ""

            # --- SUB-ROUTINE: TEXT ACQUISITION ---
            if "PDF" in active_tab:
                if not self.file_path or not os.path.exists(self.file_path):
                    self.handle_runtime_error("No target PDF document is linked. Please pick a file.")
                    return

                try:
                    reader = PdfReader(self.file_path)
                    extracted_chunks = [page.extract_text() for page in reader.pages if page.extract_text()]
                    raw_text = "\n".join(extracted_chunks)

                    if not raw_text.strip():
                        self.handle_runtime_error("Extraction complete but returned empty string content.")
                        return

                except PdfReadError:
                    self.handle_runtime_error(
                        "The selected document structure appears corrupted or password-encrypted.")
                    return
                except Exception as err:
                    self.handle_runtime_error(f"System experienced errors compiling document: {err}")
                    return
            else:
                raw_text = self.text_input.get("0.0", "end").strip()
                if not raw_text:
                    self.handle_runtime_error("The raw text parsing queue is empty.")
                    return

            # --- SUB-ROUTINE: STORAGE ACQUISITION ---
            output_destination = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("Audio MP3 Tracks", "*.mp3")],
                title="Designate Output Asset Target Location"
            )

            if not output_destination:
                logging.info("User systematically aborted runtime file export.")
                self.status_label.configure(text="Engine status: Operation Aborted", text_color="gray")
                self.reset_ui()
                return

            # --- SUB-ROUTINE: RECONFIGURING CONTEXT SETTINGS ---
            selected_voice = self.voice_dropdown.get()
            voice_id = NEURAL_VOICES.get(selected_voice, "en-US-AriaNeural")

            rate_modifier = int(self.speed_slider.get())
            rate_string = f"{rate_modifier:+d}%"

            self.status_label.configure(text="Streaming data packets from Microsoft Neural Core...",
                                        text_color="#1F6AA5")
            logging.info(f"Initiating network audio pipeline utilizing: {voice_id} at pace {rate_string}")

            # --- SUB-ROUTINE: ASYNC PROCESSING PIPELINE ---
            asyncio.run(self._execute_tts_streaming(raw_text, voice_id, rate_string, output_destination))

            self.display_success_state(output_destination)

        except PermissionError:
            self.handle_runtime_error(
                "Access Denied to target file path. Verify the destination track file isn't open elsewhere.")
        except Exception as err:
            logging.critical(f"Critical framework fail track logged: {err}", exc_info=True)
            self.handle_runtime_error(f"System pipeline experienced a terminal exception: {err}")
        finally:
            self.reset_ui()

    async def _execute_tts_streaming(self, text: str, voice: str, rate: str, output_file: str) -> None:
        """Asynchronous execution channel wrapping the edge-tts communicator."""
        communicator = edge_tts.Communicate(text, voice, rate=rate)
        await communicator.save(output_file)

    def handle_runtime_error(self, message: str) -> None:
        """Thread-safe UI warning reporting abstraction layer."""
        logging.warning(f"Application Runtime Exception Displayed: {message}")
        self.status_label.configure(text="Pipeline Status: Error Blocked", text_color="#E74C3C")
        messagebox.showerror("Execution Halt", message)
        self.reset_ui()

    def display_success_state(self, file_path: str) -> None:
        """Dispatches an elegant confirmation system dialogue."""
        filename = os.path.basename(file_path)
        logging.info(f"Audio book output cleanly exported to: {file_path}")
        self.status_label.configure(text=f"Completed Asset compilation: {filename}", text_color="#2ECC71")
        messagebox.showinfo("Compilation Success", f"Audiobook asset generation successfully finalized:\n\n{filename}")

    def reset_ui(self) -> None:
        """Restores control state interactions to active status."""
        self.is_generating = False
        self.generate_btn.configure(state="normal")


if __name__ == "__main__":
    app = AudioBookApp()
    app.mainloop()