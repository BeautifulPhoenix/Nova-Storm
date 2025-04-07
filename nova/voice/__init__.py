# Módulo de voz para Nova
# Este paquete gestiona la conversión de voz a texto y texto a voz

from nova.voice.speech_to_text import SpeechToText
from nova.voice.text_to_speech import TextToSpeech

__all__ = ['SpeechToText', 'TextToSpeech']