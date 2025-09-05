"""
Eliza_Complicated.py
Voice-enabled ELIZA chatbot with:
- Speech input (push-to-talk using SPACE + faster-whisper for speech-to-text)
- Text input (typed directly into terminal)
- Language detection (Swedish or English, with automatic switching)
- Voice output (pyttsx3 text-to-speech with preferred voices)

Main flow:
1. Wait for user input (speech or text).
2. Detect language (sticky unless strong cues appear).
3. Pass input through ELIZA pattern-matching rules.
4. Respond with text + synthesized speech.
5. Exit gracefully when quit words are spoken or typed.
"""

import re
import random
import os, time

import numpy as np
import sounddevice as sd
import queue, threading, time
from faster_whisper import WhisperModel
from pynput import keyboard

# ---------------------------------------------------------
# Single-key input helper (for detecting SPACE quickly)
# ---------------------------------------------------------
def get_single_key():
    """Read a single keypress without waiting for Enter (cross-platform)."""
    try:
        import msvcrt  # Windows
        return msvcrt.getwch()
    except Exception:  # Unix-like
        import sys
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def flush_input_buffer():
    """Clear any pending keyboard input to avoid unintended repeats."""
    try:
        import msvcrt  # Windows
        while msvcrt.kbhit():
            msvcrt.getwch()
    except Exception:  # Unix-like
        import sys
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

# ---------------------------------------------------------
# Language detection helpers and keyword sets
# ---------------------------------------------------------
SWEDISH_START_WORDS = ("hej", "jag", "varför", "slut", "hejdå", "adjö", "svenska")
ENGLISH_START_WORDS = ("hello", "hi", "hey", "why", "because", "i", "can", "are", "what", "how", "english")

GOODBYES_EN = {"quit", "bye", "goodbye"}
GOODBYES_SV = {"slut", "hejdå", "adjö"}
QUIT_WORDS = GOODBYES_EN | GOODBYES_SV  # either triggers exit

# Fun exit phrases
FAREWELLS_EN = [
    "Goodbye!",
    "Bye!",
    "See you!",
    "Take care of yourself!",
    "See you later, have a great day!",
    "Catch you soon, don’t be a stranger!",
    "Farewell, until we meet again!",
    "Later, hope everything goes well for you!",
    "Don’t do anything I wouldn’t do!",
    "Logging off like a true 90s modem… goodbye!",
    "May the Wi-Fi be with you!",
    "See you in another timeline!",
    "Vanishing dramatically… poof!"
]

FAREWELLS_SV = [
    "Hejdå!",
    "Adjö!",
    "Vi ses!",
    "Ha det bra och ta hand om dig!",
    "Vi hörs senare, ha en fin dag!",
    "På återseende, hoppas allt går bra för dig!",
    "Ses snart, glöm inte att höra av dig!",
    "Ha det gott tills vi ses igen!",
    "Gör inget jag inte skulle göra!",
    "Loggar ut som ett gammalt ICQ-konto… hej då!",
    "Må Wi-fi:et vara med dig!",
    "Vi ses i nästa liv!",
    "Försvinner mystiskt i dimman… poff!"
]

def has_swedish_markers(text_lower):
    """Check if text has strong Swedish hints (letters, words, commands)."""
    if any(ch in text_lower for ch in "åäö"):
        return True
    if text_lower.startswith(SWEDISH_START_WORDS):
        return True
    if re.search(r"\b(svenska|byta till svenska|switch to swedish)\b", text_lower):
        return True
    return False

def has_english_markers(text_lower):
    """Check if text has strong English hints."""
    if text_lower.startswith(ENGLISH_START_WORDS):
        return True
    if re.search(r"\b(english|switch to english|/lang en)\b", text_lower):
        return True
    return False

def parse_lang_command(text_lower):
    """Parse explicit /lang commands if present."""
    if text_lower.startswith(("/lang sv", "/language sv", "/lang svenska")) or "switch to swedish" in text_lower:
        return "sv"
    if text_lower.startswith(("/lang en", "/language en")) or "switch to english" in text_lower:
        return "en"
    return None

def detect_language_strong(text_lower):
    """Return 'sv' or 'en' if strong cues detected, else None."""
    cmd = parse_lang_command(text_lower)
    if cmd:
        return cmd
    if has_swedish_markers(text_lower):
        return "sv"
    if has_english_markers(text_lower):
        return "en"
    return None

def format_sentence(text):
    """Capitalize first letter, ensure ending punctuation."""
    text = text.strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


# ---------------------------------------------------------
# Text-to-Speech helpers (pyttsx3, per-call engine)
# ---------------------------------------------------------
import sys
import pyttsx3

_voice_names = {"en": None, "sv": None}   # preferred substrings ("Zira", "Bengt")
_voice_cache = {"en": None, "sv": None}   # resolved IDs

def _default_driver():
    """Pick driver backend depending on OS."""
    if sys.platform.startswith("win"):
        return "sapi5"
    if sys.platform == "darwin":
        return "nsss"
    return None  # Linux defaults to espeak

def tts_prepare(en_voice=None, sv_voice=None):
    """Set preferred voices by name substring (called once at startup)."""
    _voice_names["en"] = en_voice
    _voice_names["sv"] = sv_voice

def _resolve_voice_id(lang):
    """Find and cache a voice ID for the given language."""
    if _voice_cache.get(lang):
        return _voice_cache[lang]
    engine = pyttsx3.init(driverName=_default_driver())
    voices = engine.getProperty("voices")

    # Try explicit preferred name
    name_sub = _voice_names.get(lang)
    if name_sub:
        for v in voices:
            if name_sub.lower() in v.name.lower():
                _voice_cache[lang] = v.id
                return v.id

    # Fallback: match language code hints
    hints = ("en", "eng", "english", "us", "gb") if lang == "en" else ("sv", "swe", "svenska", "swedish", "se")
    for v in voices:
        meta = (v.name + " " + v.id).lower()
        if any(h in meta for h in hints):
            _voice_cache[lang] = v.id
            return v.id
    return None

def speak(text, lang="en", rate=175, volume=1.0):
    """Speak text by creating a fresh engine each call."""
    engine = pyttsx3.init(driverName=_default_driver())
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    vid = _resolve_voice_id(lang)
    if vid:
        engine.setProperty("voice", vid)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    del engine


# ---------------------------------------------------------
# Automatic Speech Recognition (ASR) using faster-whisper
# ---------------------------------------------------------
_ASR_MODEL = None

def asr_init(model_size="mediam", use_gpu=True):
    """Load Whisper model into memory (choose GPU or CPU)."""
    device = "cuda" if use_gpu else "cpu"
    compute_type = "float16" if use_gpu else "int8"
    global _ASR_MODEL
    _ASR_MODEL = WhisperModel(model_size, device=device, compute_type=compute_type)

def transcribe_audio_whisper(audio_mono_float32, lang_code):
    """Transcribe mono float32 audio array into text."""
    if _ASR_MODEL is None:
        asr_init()
    segments, _info = _ASR_MODEL.transcribe(
        audio_mono_float32,
        language=lang_code,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )
    return "".join(seg.text for seg in segments).strip()


# ---------------------------------------------------------
# Push-to-talk audio capture (hold SPACE to record)
# ---------------------------------------------------------
def record_while_holding_space(
    wait_timeout=10, max_seconds=12,
    samplerate=16000, blocksize=1024,
    already_pressed=False,
):
    """
    Record microphone input while SPACE is held down.
    Returns: float32 numpy array with recorded samples.
    """
    q = queue.Queue()
    listening = threading.Event()
    started = threading.Event()
    done = threading.Event()

    def on_press(key):
        if key == keyboard.Key.space and not listening.is_set():
            listening.set()
            started.set()
            print("Listening... (release SPACE to stop)")

    def on_release(key):
        if key == keyboard.Key.space and listening.is_set():
            listening.clear()
            done.set()
            return False  # stop listener

    def callback(indata, frames, time_info, status):
        if listening.is_set():
            q.put(indata.copy())

    with sd.InputStream(samplerate=samplerate, channels=1, dtype="float32",
                        blocksize=blocksize, callback=callback):
        with keyboard.Listener(on_press=None if already_pressed else on_press,
                               on_release=on_release) as listener:
            if already_pressed:
                listening.set()
                started.set()
                print("Listening... (release SPACE to stop)")
            if not started.wait(wait_timeout):
                listener.stop()
                return np.array([], dtype="float32")
            done.wait(max_seconds)
            listener.stop()

    # Collect audio frames into one array
    frames = []
    while not q.empty():
        frames.append(q.get())
        flush_input_buffer()
    return np.concatenate(frames).flatten() if frames else np.array([], dtype="float32")


# --- ELIZA bot ---

class Eliza:
    def __init__(self, language="en"):
        self.language = language

        self.responses_english = [
            (r'I need (.*)',
             ["Why do you need {0}?",
              "Would it really help you to get {0}?",
              "Are you sure you need {0}?"]),

            (r'Why don\'?t you ([^\?]*)\??',
             ["Do you really think I don't {0}?",
              "Perhaps I will {0} in the future.",
              "Do you want me to {0}?"]),

            (r'Why can\'?t I ([^\?]*)\??',
             ["Do you think you should be able to {0}?",
              "If you could {0}, what would you do?",
              "I don't know, why can't you {0}?",
              "Have you really tried?"]),

            (r'I can\'?t (.*)',
             ["How do you know you can't {0}?",
              "Perhaps you could {0} if you tried.",
              "What would it take for you to {0}?"]),

            (r'I am (.*)',
             ["Did you come to me because you are {0}?",
              "How long have you been {0}?",
              "How do you feel about being {0}?"]),

            (r'I\'?m (.*)',
             ["How does being {0} make you feel?",
              "Do you enjoy being {0}?",
              "Why do you tell me you're {0}?"]),

            (r'Are you ([^\?]*)\??',
             ["Why does it matter whether I am {0}?",
              "Would you prefer if I were not {0}?",
              "Perhaps you believe I am {0}.",
              "I may be {0}, what do you think?"]),

            (r'What (.*)',
             ["Why do you ask?",
              "How would an answer to that help you?",
              "What do you think?"]),

            (r'How (.*)',
             ["How do you suppose?",
              "Perhaps you can answer your own question.",
              "What is it you're really asking?"]),

            (r'Because (.*)',
             ["Is that the real reason?",
              "What other reasons come to mind?",
              "Does that reason apply to anything else?",
              "If {0}, what else must be true?"]),

            (r'(.*) sorry (.*)',
             ["There are many times when no apology is needed.",
              "What feelings do you have when you apologize?"]),

            (r'Hello(.*)',
             ["Hello... I'm listening.",
              "Hi there... how can I help you?",
              "Hello, how are you feeling today?"]),

            (r'I think (.*)',
             ["Do you doubt {0}?",
              "Do you really think so?",
              "But you're not sure {0}?"]),

            (r'(.*) friend (.*)',
             ["Tell me more about your friends.",
              "When you think of a friend, what comes to mind?",
              "Why don't you tell me about a childhood friend?"]),

            (r'Yes',
             ["You seem quite sure.",
              "OK, but can you elaborate a bit?"]),

            (r'(.*) computer(.*)',
             ["Are you really talking about me?",
              "Does it seem strange to talk to a computer?",
              "How do computers make you feel?",
              "Do you feel threatened by computers?"]),

            (r'Is it (.*)',
             ["Do you think it is {0}?",
              "Perhaps it's {0}, what do you think?",
              "If it were {0}, what would you do?",
              "It could well be that {0}."]),

            (r'It is (.*)',
             ["You seem very certain.",
              "If I told you that it probably isn't {0}, what would you feel?"]),

            (r'Can you ([^\?]*)\??',
             ["What makes you think I can't {0}?",
              "If I could {0}, then what?",
              "Why do you ask if I can {0}?"]),

            (r'Can I ([^\?]*)\??',
             ["Perhaps you don't want to {0}.",
              "Do you want to be able to {0}?",
              "If you could {0}, would you?"]),

            (r'You are (.*)',
             ["Why do you think I am {0}?",
              "Does it please you to think that I'm {0}?",
              "Perhaps you would like me to be {0}.",
              "Perhaps you're really talking about yourself?"]),

            (r'You\'?re (.*)',
             ["Why do you say I am {0}?",
              "Why do you think I am {0}?",
              "Are we talking about you, or me?"]),

            (r'I don\'?t (.*)',
             ["Don't you really {0}?",
              "Why don't you {0}?",
              "Do you want to {0}?"]),

            (r'I feel (.*)',
             ["Good, tell me more about these feelings.",
              "Do you often feel {0}?",
              "When do you usually feel {0}?",
              "When you feel {0}, what do you do?"]),

            (r'I have (.*)',
             ["Why do you tell me that you've {0}?",
              "Have you really {0}?",
              "Now that you have {0}, what will you do next?"]),

            (r'I would (.*)',
             ["Could you explain why you would {0}?",
              "Why would you {0}?",
              "Who else knows that you would {0}?"]),

            (r'Is there (.*)',
             ["Do you think there is {0}?",
              "It's likely that there is {0}.",
              "Would you like there to be {0}?"]),

            (r'My (.*)',
             ["I see, your {0}.",
              "Why do you say that your {0}?",
              "When your {0}, how do you feel?"]),

            (r'You (.*)',
             ["We should be discussing you, not me.",
              "Why do you say that about me?",
              "Why do you care whether I {0}?"]),

            (r'Why (.*)',
             ["Why don't you tell me the reason why {0}?",
              "Why do you think {0}?"]),

            (r'I want (.*)',
             ["What would it mean to you if you got {0}?",
              "Why do you want {0}?",
              "What would you do if you got {0}?",
              "If you got {0}, then what would you do?"]),

            (r'(.*) mother(.*)',
             ["Tell me more about your mother.",
              "What was your relationship with your mother like?",
              "How do you feel about your mother?",
              "How does this relate to your feelings today?",
              "Good family relations are important."]),

            (r'(.*) father(.*)',
             ["Tell me more about your father.",
              "How did your father make you feel?",
              "How do you feel about your father?",
              "Does your relationship with your father relate to your feelings today?",
              "Do you have trouble showing affection with your family?"]),

            (r'(.*) child(.*)',
             ["Did you have close friends as a child?",
              "What is your favorite childhood memory?",
              "Do you remember any dreams or nightmares from childhood?",
              "Did the other children sometimes tease you?",
              "How do you think your childhood experiences relate to your feelings today?"]),

            (r'(.*)\?',
             ["Why do you ask that?",
              "Please consider whether you can answer your own question.",
              "Perhaps the answer lies within yourself?",
              "Why don't you tell me?"]),

            (r'(.*)',
             ["Please tell me more.",
              "Let's change focus a bit... Tell me about your family.",
              "Can you elaborate on that?",
              "Why do you say that {0}?",
              "I see.",
              "Very interesting.",
              "{0}.",
              "I see. And what does that tell you?",
              "How does that make you feel?",
              "How do you feel when you say that?"])
        ]

        self.responses_swedish = [
            (r'Jag behöver (.*)',
             ["Varför behöver du {0}?",
              "Skulle det verkligen hjälpa dig att få {0}?",
              "Är du säker på att du behöver {0}?"]),

            (r'Varför gör du inte ([^\?]*)\??',
             ["Tror du verkligen att jag inte {0}?",
              "Kanske kommer jag att {0} i framtiden.",
              "Vill du att jag ska {0}?"]),

            (r'Varför kan jag inte ([^\?]*)\??',
             ["Tycker du att du borde kunna {0}?",
              "Om du kunde {0}, vad skulle du göra då?",
              "Jag vet inte, varför kan du inte {0}?",
              "Har du verkligen försökt?"]),

            (r'Jag kan inte (.*)',
             ["Hur vet du att du inte kan {0}?",
              "Kanske skulle du kunna {0} om du försökte.",
              "Vad skulle krävas för att du ska {0}?"]),

            (r'Jag är (.*)',
             ["Kom du till mig för att du är {0}?",
              "Hur länge har du varit {0}?",
              "Hur känns det att vara {0}?"]),

            (r'Är du ([^\?]*)\??',
             ["Varför spelar det någon roll om jag är {0}?",
              "Skulle du föredra om jag inte var {0}?",
              "Kanske tror du att jag är {0}.",
              "Jag kan vara {0}, vad tror du?"]),

            (r'Vad (.*)',
             ["Varför frågar du?",
              "Hur skulle ett svar på det hjälpa dig?",
              "Vad tror du själv?"]),

            (r'Hur (.*)',
             ["Hur menar du?",
              "Kanske kan du besvara din egen fråga.",
              "Vad är det egentligen du undrar?"]),

            (r'För att (.*)|Eftersom (.*)',
             ["Är det den verkliga orsaken?",
              "Vilka andra skäl kommer du att tänka på?",
              "Gäller den orsaken i andra sammanhang?",
              "Om {0}, vad mer måste vara sant?"]),

            (r'(.*) förlåt (.*)',
             ["Det finns många tillfällen då en ursäkt inte behövs.",
              "Vilka känslor får du när du ber om ursäkt?"]),

            (r'Hej(.*)',
             ["Hej... jag lyssnar.",
              "Hej där... hur kan jag hjälpa dig?",
              "Hej, hur mår du idag?"]),

            (r'Jag tror (.*)',
             ["Tvivlar du på {0}?",
              "Tror du verkligen det?",
              "Men du är inte säker på {0}?"]),

            (r'(.*) vän(.*)',
             ["Berätta mer om dina vänner.",
              "Vad tänker du på när du tänker på en vän?",
              "Varför berättar du inte om en barndomsvän?"]),

            (r'Ja',
             ["Du verkar ganska säker.",
              "Okej, men kan du utveckla lite?"]),

            (r'(.*) dator(.*)',
             ["Pratar du egentligen om mig?",
              "Känns det märkligt att prata med en dator?",
              "Hur får datorer dig att känna?",
              "Känner du dig hotad av datorer?"]),

            (r'Är det (.*)',
             ["Tycker du att det är {0}?",
              "Kanske är det {0}, vad tror du?",
              "Om det vore {0}, vad skulle du göra?",
              "Det kan mycket väl vara {0}."]),

            (r'Det är (.*)',
             ["Du verkar väldigt säker.",
              "Om jag sa att det troligen inte är {0}, hur skulle du känna då?"]),

            (r'Kan du ([^\?]*)\??',
             ["Varför tror du att jag inte kan {0}?",
              "Om jag kunde {0}, vad då?",
              "Varför frågar du om jag kan {0}?"]),

            (r'Kan jag ([^\?]*)\??',
             ["Kanske vill du inte {0}.",
              "Vill du kunna {0}?",
              "Om du kunde {0}, skulle du det?"]),

            (r'Du är (.*)',
             ["Varför tror du att jag är {0}?",
              "Gör det dig glad att tänka att jag är {0}?",
              "Kanske vill du att jag ska vara {0}.",
              "Kanske pratar du egentligen om dig själv?"]),

            (r'Jag (?:gör|vill|kan) inte (.*)',
             ["Gör du verkligen inte {0}?",
              "Varför gör du inte {0}?",
              "Vill du göra {0}?"]),

            (r'Jag känner mig (.*)',
             ["Bra, berätta mer om de här känslorna.",
              "Känner du dig ofta {0}?",
              "När brukar du känna dig {0}?",
              "När du känner dig {0}, vad gör du då?"]),

            (r'Jag känner (.*)',
             ["Berätta mer om de känslorna.",
              "Känner du ofta {0}?",
              "När känner du {0}?"]),

            (r'Jag har (.*)',
             ["Varför berättar du att du har {0}?",
              "Har du verkligen {0}?",
              "Nu när du har {0}, vad gör du härnäst?"]),

            (r'Jag skulle (.*)',
             ["Kan du förklara varför du skulle {0}?",
              "Varför skulle du {0}?",
              "Vem mer vet att du skulle {0}?"]),

            (r'Finns det (.*)',
             ["Tror du att det finns {0}?",
              "Det är troligt att det finns {0}.",
              "Skulle du vilja att det fanns {0}?"]),

            (r'Min(?:a|t)? (.*)',
             ["Jag förstår, din {0}.",
              "Varför säger du att din {0}?",
              "När din {0}, hur känns det då?"]),

            (r'Du (.*)',
             ["Vi borde prata om dig, inte mig.",
              "Varför säger du det där om mig?",
              "Varför bryr du dig om huruvida jag {0}?"]),

            (r'Varför (.*)',
             ["Varför berättar du inte anledningen till varför {0}?",
              "Varför tror du att {0}?"]),

            (r'Jag vill (.*)',
             ["Vad skulle det betyda för dig om du fick {0}?",
              "Varför vill du ha {0}?",
              "Vad skulle du göra om du fick {0}?",
              "Om du fick {0}, vad skulle du göra då?"]),

            (r'(.*) mamma(.*)|(.*) mor(.*)',
             ["Berätta mer om din mamma.",
              "Hur var din relation med din mamma?",
              "Hur känner du för din mamma?",
              "Hur hänger det här ihop med hur du känner idag?",
              "Bra familjerelationer är viktiga."]),

            (r'(.*) pappa(.*)|(.*) far(.*)',
             ["Berätta mer om din pappa.",
              "Hur fick din pappa dig att känna?",
              "Hur känner du för din pappa?",
              "Relaterar din relation till din pappa till hur du känner idag?",
              "Har du svårt att visa känslor i din familj?"]),

            (r'(.*) barndom(.*)|(.*) barn(.*)',
             ["Hade du nära vänner som barn?",
              "Vilket är ditt favoritminne från barndomen?",
              "Minns du några drömmar eller mardrömmar från barndomen?",
              "Retade de andra barnen dig ibland?",
              "Hur tycker du att dina barndomsupplevelser hänger ihop med hur du känner idag?"]),

            (r'(.*)\?',
             ["Varför frågar du det?",
              "Fundera på om du kan svara på din egen fråga.",
              "Kanske finns svaret inom dig?",
              "Varför berättar du inte för mig?"]),

            (r'(.*)',
             ["Berätta mer.",
              "Låt oss byta fokus lite... berätta om din familj.",
              "Kan du utveckla det?",
              "Varför säger du att {0}?",
              "Jag förstår.",
              "Väldigt intressant.",
              "{0}.",
              "Jag förstår. Och vad säger det dig?",
              "Hur får det dig att känna?",
              "Hur känner du när du säger det?"])
        ]

        self.reflections = {
            "am": "are", "was": "were",
            "i": "you", "i'd": "you would", "i've": "you have", "i'll": "you will",
            "my": "your", "are": "am", "you've": "i have", "you'll": "i will",
            "your": "my", "yours": "mine", "you": "me", "me": "you",
            "jag": "du", "mig": "dig", "min": "din", "mitt": "ditt", "mina": "dina",
            "du": "jag", "dig": "mig", "din": "min", "ditt": "mitt", "dina": "mina"
        }

    def get_active_rules(self):
        """Return language-specific response rules."""
        return self.responses_swedish if self.language == "sv" else self.responses_english

    def respond(self, user_statement):
        """Generate ELIZA-style reply based on regex pattern matching."""
        for regex_pattern, possible_replies in self.get_active_rules():
            match = re.search(regex_pattern, user_statement, re.IGNORECASE)
            if match:
                template = random.choice(possible_replies)
                fills = [self.reflect_text(g) for g in match.groups() if g is not None]
                return template.format(*fills)
        return "I'm not sure I understand you fully." if self.language == "en" else "Jag är inte säker på att jag förstår dig helt."

    def reflect_text(self, fragment):
        """Flip pronouns/perspective (e.g., 'I' -> 'you')."""
        if fragment is None:
            return ""
        words = re.findall(r"\b[\wåäöÅÄÖ']+\b", fragment.lower())
        reflected = [self.reflections.get(w, w) for w in words]
        return " ".join(reflected)


# ---------------------------------------------------------
# Input/output helpers
# ---------------------------------------------------------
def lang_to_bcp47(active_language):
    """Convert 'en'/'sv' to full language tag (used for TTS)."""
    return "sv-SE" if active_language == "sv" else "en-US"

def get_user_input(active_language):
    """Get user input: typed or spoken (push-to-talk)."""
    print("> ", end="", flush=True)
    first = get_single_key()

    # Speech input
    if first == " ":
        audio = record_while_holding_space(already_pressed=True)
        if audio.size == 0:
            print("(no speech captured; hold SPACE to talk)")
            return None
        lang_code = "sv" if active_language == "sv" else "en"
        raw = transcribe_audio_whisper(audio, lang_code).strip()
        if not raw:
            print("(didn't catch that)")
            return None
        print(format_sentence(raw))
        return raw, raw.lower()

    # Typed input
    print(first, end="", flush=True)
    rest = sys.stdin.readline()
    raw = (first + rest).strip()
    if not raw:
        return None
    return raw, raw.lower()


# ---------------------------------------------------------
# Main program loop
# ---------------------------------------------------------
def main():
    session_number = 1
    tts_prepare(en_voice="Zira", sv_voice="Bengt")  # Pick voices

    # GPU check for Whisper
    import importlib
    torch_spec = importlib.util.find_spec("torch")
    use_gpu = False
    if torch_spec:
        torch = importlib.import_module("torch")
        use_gpu = torch.cuda.is_available()

    # Initialize ASR model
    asr_init(model_size="medium", use_gpu=use_gpu)

# Available models: tiny, base, small, medium, large-v2.

# Smaller = faster but less accurate.
# Larger = slower but more accurate.
    active_language = "en"
    eliza_bot = Eliza(language=active_language)

# Clear any setup output before showing user prompts
    os.system("cls" if os.name == "nt" else "clear")
    print("""
                             WELCOME TO

    EEEEEEEE       LLL         IIIII          ZZZZZZZ       AAAAAAA
    EEEEEEEE       LLL          III              ZZZ       AAA   AAA
    EEE            LLL          III             ZZZ        AAA   AAA
    EEEEEEE        LLL          III            ZZZ         AAAAAAAAA
    EEEEEEE        LLL          III           ZZZ          AAAAAAAAA
    EEE            LLL          III          ZZZ           AAA   AAA
    EEEEEEE        LLLLLLL      III         ZZZ            AAA   AAA
    EEEEEEE        LLLLLLL     IIIII       ZZZZZZZ         AAA   AAA
    """)


    while True:
        print(f"--- Session {session_number} ---")
        session_number += 1
        print("Hello! Hold SPACE to talk or type to write. Say 'quit'/'slut' to exit.")
        active_language = "en"
        eliza_bot = Eliza(language=active_language)

        while True:
            user_data = get_user_input(active_language)
            if user_data is None:
                continue
            user_text_raw, user_text = user_data

            # Exit check
            words = re.findall(r"\b[\wåäö]+\b", user_text)
            if any(w in QUIT_WORDS for w in words):
                farewells = FAREWELLS_SV if active_language == "sv" else FAREWELLS_EN
                farewell = format_sentence(random.choice(farewells))
                print("ELIZA:", farewell)
                speak(farewell, lang=active_language)
                time.sleep(2)
                os.system("cls" if os.name == "nt" else "clear")
                break

            # Switch language if strong cues
            strong = detect_language_strong(user_text)
            if strong and strong != active_language:
                active_language = strong
                eliza_bot.language = active_language

            # Respond via ELIZA
            reply = format_sentence(eliza_bot.respond(user_text))
            print(f"ELIZA: {reply}")
            speak(reply, lang=active_language)



if __name__ == "__main__":
    main()