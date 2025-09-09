# ELIZA - Advanced Voice-Enabled Chatbot

A sophisticated, multilingual implementation of the classic ELIZA psychotherapist chatbot with modern AI features including voice recognition, text-to-speech synthesis, intelligent language detection, and advanced text processing capabilities.

## ✨ Key Features

### 🎙️ **Voice Interaction**
- **Push-to-talk interface** - Hold SPACE to speak, release to process
- **Real-time speech recognition** - Powered by Faster Whisper for accurate transcription
- **Natural voice synthesis** - High-quality text-to-speech in both languages
- **Cross-platform audio support** - Works on Windows, macOS, and Linux

### 🌍 **Intelligent Language Support**
- **Bilingual operation** - Seamless English and Swedish conversation
- **Automatic language detection** - Smart switching based on speech patterns and keywords
- **Sticky language mode** - Maintains language preference until strong cues suggest otherwise
- **Manual language switching** - Support for explicit commands (`/lang en`, `/lang sv`)

### 🧠 **Advanced Text Processing**
- **Smart spell correction** - English (pyspellchecker) and Swedish (fuzzy matching)
- **Text humanization** - Adds realistic typos, fillers, and casual speech patterns
- **Slang normalization** - Handles contractions and informal language
- **Live colored terminal input** - Real-time character echo with backspace support

### 🎯 **Enhanced ELIZA Engine**
- **Pattern-based responses** - Comprehensive rule sets for both languages
- **Contextual reflection** - Intelligent pronoun and perspective switching
- **Emotional intelligence** - Recognizes and responds to feelings and family topics
- **Cultural adaptation** - Language-specific conversation patterns and expressions

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Microphone and audio output
- Optional: CUDA-compatible GPU for faster speech recognition

### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/KalleEhrsson/ELIZA.git
cd ELIZA
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python Eliza_Complicated.py
```

### Dependencies
Create a `requirements.txt` file with:
```
numpy>=1.21.0
sounddevice>=0.4.0
faster-whisper>=0.9.0
pynput>=1.7.0
pyttsx3>=2.90
spellchecker>=0.4
rapidfuzz>=2.0.0
colorama>=0.4.4
```

Optional for GPU acceleration:
```
torch>=1.10.0
```

## 🚀 Usage Guide

### Basic Operation
1. **Start the program** - Run `python Eliza_Complicated.py`
2. **Choose input method:**
   - **Voice**: Hold SPACE key and speak, release when done
   - **Text**: Type directly and press Enter
3. **Listen and respond** - ELIZA responds with both text and synthesized speech
4. **Exit gracefully** - Say or type goodbye in either language

### Language Switching
The chatbot automatically detects and switches languages based on:
- **Swedish indicators**: Characters (åäö), words (jag, är, inte), commands
- **English indicators**: Common words (the, and, you), patterns, commands
- **Explicit commands**:
  - English: `"switch to english"`, `"/lang en"`
  - Swedish: `"byta till svenska"`, `"/lang sv"`

### Exit Commands
**English**: quit, bye, goodbye, exit, see you, farewell
**Swedish**: slut, hejdå, adjö, vi ses, ha det, farväl

## ⚙️ Configuration

### Voice Preferences
Modify voice settings in the `main()` function:
```python
# Set preferred TTS voices (Windows SAPI example)
tts_prepare(en_voice="Zira", sv_voice="Bengt")
```

### Speech Recognition Model
Adjust Whisper model size for your hardware:
```python
# Options: tiny, base, small, medium, large-v2
# Smaller = faster but less accurate
# Larger = slower but more accurate
asr_init(model_size="medium", use_gpu=True)
```

### Text Humanization
Customize the realistic text modifications:
```python
humanize_text(
    text, lang="en",
    typo_prob=0.22,    # Probability of adding typos
    max_typos=2,       # Maximum typos per response
    filler_prob=0.18,  # Probability of adding fillers ("um", "eh")
    style_prob=0.25    # Probability of casual style tweaks
)
```

### Audio Settings
Configure recording parameters:
```python
record_while_holding_space(
    wait_timeout=10,    # Seconds to wait for SPACE press
    max_seconds=12,     # Maximum recording duration
    samplerate=16000,   # Audio sample rate
    blocksize=1024      # Audio processing block size
)
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Voice Input     │───▶│ Speech-to-Text   │───▶│ Language        │
│ (Push-to-Talk)  │    │ (Faster Whisper) │    │ Detection       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Text Input      │───▶│ Spell Correction │───▶│ Text Processing │
│ (Live Typing)   │    │ & Normalization  │    │ & Humanization  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Voice Output    │◀───│ Text-to-Speech   │◀───│ ELIZA Response  │
│ (pyttsx3)       │    │ Synthesis        │    │ Generation      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🧩 Core Components

### Language Detection System
- **Word-based recognition** - Maintains vocabularies of common words in each language
- **Character-based hints** - Detects Swedish-specific characters (åäö)
- **Command parsing** - Recognizes explicit language switch requests
- **Sticky mode** - Preserves language choice until strong contrary evidence

### ELIZA Response Engine
The bot includes sophisticated pattern matching for:

**English Patterns:**
- Personal statements: "I need...", "I am...", "I feel..."
- Questions: "What...", "Why...", "How..."
- Family topics: "mother", "father", "child"
- Emotional expressions and psychological themes

**Swedish Patterns:**
- Personal statements: "Jag behöver...", "Jag är...", "Jag känner..."
- Questions: "Vad...", "Varför...", "Hur..."
- Family topics: "mamma", "pappa", "barn"
- Swedish-specific grammar and cultural expressions

### Text Processing Pipeline
1. **Input normalization** - Handle slang and contractions
2. **Language detection** - Determine active language
3. **Spell correction** - Fix common typing errors
4. **ELIZA processing** - Generate therapeutic responses
5. **Humanization** - Add realistic speech patterns
6. **Output formatting** - Proper capitalization and punctuation

## 🔧 Troubleshooting

### Audio Issues
**No microphone input detected:**
- Check microphone permissions
- Verify device access: `python -c "import sounddevice as sd; print(sd.query_devices())"`
- Ensure microphone is not muted or used by other applications

**Text-to-speech not working:**
- **Windows**: Ensure SAPI voices are installed
- **macOS**: Check System Preferences → Accessibility → Speech
- **Linux**: Install espeak or festival: `sudo apt install espeak espeak-data`

### Performance Issues
**Slow speech recognition:**
- Reduce Whisper model size: `asr_init(model_size="small")`
- Use CPU mode: `asr_init(use_gpu=False)`
- Check GPU memory availability

**CUDA/GPU errors:**
- Install CUDA toolkit matching your PyTorch version
- Set CPU-only mode: `use_gpu=False` in `asr_init()`
- Verify GPU compatibility: `python -c "import torch; print(torch.cuda.is_available())"`

### Language Detection Issues
- Speak clearly using language-specific words
- Use explicit commands: `/lang en` or `/lang sv`
- Check if Swedish characters (åäö) are being input correctly

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **Language expansion** - Add support for more languages
- **UI enhancement** - Develop graphical interface
- **Performance optimization** - Improve real-time processing
- **Response patterns** - Add more sophisticated ELIZA rules
- **Voice quality** - Integration with neural TTS systems

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request with clear description

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **RAM**: 4GB
- **Storage**: 2GB free space (for Whisper models)
- **Audio**: Microphone and speakers/headphones

### Recommended Setup
- **RAM**: 8GB+ (for smooth real-time processing)
- **GPU**: CUDA-compatible with 4GB+ VRAM
- **CPU**: Multi-core processor
- **Storage**: SSD for faster model loading

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ELIZA** - Original concept by Joseph Weizenbaum (1966)
- **Faster Whisper** - Efficient speech recognition implementation
- **OpenAI Whisper** - Foundation speech recognition model
- **pyttsx3** - Cross-platform text-to-speech library

**School Project** - Made with dedication for exploring multilingual conversational AI, speech processing, and human-computer interaction.

This project demonstrates advanced integration of speech recognition, natural language processing, and text-to-speech synthesis in a multilingual context, showcasing modern approaches to conversational AI development.
