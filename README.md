# ELIZA Voice Chatbot 🎙️

A modern, voice-enabled implementation of the classic ELIZA psychotherapist chatbot with bilingual support for English and Swedish. This project combines traditional conversational AI with cutting-edge speech recognition and text-to-speech technologies for an immersive therapeutic conversation experience.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Voice Enabled](https://img.shields.io/badge/voice-enabled-orange.svg)
![Bilingual](https://img.shields.io/badge/languages-English%20%7C%20Swedish-red.svg)
![ASR](https://img.shields.io/badge/ASR-Faster%20Whisper-blue.svg)

## ✨ Features

- **🎙️ Push-to-Talk Interface** - Hold SPACE to speak, release to process
- **🌍 Bilingual Support** - Seamlessly switch between English and Swedish
- **🧠 Intelligent Language Detection** - Automatically detects and switches languages
- **🗣️ Natural Voice Synthesis** - High-quality text-to-speech in both languages  
- **⚡ Real-Time Processing** - Powered by Faster Whisper for instant transcription
- **🔄 Smart Context Handling** - Maintains conversation flow across language switches
- **🎯 Advanced Pattern Matching** - Rich response patterns for natural conversations

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** (Python 3.8+ recommended)
- **Microphone and speakers/headphones**
- **CUDA-compatible GPU** (optional, for enhanced performance)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KalleEhrsson/ELIZA.git
   cd ELIZA
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv eliza-env
   source eliza-env/bin/activate  # On Windows: eliza-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the chatbot**
   ```bash
   python eliza_voice.py
   ```

### Dependencies

Create a `requirements.txt` file with:
```txt
numpy>=1.21.0
sounddevice>=0.4.0
faster-whisper>=0.9.0
pynput>=1.7.0
pyttsx3>=2.90
torch>=1.9.0  # Optional: for GPU acceleration detection
```

## 🎮 Usage Guide

### Basic Operation
1. **Start the program** - Run `python eliza_voice.py`
2. **Interact with ELIZA** - Hold down SPACE and speak, or type your message and press Enter
3. **Release or press Enter** - Let go of SPACE or hit Enter when you're done
4. **Listen to response** - ELIZA will reply with synthesized speech

### Language Switching

The system supports seamless language switching during conversations:

**English Commands:**
- Voice: "Switch to English" 
- Text commands: `/lang en`, `/language en`
- Exit phrases: "quit", "bye", "goodbye"

**Swedish Commands:**
- Voice: "Byta till svenska" or "switch to Swedish"
- Text commands: `/lang sv`, `/language sv`, `/lang svenska`
- Exit phrases: "slut", "hejdå", "adjö"

### Session Management
- Each conversation is numbered as a session
- Exiting starts a new session automatically
- Terminal clears between sessions for fresh starts
- Maintains conversation context within each session

### Automatic Language Detection
The system intelligently detects language using multiple strategies:
- **Character markers** - Swedish: åäö characters, English: standard patterns
- **Start word recognition** - Language-specific conversation starters
- **Contextual analysis** - Phrase structures and linguistic patterns
- **Explicit commands** - Direct language switch requests
- **Sticky language switching** - Only switches on strong linguistic cues to prevent accidental changes

## ⚙️ Configuration

### Voice Settings
Customize TTS voices in the `main()` function:
```python
# Set preferred voices by name substring (Windows SAPI example)
tts_prepare(en_voice="Zira", sv_voice="Bengt")

# Other common voice names:
# Windows: "Zira", "David", "Mark", "Hazel"  
# macOS: "Alex", "Samantha", "Daniel"
# Linux: Usually uses espeak or festival
```

### Speech Recognition Model
Adjust Whisper model based on your hardware capabilities:
```python
# Available models: tiny, base, small, medium, large
# GPU detection is automatic via torch.cuda.is_available()
asr_init(model_size="medium", use_gpu=True)  # Set to False to force CPU
```

### Recording Parameters
Fine-tune audio capture in `record_while_holding_space()`:
```python
record_while_holding_space(
    wait_timeout=10,      # Seconds to wait for first SPACE press
    max_seconds=12,       # Maximum recording duration while holding SPACE
    samplerate=16000,     # Audio sample rate (16kHz recommended)
    blocksize=1024        # Audio processing block size
)
```

### ELIZA Response Patterns
The bot includes extensive pattern matching for both languages with reflection capabilities:
- **English**: 30+ conversation patterns covering personal statements, questions, emotions
- **Swedish**: 30+ culturally adapted patterns with proper Swedish grammar
- **Word reflection**: Automatically converts "I" ↔ "you", "my" ↔ "your", "jag" ↔ "du", etc.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Speech-to-Text  │───▶│Language Detection│
│ (Push-to-Talk)  │    │ (Faster Whisper) │    │   & Switching   │
│   SPACE key     │    │  CPU/GPU Support │    │ Sticky Algorithm│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Voice Output   │◀───│  Text-to-Speech  │◀───│ ELIZA Response  │
│   (pyttsx3)     │    │Cross-platform TTS│    │   Generation    │
│ Per-call Engine │    │ Voice Selection  │    │Pattern Matching │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

**Audio Processing Pipeline**:
- `record_while_holding_space()` - Real-time audio capture with push-to-talk
- `transcribe_audio_whisper()` - Speech recognition with VAD filtering
- `speak()` - Text-to-speech with per-call engine initialization

**Language Intelligence**:
- `detect_language_strong()` - Multi-strategy language detection
- `has_swedish_markers()` / `has_english_markers()` - Pattern-based detection
- `parse_lang_command()` - Explicit command parsing

**Conversation Engine**:
- `Eliza` class with bilingual response patterns
- `reflect_text()` - Grammatical reflection (I ↔ you transformations)
- Session-based conversation management

## 💬 Conversation Examples

### English Conversation
```
Session 1
Hello / Hej! Hold SPACE to talk. Say 'quit' or 'slut' to exit.

[User holds SPACE and speaks: "I feel anxious about my job"]
I feel anxious about my job.
ELIZA: When do you usually feel anxious about your job?

[User: "My boss is very demanding"]  
My boss is very demanding.
ELIZA: Tell me more about your boss.

[User: "Switch to Swedish"]
Switch to Swedish.
ELIZA: [Language switched to Swedish]
```

### Swedish Conversation  
```
[User: "Jag känner mig trött"]
Jag känner mig trött.
ELIZA: Känner du dig ofta trött?

[User: "Min mamma ringer hela tiden"]
Min mamma ringer hela tiden.  
ELIZA: Berätta mer om din mamma.

[User: "quit"]
Quit.
ELIZA: Loggar ut som ett gammalt ICQ-konto… hej då!
```

## 🔧 Troubleshooting

### Audio Issues

**No audio input detected:**
- Verify microphone permissions in system settings
- Test microphone access: `python -c "import sounddevice as sd; print(sd.query_devices())"`
- Check default audio device configuration

**Text-to-speech not working:**
- **Windows**: Ensure SAPI voices are installed in system settings
- **macOS**: Verify system voice settings in Accessibility
- **Linux**: Install speech synthesis engines: `sudo apt-get install espeak festival`

### Performance Issues

**GPU/CUDA errors:**
- Set `use_gpu=False` in `asr_init()` for CPU-only processing
- Verify CUDA toolkit installation for GPU acceleration
- Check GPU memory availability (4GB+ VRAM recommended)

**Language detection problems:**
- Speak clearly and use language-specific vocabulary
- Try explicit language commands: "/lang en" or "/lang sv"
- Ensure proper microphone distance and audio quality

### Performance Optimization

**Memory & CPU:**
- Per-call TTS engine initialization prevents memory leaks
- Audio processing uses efficient numpy arrays
- Whisper model caching for faster subsequent transcriptions

**Hardware Recommendations:**
- **Minimum**: 4GB RAM, dual-core CPU, integrated audio
- **Recommended**: 8GB+ RAM, quad-core CPU, dedicated GPU with 4GB+ VRAM
- **Storage**: 2GB free space for Whisper models

**Model Size Selection:**
| Model | Size | VRAM | Speed | Accuracy |
|-------|------|------|-------|----------|
| tiny | 39 MB | 1 GB | Fastest | Basic |
| base | 74 MB | 1 GB | Fast | Good |  
| small | 244 MB | 2 GB | Medium | Better |
| medium | 769 MB | 5 GB | Slow | Excellent |
| large | 1550 MB | 10 GB | Slowest | Best |

## 🤝 Contributing

We welcome contributions! Here are ways to help:

- 🌐 **Add language support** - Implement new language patterns
- 🎨 **Improve UI/UX** - Enhanced user interface design
- ⚡ **Performance optimization** - Speed and memory improvements  
- 📝 **Expand conversation patterns** - More sophisticated responses
- 🐛 **Bug fixes** - Error handling and stability improvements
- 📚 **Documentation** - Better guides and examples

### Development Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-awesome-addition`
3. **Make changes and test thoroughly**
4. **Submit a pull request** with clear description and test results

### Code Style & Guidelines
- Follow PEP 8 Python style guidelines
- Use descriptive variable names and clear function documentation
- Maintain bilingual support in all new features
- Test on multiple platforms (Windows, macOS, Linux)
- Include both voice and text examples in documentation

## 🔬 Technical Implementation Details

### Audio Pipeline
```python
# Real-time audio capture with threading
def record_while_holding_space():
    # Uses sounddevice for cross-platform audio
    # Implements push-to-talk with keyboard listener
    # Thread-safe queue for audio chunks
```

### Language Detection Algorithm  
```python
def detect_language_strong(text_lower):
    # 1. Check explicit commands (/lang en, byta till svenska)
    # 2. Analyze character patterns (åäö for Swedish)
    # 3. Match language-specific starter words
    # 4. Return None for ambiguous input (sticky behavior)
```

### TTS Engine Management
```python  
def speak(text, lang="en", rate=175, volume=1.0):
    # Creates fresh engine per call to prevent crashes
    # Platform-specific driver selection (SAPI5, nsss, espeak)
    # Voice caching for performance
    # Automatic cleanup to prevent memory leaks
```

### ELIZA Response Generation
```python
class Eliza:
    # Regex-based pattern matching
    # Word reflection transformations  
    # Bilingual response templates
    # Contextual response selection
```

## 📊 Project Statistics

- **~500 lines of Python code**
- **60+ therapeutic response patterns**
- **13 English farewell messages**  
- **13 Swedish farewell messages**
- **Cross-platform compatibility**
- **Real-time audio processing**
- **GPU acceleration support**

## 🎓 Educational Value

This project demonstrates several advanced programming concepts:

- **Natural Language Processing**: Pattern matching, text reflection, language detection
- **Audio Processing**: Real-time capture, speech recognition, synthesis  
- **Multilingual Systems**: Dynamic language switching, cultural adaptation
- **Threading**: Concurrent audio processing and user input handling
- **Hardware Integration**: GPU detection, platform-specific optimizations
- **User Interface Design**: Push-to-talk interaction, session management

## 🌟 Inspiration & References

This implementation pays homage to Joseph Weizenbaum's original ELIZA (1966) while incorporating modern technologies:

- **Historical Context**: One of the first chatbots to demonstrate natural language conversation
- **Therapeutic Approach**: Non-directive conversation techniques from person-centered therapy  
- **Modern Enhancements**: Voice interaction, multilingual support, advanced speech recognition
- **Cultural Adaptation**: Swedish language patterns and cultural references

---

**School Project** - Created with ❤️ for learning multilingual conversational AI, speech processing, and human-computer interaction.

*This project explores the intersection of classic AI concepts with modern speech technology, demonstrating how traditional algorithms can be enhanced with contemporary tools to create engaging, accessible applications.*

## 📞 Support & Contact

For questions, issues, or feature requests:
- 🐛 **Bug Reports**: Open a [GitHub Issue](https://github.com/KalleEhrsson/ELIZA/issues)  
- 💡 **Feature Requests**: Submit a [GitHub Issue](https://github.com/KalleEhrsson/ELIZA/issues) with the "enhancement" label
- 📖 **Documentation**: Check this README and inline code comments
- 🔧 **Development**: See the Contributing section above

---
*"The computer programmer is a creator of universes for which he alone is responsible."* - Joseph Weizenbaum
