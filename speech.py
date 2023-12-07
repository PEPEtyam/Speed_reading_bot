
import wave
import speech_recognition as sr

from pydub import AudioSegment


def convert_to_wav(input_file, output_file):
    audio = AudioSegment.from_ogg(input_file)
    audio.export(output_file, format="wav")


def recognize_speech(file_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file_path)

    with audio_file as source:
        audio_data = recognizer.record(source)

    try:
        # Используем Google Web Speech API для распознавания речи
        result = recognizer.recognize_google(
            audio_data, show_all=True, language="ru-RU")
        best_alternative = result.get('alternative', [])[
            0]['transcript'] if 'alternative' in result else ""
        return best_alternative
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка при запросе к сервису распознавания речи: {e}"


def file_duration(file_path):
    with wave.open(file_path, 'rb') as wf:
        frames = wf.getnframes()
        framerate = wf.getframerate()
        duration = frames / float(framerate)
    return duration
