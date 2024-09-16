import sys
import logging
from pathlib import Path
import datetime
import tempfile
import wave
import pyaudio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout, QFileDialog
from PySide6.QtCore import QThread, Signal, QObject, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the output directory
OUTPUT_DIR = Path("mp3files")
OUTPUT_DIR.mkdir(exist_ok=True)

class TTSSignals(QObject):
    finished = Signal(str)

class TTSThread(QThread):
    def __init__(self, client, text, voice):
        super().__init__()
        self.client = client
        self.text = text
        self.voice = voice
        self.signals = TTSSignals()

    def run(self):
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=self.text
            )
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"output_{self.voice}_{timestamp}.mp3"
            with open(output_file, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            self.signals.finished.emit(str(output_file))
        except Exception as e:
            logging.error(f"Error in TTSThread: {str(e)}")
            self.signals.finished.emit(f"Error: {str(e)}")

class TranscribeThread(QThread):
    finished = Signal(str)

    def __init__(self, client, audio_file):
        super().__init__()
        self.client = client
        self.audio_file = audio_file

    def run(self):
        try:
            with open(self.audio_file, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            self.finished.emit(transcript.text)
        except Exception as e:
            logging.error(f"Error in TranscribeThread: {str(e)}")
            self.finished.emit(f"Error: {str(e)}")

class TTSSTTApp(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Initializing TTSSTTApp")
        try:
            self.client = OpenAI()
            self.initUI()
            self.initAudio()
            logging.info("TTSSTTApp initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing TTSSTTApp: {str(e)}")
            raise

    def initUI(self):
        logging.info("Initializing UI")
        layout = QVBoxLayout()

        self.text_input = QTextEdit()
        layout.addWidget(self.text_input)

        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        layout.addWidget(self.voice_combo)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton('Generate and Play Speech')
        self.generate_button.clicked.connect(self.generate_speech)
        button_layout.addWidget(self.generate_button)

        self.load_audio_button = QPushButton('Load Audio File')
        self.load_audio_button.clicked.connect(self.load_audio_file)
        button_layout.addWidget(self.load_audio_button)

        self.transcribe_button = QPushButton('Transcribe')
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        self.transcribe_button.setEnabled(False)
        button_layout.addWidget(self.transcribe_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('Text-to-Speech and Speech-to-Text App')
        self.setGeometry(300, 300, 500, 300)
        logging.info("UI initialized successfully")

    def initAudio(self):
        logging.info("Initializing Audio")
        try:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            logging.info("Audio initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing audio: {str(e)}")
            QMessageBox.warning(self, "Audio Initialization Error", 
                                "Failed to initialize audio. Playback may not work.")

    def generate_speech(self):
        text = self.text_input.toPlainText()
        voice = self.voice_combo.currentText()
        
        self.tts_thread = TTSThread(self.client, text, voice)
        self.tts_thread.signals.finished.connect(self.on_tts_finished)
        self.tts_thread.start()
        self.generate_button.setEnabled(False)

    def on_tts_finished(self, result):
        self.generate_button.setEnabled(True)
        if result.startswith("Error"):
            logging.error(result)
            QMessageBox.critical(self, "Error", result)
        else:
            logging.info(f"Speech generated and saved to {result}")
            self.play_audio(result)

    def play_audio(self, file_path):
        try:
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()
        except Exception as e:
            logging.error(f"Error playing audio: {str(e)}")
            QMessageBox.warning(self, "Playback Error", 
                                f"Failed to play audio: {str(e)}")

    def load_audio_file(self):
        file_dialog = QFileDialog()
        audio_file, _ = file_dialog.getOpenFileName(self, "Load Audio File", "", "Audio Files (*.mp3 *.wav *.m4a)")
        if audio_file:
            self.audio_file = audio_file
            self.transcribe_button.setEnabled(True)
            QMessageBox.information(self, "File Loaded", f"Audio file loaded: {audio_file}")

    def transcribe_audio(self):
        if hasattr(self, 'audio_file'):
            self.transcribe_thread = TranscribeThread(self.client, self.audio_file)
            self.transcribe_thread.finished.connect(self.on_transcribe_finished)
            self.transcribe_button.setEnabled(False)
            self.transcribe_thread.start()
        else:
            QMessageBox.warning(self, "No Audio File", "Please load an audio file first.")

    def on_transcribe_finished(self, result):
        self.transcribe_button.setEnabled(True)
        if result.startswith("Error"):
            logging.error(result)
            QMessageBox.critical(self, "Error", result)
        else:
            self.text_input.setText(result)
            logging.info("Transcription completed")

def check_window_visibility(window):
    if window.isVisible():
        logging.info("Window is visible")
    else:
        logging.warning("Window is not visible")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = TTSSTTApp()
        ex.show()
        
        # Check window visibility after a short delay
        QTimer.singleShot(1000, lambda: check_window_visibility(ex))
        
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"Critical error in main: {str(e)}")
        sys.exit(1)