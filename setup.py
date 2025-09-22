from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh.readlines() if line.strip() and not line.startswith("#")]

setup(
    name="video-intelligent-splitter",
    version="1.0.0",
    author="livoras",
    description="Automatically splits videos into segments based on scene changes using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/livoras/video_splitter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "video-splitter=video_splitter_pkg.video_splitter:main",
        ],
    },
    keywords="video processing, scene detection, AI, computer vision, video splitting",
    project_urls={
        "Bug Reports": "https://github.com/livoras/video_splitter/issues",
        "Source": "https://github.com/livoras/video_splitter",
    },
)