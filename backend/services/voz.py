'''
services/voz.py
Transcripción de audio a texto usando SpeechRecognition y Google Web Speech API.
El audio llega como bytes desde el navegador via HTTP (webm/wav/mp4).
Gratuito — no consume tokens de OpenAI.
'''

import os
import tempfile
import speech_recognition as sr


async def transcribir_audio(audio_bytes: bytes, idioma_voz: str = "es-MX") -> dict:
    '''
    Recibe bytes de audio enviados desde el navegador y retorna dict con:
    - status : success | error | no_entendido
    - texto  : transcripción resultante
    - error  : descripción del error (solo si status != success)

    Diferencia con la consola:
    - Consola usa sr.Microphone() + recognizer.listen()
    - API usa sr.AudioFile()     + recognizer.record()
    El reconocedor y recognize_google() son idénticos en ambos casos.
    '''
    tmp_path = None

    try:
        # Guardar bytes en archivo temporal que SpeechRecognition pueda leer
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)

        texto = recognizer.recognize_google(audio, language=idioma_voz)

        return {
            "status": "success",
            "texto" : texto.strip(),
        }

    except sr.UnknownValueError:
        return {
            "status": "no_entendido",
            "texto" : "",
            "error" : "El audio no pudo ser reconocido.",
        }

    except sr.RequestError as e:
        return {
            "status": "error",
            "texto" : "",
            "error" : f"Error al contactar Google Speech: {e}",
        }

    except Exception as e:
        return {
            "status": "error",
            "texto" : "",
            "error" : str(e),
        }

    finally:
        # Siempre borrar el archivo temporal, incluso si hubo error
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)