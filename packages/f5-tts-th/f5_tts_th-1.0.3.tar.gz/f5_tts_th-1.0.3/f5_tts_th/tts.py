from cached_path import cached_path
from .utils_infer import load_model,load_vocoder,infer_process,preprocess_ref_audio_text

hf_cache_dir = None
vocoder_name = "vocos"
model_type = "v1"

def load_f5tts(model_type="v1"):
    if model_type == "v1":
        ckpt_path = str(
                cached_path(f"hf://VIZINTZOR/F5-TTS-THAI/model_1000000.pt", cache_dir=hf_cache_dir)
            )
        vocab_path = str(cached_path("hf://VIZINTZOR/F5-TTS-THAI/vocab.txt", cache_dir=hf_cache_dir))
        model_cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, text_mask_padding=False, conv_layers=4, pe_attn_head=1)
        model = load_model(model_cfg,ckpt_path,mel_spec_type=vocoder_name,vocab_file=vocab_path)
    elif model_type == "v2":
        ckpt_path = str(
                cached_path(f"hf://VIZINTZOR/F5-TTS-TH-V2/model_250000.pt", cache_dir=hf_cache_dir)
            )
        vocab_path = str(cached_path("hf://VIZINTZOR/F5-TTS-TH-V2/vocab.txt", cache_dir=hf_cache_dir))
        model_cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, text_mask_padding=True, conv_layers=4, pe_attn_head=None)
        model = load_model(model_cfg,ckpt_path,mel_spec_type=vocoder_name,vocab_file=vocab_path)
    return model

f5_model = load_f5tts(model_type)
vocoder = load_vocoder(vocoder_name)

def infer(ref_audio,ref_text,gen_text,step=32,speed=1.0,cfg=2.0):

    ref_audio, ref_text = preprocess_ref_audio_text(ref_audio, ref_text)

    wav , sr, _ = infer_process(
        ref_audio,
        ref_text,
        gen_text,
        f5_model,
        vocoder,
        mel_spec_type = vocoder_name,
        nfe_step=step,
        speed=speed,
        cfg_strength=cfg,
        set_max_chars=300,
        use_ipa=False if model_type == "v1" else True
        )

    return wav

    