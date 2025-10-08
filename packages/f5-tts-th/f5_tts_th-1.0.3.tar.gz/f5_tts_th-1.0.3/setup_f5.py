from setuptools import setup, find_packages

with open("README_f5tts.md","r",encoding="utf-8") as f:
    description = f.read()

setup(
    name='f5-tts-th',
    version='1.0.3',
    packages=find_packages(),
    package_data={
        'f5_tts_th': ['data/*'],
    },
    include_package_data=True,
    install_requires=[
        "cached_path",
        "jieba",
        "librosa",
        "matplotlib",
        "numpy<=1.26.4",
        "pydub",
        "pypinyin",
        "soundfile",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "torchdiffeq",
        "tqdm>=4.65.0",
        "transformers",
        "vocos",
        "x_transformers>=1.31.14",
        "pythainlp",
        "python-crfsuite",
        "ssg"
    ],
    description="Open Source Text-to-Speech (TTS) ภาษาไทย — เครื่องมือสร้างเสียงพูดจากข้อความด้วยเทคนิค Flow Matching",
    long_description=description,
    long_description_content_type="text/markdown",
)
