from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ariai",
    version="0.1.0",
    author="AriAI Team",
    author_email="your.email@example.com",  # You should update this
    description="A flexible chatbot framework supporting multiple AI providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ariai",  # Update with your GitHub if you have one
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=0.27.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "rich>=13.0.0",
        "gradio>=4.0.0",
    ],
)