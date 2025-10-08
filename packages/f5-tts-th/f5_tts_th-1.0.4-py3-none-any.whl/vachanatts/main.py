from .config import SpeechConfig
from .voice import Voice
import os 
import wave

def download_voice(url, local_path):
    import requests
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not os.path.exists(local_path):
        print(f"Downloading {url} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
    return local_path
    
def load_voice(voice_name="th_f_1"):
    
    model_filename = f"{voice_name}.onnx"
    config_filename = f"speaker_config.json"

    local_model_path = f"./voices/{model_filename}"
    local_config_path = f"./voices/{config_filename}"

    if os.path.exists(local_model_path) and os.path.exists(local_config_path):
        return Voice.load(local_model_path, local_config_path)
    else:
        model_url = f"https://huggingface.co/VIZINTZOR/VachanaTTS/resolve/main/voices/{model_filename}"
        config_url = f"https://huggingface.co/VIZINTZOR/VachanaTTS/resolve/main/speaker_config.json"

        model_path = download_voice(model_url, local_model_path)
        config_path = download_voice(config_url, local_config_path)

        return Voice.load(model_path, config_path)

loaded_voices = {}

def TTS(
    text,
    voice="th_f_1",
    output="output.wav",
    volume=1.0,
    speed=1.0,
    noise_scale=0.667,
    noise_w_scale=0.8
):

    syn_config = SpeechConfig(
        volume=volume,
        length_scale=(1 / speed), 
        noise_scale=noise_scale,
        noise_w_scale=noise_w_scale, 
    )

    if voice not in loaded_voices:
        loaded_voices[voice] = load_voice(voice)
    voice = loaded_voices[voice]
    
    with wave.open(output, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file, syn_config)