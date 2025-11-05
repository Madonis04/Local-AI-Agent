# voice/voice_interface.py
import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import pyttsx3
import re
from pathlib import Path
from datetime import datetime
import threading
import time

from config_manager import config
from logger import logger


class VoiceInterface:
    """
    Voice interface for the AI agent with speech-to-text and text-to-speech.
    """
    
    def __init__(self):
        self.enabled = config.getboolean('Voice', 'enabled', fallback=False)
        
        if not self.enabled:
            logger.info("Voice interface disabled in config")
            return
        
        logger.info("Initializing voice interface...")
        
        # Audio settings
        self.sample_rate = config.getint('Voice', 'sample_rate', fallback=16000)
        self.channels = 1
        self.recording = False
        self.audio_data = []
        
        # TTS threading lock
        self.tts_lock = threading.Lock()
        self.tts_busy = False
        
        # Create audio directory
        data_dir = Path(config.get('Paths', 'data_directory', fallback='.agent_data'))
        self.audio_dir = data_dir / 'audio'
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Whisper (Speech-to-Text)
        self._init_whisper()
        
        # Initialize TTS (Text-to-Speech)
        self._init_tts()
        
        logger.info("Voice interface initialized successfully")
    
    def _init_whisper(self):
        """Initialize Whisper speech recognition."""
        try:
            model_size = config.get('Voice', 'whisper_model', fallback='base')
            logger.info(f"Loading Whisper model: {model_size}")
            
            self.whisper_model = whisper.load_model(model_size)
            logger.info(f"Whisper model loaded: {model_size}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            self.enabled = False
            raise
    
    def _init_tts(self):
        """Initialize text-to-speech engine."""
        try:
            # Store TTS engine as None initially
            self.tts_engine = None
            
            # Get TTS configuration
            self.tts_rate = config.getint('Voice', 'speech_rate', fallback=150)
            self.tts_volume = config.getfloat('Voice', 'speech_volume', fallback=0.9)
            self.tts_voice_gender = config.get('Voice', 'voice_gender', fallback='male')
            
            logger.info("TTS engine will be initialized per-use to avoid threading issues")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.enabled = False
            raise
    
    def _get_tts_engine(self):
        """Get or create a TTS engine instance (thread-safe)."""
        try:
            # Create new engine instance
            engine = pyttsx3.init()
            
            # Configure
            engine.setProperty('rate', self.tts_rate)
            engine.setProperty('volume', self.tts_volume)
            
            # Set voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if self.tts_voice_gender.lower() in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            return engine
            
        except Exception as e:
            logger.error(f"Error creating TTS engine: {e}")
            return None
    
    def _clean_text_for_speech(self, text):
        """
        Clean text to make it suitable for TTS.
        Removes emojis, URLs, symbols, and summarizes long content.
        
        Args:
            text: Original text
        
        Returns:
            Cleaned text suitable for speech
        """
        # Remove emojis (Unicode ranges)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters and symbols
        text = re.sub(r'[=\-_|]+', '', text)
        
        # Remove file paths (e.g., agent_data\screenshots\...)
        text = re.sub(r'[a-zA-Z]:\\[\w\\\-\.]+', 'the file', text)
        text = re.sub(r'[\w\-]+\\[\w\\\-\.]+', 'the file', text)
        
        # Remove multiple spaces/newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Handle specific response types
        if 'Screenshot saved' in text:
            return "Screenshot saved successfully. Check your screen for details."
        
        if 'Reminder set' in text:
            # Extract just the time
            match = re.search(r'Reminder set for (\d{1,2}:\d{2} [AP]M)', text)
            if match:
                return f"Reminder set for {match.group(1)}."
            return "Reminder set successfully."
        
        if 'Search Results' in text:
            lines = text.split('\n')
            results = []
            count = 0
            for line in lines:
                if line.strip() and count < 3:
                    if line.strip() and not line.startswith('http'):
                        results.append(line.strip())
                        if line.strip().startswith(('1.', '2.', '3.')):
                            count += 1
            
            if results:
                return "I found these results: " + ". ".join(results[:6])
        
        if 'Last' in text and 'conversations' in text:
            return "I found your recent conversation history. Please check the screen for details."
        
        # Limit length
        max_length = 500
        if len(text) > max_length:
            text = text[:max_length] + "... Please check the screen for full details."
        
        # Clean up extra spaces
        text = text.strip()
        
        return text
    
    def record_audio(self, duration=None):
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds (None for press-to-stop)
        
        Returns:
            Path to saved audio file
        """
        if not self.enabled:
            return None
        
        try:
            logger.info("Recording audio... (Press Enter to stop)")
            
            # Record audio
            self.audio_data = []
            self.recording = True
            
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio recording status: {status}")
                if self.recording:
                    self.audio_data.append(indata.copy())
            
            # Start recording
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback
            ):
                if duration:
                    sd.sleep(int(duration * 1000))
                else:
                    input()  # Wait for Enter key
            
            self.recording = False
            
            # Combine audio chunks
            if not self.audio_data:
                logger.warning("No audio data recorded")
                return None
            
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.audio_dir / f"recording_{timestamp}.wav"
            
            sf.write(audio_path, audio_array, self.sample_rate)
            logger.info(f"Audio saved: {audio_path}")
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            self.recording = False
            return None
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Transcribed text
        """
        if not self.enabled:
            return None
        
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                str(audio_path),
                language=config.get('Voice', 'language', fallback='en'),
                fp16=False  # Use FP32 for CPU
            )
            
            text = result['text'].strip()
            logger.info(f"Transcription: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def speak(self, text, clean=True):
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            clean: Whether to clean text before speaking
        """
        if not self.enabled:
            return
        
        # Wait if TTS is busy
        with self.tts_lock:
            if self.tts_busy:
                logger.warning("TTS busy, skipping speech")
                return
            
            self.tts_busy = True
        
        try:
            # Clean text for speech if requested
            if clean:
                speech_text = self._clean_text_for_speech(text)
            else:
                speech_text = text
            
            if not speech_text or len(speech_text.strip()) == 0:
                logger.warning("No speakable text after cleaning")
                return
            
            logger.info(f"Speaking: {speech_text[:100]}...")
            
            # Create new TTS engine instance
            engine = self._get_tts_engine()
            if not engine:
                logger.error("Could not create TTS engine")
                return
            
            # Speak synchronously
            engine.say(speech_text)
            engine.runAndWait()
            
            # Stop and delete engine
            engine.stop()
            del engine
            
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
        finally:
            # Release lock
            with self.tts_lock:
                self.tts_busy = False
            time.sleep(0.1)  # Small delay to prevent rapid TTS calls
    
    def voice_input(self):
        """
        Get voice input from user (record + transcribe).
        
        Returns:
            Transcribed text
        """
        if not self.enabled:
            return None
        
        # Record audio
        audio_path = self.record_audio()
        
        if not audio_path:
            return None
        
        # Transcribe
        text = self.transcribe_audio(audio_path)
        
        return text
    
    def voice_output(self, text):
        """
        Output text as speech.
        
        Args:
            text: Text to speak
        """
        if not self.enabled:
            return
        
        self.speak(text, clean=True)
    
    def test_voice(self):
        """Test voice interface."""
        if not self.enabled:
            print("Voice interface is disabled")
            return
        
        print("\n🎤 Testing Voice Interface...")
        print("=" * 60)
        
        # Test TTS
        print("\n1. Testing Text-to-Speech...")
        self.speak("Hello! I am your AI assistant. Voice interface is working correctly.", clean=False)
        
        # Test STT
        print("\n2. Testing Speech-to-Text...")
        print("Say something when ready, then press Enter to stop recording.")
        input("Press Enter to start recording...")
        
        text = self.voice_input()
        if text:
            print(f"You said: {text}")
            self.speak(f"I heard you say: {text}", clean=False)
        else:
            print("Could not transcribe audio")
        
        print("\n✅ Voice interface test complete!")
