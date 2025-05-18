import speech_recognition
from vacore import VACore


def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        try:
            audio = recognizer.listen(microphone, 5, 5)

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        try:
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        except speech_recognition.RequestError:
            print("Check your Internet Connection, please")

        return recognized_data


if __name__ == "__main__":
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    with microphone:
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

    core = VACore()
    core.init_with_plugins()

    while True:
        voice_input_str = record_and_recognize_audio()

        if voice_input_str != "":
            core.run_input_str(voice_input_str)

        core._update_timers()
