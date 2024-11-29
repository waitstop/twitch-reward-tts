from io import BytesIO
from os import makedirs, path, remove
from flask import Flask, after_this_request, request, send_file
import pyttsx3
import uuid
from rvc_python.infer import RVCInference
from constants import MODEL_PATHS, AUDIO_PATH


tts = pyttsx3.init()
rvc = RVCInference()
app = Flask(__name__)

def text_to_speech(text: str) -> str:
    makedirs(AUDIO_PATH, exist_ok=True)
    output_path = path.join(AUDIO_PATH, f"{uuid.uuid4()}.mp3")
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

def clone_voice(input_path: str, output_path: str, model_path: str) -> str:
    rvc.load_model(model_path)
    rvc.infer_file(input_path, output_path)
    rvc.unload_model()
    return output_path

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()

    text = data['text']

    model = data.get('model', 'villager')
    if model not in MODEL_PATHS:
        return {"message": f"Модель '{model}' не найдена."}, 400
    model = MODEL_PATHS[data['model']]

    audio_file = text_to_speech(text)
    processed_voice = clone_voice(
        audio_file,
        path.join(AUDIO_PATH, f"{uuid.uuid4()}.mp3"),
        model
        )
    
    with open(processed_voice, 'rb') as f:
        audio_data = BytesIO(f.read())

    @after_this_request
    def _(response):
        try:
            remove(audio_file)
            remove(processed_voice)
        except Exception as e:
            print(f"Ошибка при удалении файлов: {e}")
        return response
    
    return send_file(audio_data, mimetype="audio/mpeg", as_attachment=True, download_name="processed_voice.mp3")


if __name__ == "__main__":
    app.run(debug=True)