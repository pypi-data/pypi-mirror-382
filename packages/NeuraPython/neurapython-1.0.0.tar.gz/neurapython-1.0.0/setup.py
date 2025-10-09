from setuptools import setup, find_packages

setup(
    name="NeuraPython",
    version="1.0.0",
    author="Ibrahim Shahid",
    author_email="ibrahimshahid7767@gmail.com",
    description="A multi-purpose AI and utility module for Python — includes GUI, file handling, math, media, and OS integration.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # finds your 'neurapython' package automatically
    install_requires=[
        "pyttsx3",
        "speechrecognition",
        "PyQt6",
        "pandas",
        "pygame",
        "opencv-python",
        "matplotlib",
        "pillow",
    ],
    python_requires='>=3.7',
)
