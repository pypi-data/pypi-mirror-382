import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

from local_whisper_korean_subtitle_generator.tools.korean_translation_tool import KoreanTranslationTool
from local_whisper_korean_subtitle_generator.tools.srt_formatter_tool import SRTFormatterTool


class IntegratedSRTGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Integrated SRT Subtitle Generator")
        self.root.geometry("800x700")

        self.model_options = [
            "tiny", "base", "small", "medium", "large", "large-v2", "large-v3"
        ]

        self.language_options = [
            "auto", "ko", "en", "ja", "zh", "es", "fr", "de", "it", "pt", "ru", "ar"
        ]

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="Integrated SRT Subtitle Generator", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        self.progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        self.progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        self.step1_label = ttk.Label(self.progress_frame, text="1. Transcription", foreground="gray")
        self.step1_label.grid(row=0, column=0, padx=5)
        self.step2_label = ttk.Label(self.progress_frame, text="2. Translation", foreground="gray")
        self.step2_label.grid(row=0, column=1, padx=5)
        self.step3_label = ttk.Label(self.progress_frame, text="3. SRT Generation", foreground="gray")
        self.step3_label.grid(row=0, column=2, padx=5)
        self.step4_label = ttk.Label(self.progress_frame, text="4. Done", foreground="gray")
        self.step4_label.grid(row=0, column=3, padx=5)

        config_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(config_frame, text="Whisper model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(config_frame, textvariable=self.model_var, values=self.model_options, state="readonly")
        model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        ttk.Label(config_frame, text="Language:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.language_var = tk.StringVar(value="auto")
        language_combo = ttk.Combobox(config_frame, textvariable=self.language_var, values=self.language_options, state="readonly")
        language_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        ttk.Label(config_frame, text="Translation engine:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(config_frame, text="OpenAI (fixed)").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        ttk.Label(config_frame, text="OpenAI API key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.openai_key_var = tk.StringVar(value=os.getenv("OPENAI_API_KEY", ""))
        openai_entry = ttk.Entry(config_frame, textvariable=self.openai_key_var, width=50, show="*")
        openai_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(config_frame, text="Save", command=self.save_openai_key).grid(row=2, column=3, padx=(10, 0))

        file_frame = ttk.LabelFrame(main_frame, text="File selection", padding="10")
        file_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(file_frame, text="Input file:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path_var = tk.StringVar(value="")
        input_entry = ttk.Entry(file_frame, textvariable=self.input_path_var, width=50)
        input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(file_frame, text="Browse", command=self.select_input_file).grid(row=0, column=2, padx=(10, 0))

        ttk.Label(file_frame, text="Output folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path_var = tk.StringVar(value=str(Path.cwd() / "output"))
        output_entry = ttk.Entry(file_frame, textvariable=self.output_path_var, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Button(file_frame, text="Browse", command=self.select_output_folder).grid(row=1, column=2, padx=(10, 0))

        self.progress_var = tk.StringVar(value="Idle...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=0, columnspan=3, pady=5)

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.log_text = tk.Text(log_frame, height=8, width=80)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        self.start_button = ttk.Button(button_frame, text="Start full process", command=self.start_full_process)
        self.start_button.grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Transcription only", command=self.start_transcription_only).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Translation only", command=self.start_translation_only).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).grid(row=0, column=3, padx=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        file_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def select_input_file(self):
        filetypes = [
            ("All media files", "*.mp4;*.mp3;*.wav;*.m4a;*.avi;*.mov;*.mkv"),
            ("Video files", "*.mp4;*.avi;*.mov;*.mkv"),
            ("Audio files", "*.mp3;*.wav;*.m4a"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
        if filename:
            self.input_path_var.set(filename)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_path_var.set(folder)

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def setup_api_keys(self) -> bool:
        try:
            if self.openai_key_var.get():
                os.environ['OPENAI_API_KEY'] = self.openai_key_var.get().strip()
            key = os.getenv('OPENAI_API_KEY')
            if key:
                self.log_message(f"Loaded OpenAI API key: {key[:10]}...")
                return True
            self.log_message("Error: OpenAI API key is missing. Enter it above and click Save.")
            return False
        except Exception as e:
            self.log_message(f"Error: Failed to load API key - {str(e)}")
            return False

    def save_openai_key(self):
        try:
            key = (self.openai_key_var.get() or '').strip()
            if not key:
                messagebox.showerror("Error", "Please enter a valid OpenAI API key.")
                return
            os.environ['OPENAI_API_KEY'] = key
            self.log_message("OpenAI API key saved to environment")
            messagebox.showinfo("Done", "OpenAI API key saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")

    def update_progress(self, step, status="In progress"):
        steps = [self.step1_label, self.step2_label, self.step3_label, self.step4_label]
        colors = {"In progress": "orange", "Done": "green", "Idle": "gray"}
        for i, step_label in enumerate(steps):
            if i < step:
                step_label.config(foreground=colors["Done"])
            elif i == step:
                step_label.config(foreground=colors[status])
            else:
                step_label.config(foreground=colors["Idle"])

    def start_full_process(self):
        if not self.input_path_var.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return
        if not self.setup_api_keys():
            messagebox.showerror("Error", "API key not found. Please set OPENAI_API_KEY.")
            return
        self.start_button.config(state='disabled')
        self.progress_bar.start()
        thread = threading.Thread(target=self.run_full_process)
        thread.daemon = True
        thread.start()

    def start_transcription_only(self):
        if not self.input_path_var.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return
        self.start_button.config(state='disabled')
        self.progress_bar.start()
        thread = threading.Thread(target=self.run_transcription_only)
        thread.daemon = True
        thread.start()

    def start_translation_only(self):
        if not self.setup_api_keys():
            messagebox.showerror("Error", "API key not found. Please set OPENAI_API_KEY.")
            return
        json_file = filedialog.askopenfilename(
            title="Select JSON file to translate",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not json_file:
            return
        self.start_button.config(state='disabled')
        self.progress_bar.start()
        thread = threading.Thread(target=self.run_translation_only, args=(json_file,))
        thread.daemon = True
        thread.start()

    def run_full_process(self):
        try:
            self.log_message("=== Step 1: Transcription started ===")
            self.update_progress(0, "In progress")
            self.progress_var.set("Transcribing...")
            json_path = self.run_transcription()
            if not json_path:
                return
            self.log_message("=== Steps 2-3: Translation and SRT generation ===")
            self.update_progress(1, "In progress")
            self.progress_var.set("Translating and generating SRT...")
            srt_path = self.run_translation_and_srt(json_path)
            if not srt_path:
                return
            self.log_message("=== Full process completed ===")
            self.update_progress(3, "Done")
            self.progress_var.set("Done!")
            messagebox.showinfo("Done", "SRT subtitle file has been created!")
        except Exception as e:
            self.log_message(f"Error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")
        finally:
            self.start_button.config(state='normal')
            self.progress_bar.stop()

    def run_transcription_only(self):
        try:
            self.log_message("=== Transcription started ===")
            self.update_progress(0, "In progress")
            self.progress_var.set("Transcribing...")
            json_path = self.run_transcription()
            if json_path:
                self.log_message("=== Transcription completed ===")
                self.update_progress(0, "Done")
                self.progress_var.set("Transcription completed!")
                messagebox.showinfo("Done", f"Transcription completed!\nTemporary file: {json_path}")
        except Exception as e:
            self.log_message(f"Error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during transcription: {str(e)}")
        finally:
            self.start_button.config(state='normal')
            self.progress_bar.stop()

    def run_translation_only(self, json_path):
        try:
            self.log_message("=== Translation started ===")
            self.update_progress(1, "In progress")
            self.progress_var.set("Translating...")
            srt_path = self.run_translation_and_srt(json_path)
            if srt_path:
                self.log_message("=== Translation completed ===")
                self.update_progress(2, "Done")
                self.progress_var.set("SRT generation completed!")
                messagebox.showinfo("Done", "SRT subtitle file has been created!")
        except Exception as e:
            self.log_message(f"Error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during translation: {str(e)}")
        finally:
            self.start_button.config(state='normal')
            self.progress_bar.stop()

    def run_transcription(self):
        try:
            import whisper
            self.log_message("Loading Whisper model...")
            model_name = self.model_var.get()
            model = whisper.load_model(model_name)
            self.log_message(f"Model '{model_name}' loaded")
            self.log_message("Starting transcription...")
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            result = model.transcribe(
                self.input_path_var.get(),
                language=language,
                verbose=True
            )
            self.log_message("Transcription completed")
            self.log_message("Saving JSON file...")
            input_path = Path(self.input_path_var.get())
            output_filename = input_path.stem + ".json"
            output_path = Path(self.output_path_var.get()) / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            self.log_message(f"Temporary JSON saved: {output_path}")
            return str(output_path)
        except Exception as e:
            self.log_message(f"Transcription error: {str(e)}")
            return None

    def run_translation_and_srt(self, json_path):
        try:
            if not self.setup_api_keys():
                return None
            os.environ["TRANSLATION_PROVIDER"] = "openai"
            self.log_message("Translation engine: openai")
            self.log_message("Starting translation/formatting tools...")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            segments = None
            if isinstance(data, list):
                segments = data
            elif isinstance(data, dict):
                raw_segments = None
                if isinstance(data.get('segments'), list):
                    raw_segments = data.get('segments')
                elif isinstance(data.get('results'), list):
                    raw_segments = data.get('results')
                if isinstance(raw_segments, list):
                    segments = []
                    for seg in raw_segments:
                        if not isinstance(seg, dict):
                            continue
                        text = seg.get('text', '')
                        start = float(seg.get('start', 0.0)) if seg.get('start') is not None else 0.0
                        end = float(seg.get('end', 0.0)) if seg.get('end') is not None else 0.0
                        segments.append({"text": text, "start": start, "end": end})
            if not isinstance(segments, list):
                self.log_message("Error: Input JSON is not a list of segments.")
                return None
            translator_tool = KoreanTranslationTool()
            translated_json = translator_tool._run(json.dumps(segments, ensure_ascii=False))
            try:
                parsed_translated = json.loads(translated_json) if isinstance(translated_json, str) else translated_json
                if isinstance(parsed_translated, dict) and parsed_translated.get("error"):
                    self.log_message(f"Translation error: {parsed_translated.get('error')}")
                    return None
                if not isinstance(parsed_translated, list):
                    self.log_message("Error: Translated result is not a list of segments.")
                    return None
                translated_json = json.dumps(parsed_translated, ensure_ascii=False)
            except Exception as e:
                self.log_message(f"Error: Failed to parse translation result - {str(e)}")
                return None
            srt_tool = SRTFormatterTool()
            srt_content = srt_tool._run(translated_json)
            input_path = Path(json_path)
            srt_filename = input_path.stem + ".srt"
            srt_path = Path(self.output_path_var.get()) / srt_filename
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            self.log_message("Translation/formatting completed")
            try:
                if os.path.exists(json_path):
                    os.remove(json_path)
                    self.log_message("Temporary JSON file deleted")
            except Exception:
                pass
            return str(srt_path)
        except Exception as e:
            self.log_message(f"Translation error: {str(e)}")
            return None

    def run(self):
        self.root.mainloop()


def main():
    app = IntegratedSRTGenerator()
    app.run()
