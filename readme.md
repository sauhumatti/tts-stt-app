# Text-to-Speech and Speech-to-Text Application

This application provides a graphical user interface for converting text to speech and transcribing audio files to text using OpenAI's API. It's built with Python and PySide6, making it compatible with Windows Subsystem for Linux (WSL2) environments.

## Features

- Text-to-Speech: Convert typed text to speech using various voice options.
- Speech-to-Text: Transcribe uploaded audio files to text.
- Simple and intuitive graphical user interface.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/sauhumatti/tts-stt-app.git
   cd tts-stt-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Use the interface to:
   - Type text and select a voice to generate speech.
   - Load an audio file and transcribe it to text.

## Note for WSL2 Users

This application is designed to work in a WSL2 environment. Audio recording directly within WSL2 is not supported, but you can use Windows tools to record audio and then use this application to transcribe the files.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.