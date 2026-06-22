Markdown
# 🎧 Audiobook Generator Pro

An open-source, ultra-efficient desktop application built in Python that converts PDF documents and raw text into hyper-realistic, studio-quality MP3 audiobooks. 

Unlike other tools, this application utilizes **Edge-TTS** to leverage premium cloud-based neural voices completely for free, bypassing the need for expensive API keys, subscriptions, or restrictive character limits.

---

## ✨ Features

- **Unlimited Neural Text-to-Speech:** Powered by Microsoft Azure's hidden "Read Aloud" neural engine. Enjoy highly expressive, human-like voices without a single limitation.
- **Multi-Source Input:** Seamlessly switch between processing entire local `.pdf` documents or dropping in raw text via an elegant tabbed interface.
- **Advanced Text Extraction:** Efficiently reads and binds multi-page text blocks while intelligently ignoring corrupt or encrypted data pipelines.
- **Pacing Modulation:** Control the reading speed dynamically from -50% to +50% using a clean GUI slider.
- **Asynchronous Execution:** Thread-safe, non-blocking background architecture means the UI stays responsive and crisp even when generating massive audio files.
- **Modern User Interface:** Styled elegantly using modern Dark/Light/System themes courtesy of `CustomTkinter`.

---

## 🛠️ Built With

* [Python 3.8+](https://www.python.org/)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI Design
* [Edge-TTS](https://github.com/rany2/edge-tts) - Unlimited Neural Voice Engine
* [PyPDF](https://github.com/py-pdf/pypdf) - Clean Document Parsing

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install the necessary package dependencies via your terminal:

```bash
# Navigate into the project directory
cd audiobook-generator-pro

# Install dependencies
pip install -r requirements.txt
2. Run the Application
Start the main application loop by executing:

Bash
python main.py
🗺️ UI Extensions & Roadmap (Contributors Welcome! 👋)
We want to make this app look visually stunning and dynamic. If you want to contribute, here are a few feature sets we are actively looking to implement:

[ ] Dynamic Audio Waveform Animation: Integrating a responsive canvas vector wave that bounces visually while text processing is ongoing.

[ ] Real-Time Word Highlighting: Utilizing .vtt stream metadata from Edge-TTS to highlight the exact word/sentence in the textbox as it's spoken.

[ ] Native File Drag & Drop: Swapping basic file dialogues out for TkinterDnD2 to let users drag PDFs directly into the window.

[ ] In-App Media Player: Adding simple Play, Pause, and Stop actions to sample specific text segments directly in-app before rendering full MP3s.

Feel free to open an Issue or submit a Pull Request to help upgrade the app!

📄 License
Distributed under the MIT License. See LICENSE for more information.