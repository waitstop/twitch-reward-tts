from os import makedirs, path
from flask import Flask, request, send_file
import pyttsx3
import uuid
import torch.nn as nn

from rvc_model import VoiceConversionModel


tts = pyttsx3.init()
app = Flask(__name__)

def text_to_speech(text: str) -> str:
    makedirs("audio_files", exist_ok=True)
    output_path = path.join("audio_files", f"{uuid.uuid4()}.mp3")
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    text = data['text']
    audio_file = text_to_speech(text)
    return send_file(audio_file, mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(debug=True)