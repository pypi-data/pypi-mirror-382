from setuptools import setup, find_packages

with open("README.md","r",encoding="utf-8") as f:
    description = f.read()

setup(
    name='vachanatts',
    version='0.0.7',
    packages=find_packages(),
    package_data={
        'vachanatts': ['data/*'],
    },
    include_package_data=True,
    install_requires=[
        "pythainlp",
        "ssg",
        "onnxruntime"
    ],
    description="VachanaTTS Text-to-Speech ภาษาไทย รวดเร็วและใช้งานง่าย.",
    long_description=description,
    long_description_content_type="text/markdown",
)
