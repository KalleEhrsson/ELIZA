# 🎤 Multilingual Voice ELIZA Chatbot

> **School Project** - A modern, voice-enabled implementation of the classic ELIZA psychotherapist chatbot with support for **English** and **Swedish**. Features real-time speech recognition, text-to-speech synthesis, and intelligent language switching.

## ✨ Features

- 🎙️ **Push-to-talk voice interaction** - Hold SPACE to speak
- 🌍 **Bilingual support** - English and Swedish with automatic language detection
- 🧠 **Smart language switching** - Detects language from speech patterns and explicit commands
- 🗣️ **Text-to-speech synthesis** - Natural voice responses in both languages
- 🎯 **Advanced speech recognition** - Powered by Faster Whisper for accurate transcription
- 🔄 **Real-time processing** - Instant response generation and voice synthesis

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- CUDA-compatible GPU (optional, for faster speech recognition)
- Microphone and speakers/headphones

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/eliza-voice-chatbot.git
   cd eliza-voice-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the chatbot**
   ```bash
   python eliza_voice.py
   ```

## 📦 Dependencies

```
numpy
sounddevice
faster-whisper
pynput
pyttsx3
```

Create a `requirements.txt` file:
```txt
numpy>=1.21.0
sounddevice>=0.4.0
faster-whisper>=0.9.0
pynput>=1.7.0
pyttsx3>=2.90
```

## 🎯 How to Use

1. **Start the program** - Run `python eliza_voice.py`
2. **Talk to ELIZA** - Hold down the SPACE key and speak
3. **Release to process** - Let go of SPACE when you're done speaking
4. **Listen to response** - ELIZA will respond with synthesized speech

### Voice Commands

#### Language Switching
- **English**: Say "switch to english" or "/lang en"
- **Swedish**: Say "byta till svenska" or "/lang sv"

#### Exit Commands
- **English**: "quit", "bye", "goodbye"
- **Swedish**: "slut", "hejdå", "adjö"

## 🧠 Language Detection

The chatbot automatically detects language using:

- **Swedish markers**: åäö characters, common Swedish words
- **English markers**: Common English starter words and patterns  
- **Explicit commands**: Direct language switch requests
- **Context clues**: Language-specific phrases and expressions

## 🔧 Configuration

### Voice Selection

Modify the voice preferences in the `main()` function:

```python
# Set preferred voices by name substring
tts_prepare(en_voice="Zira", sv_voice="Bengt")  # Windows SAPI voices
```

### Speech Recognition Model

Adjust the Whisper model size for your needs:

```python
# Options: tiny, base, small, medium, large
asr_init(model_size="small", use_gpu=True)
```

### Recording Settings

Customize recording parameters in `record_while_holding_space()`:

```python
record_while_holding_space(
    wait_timeout=10,    # Seconds to wait for first SPACE press
    max_seconds=12,     # Maximum recording duration
    samplerate=16000,   # Audio sample rate
    blocksize=1024      # Audio processing block size
)
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Speech-to-Text  │───▶│ Language Detect│
│  (Push-to-Talk) │    │ (Faster Whisper) │    │   & Switching   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Voice Output   │◀───│  Text-to-Speech  │◀───│ ELIZA Response │
│   (pyttsx3)     │    │    (pyttsx3)     │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 ELIZA Response Patterns

The chatbot includes comprehensive response patterns for both languages:

### English Patterns
- Personal statements ("I am...", "I feel...")
- Questions ("What...", "Why...", "How...")
- Family relationships ("mother", "father", "child")
- Emotional expressions and reflections

### Swedish Patterns  
- Personal statements ("Jag är...", "Jag känner...")
- Questions ("Vad...", "Varför...", "Hur...")
- Family relationships ("mamma", "pappa", "barn")
- Swedish-specific grammar and expressions

## 🛠️ Troubleshooting

### Common Issues

**No audio input detected:**
- Check microphone permissions
- Verify `sounddevice` can access your microphone
- Try: `python -c "import sounddevice as sd; print(sd.query_devices())"`

**TTS not working:**
- Windows: Ensure SAPI voices are installed
- macOS: Check system voice settings  
- Linux: Install `espeak` or `festival`

**GPU/CUDA errors:**
- Set `use_gpu=False` in `asr_init()` for CPU-only mode
- Ensure CUDA toolkit is properly installed for GPU acceleration

**Language detection issues:**
- Speak clearly and use language-specific words
- Try explicit commands: "/lang en" or "/lang sv"

## 🤝 Contributing

Contributions are welcome! Here are some ways to help:

- 🌐 Add support for more languages
- 🎨 Improve the user interface
- 🔧 Optimize performance
- 📝 Add more ELIZA response patterns
- 🐛 Fix bugs and improve error handling

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ELIZA** - Original concept by Joseph Weizenbaum (1966)
- **Faster Whisper** - High-performance speech recognition
- **pyttsx3** - Cross-platform text-to-speech synthesis
- **OpenAI Whisper** - Foundation for the speech recognition model

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **RAM**: 4GB (8GB recommended for GPU usage)
- **Storage**: 2GB free space for models
- **Audio**: Microphone and audio output device

### Recommended Requirements
- **GPU**: CUDA-compatible GPU with 4GB+ VRAM
- **RAM**: 8GB+
- **CPU**: Multi-core processor for real-time processing

---

**School Project - Made with ❤️ for learning multilingual conversational AI**

*This project was created as part of a computer science coursework exploring natural language processing, speech recognition, and multilingual AI systems.*

*For questions, issues, or feature requests, please open a GitHub issue.*
