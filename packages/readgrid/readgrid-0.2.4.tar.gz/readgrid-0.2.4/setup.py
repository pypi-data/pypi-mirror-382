from setuptools import setup, find_packages

setup(
    name="readgrid",
    version="0.2.4",
    author="David Jeremiah",
    author_email="flasconnect@gmail.com",
    description="A document layout pipeline for detecting tables, images, and structured extraction.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/davidkjeremiah/readgrid",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "Pillow",
        "google-genai",
        "ipywidgets",
        "IPython",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    license_files=("LICENSE",),
    python_requires=">=3.8",
)
