from setuptools import setup, find_packages

setup(
    name="tutorial_pip_install_ry",
    version="0.1.0",
    author="Runyao Yu",
    author_email="runyao.yu@tudelft.nl",
    description="Tutorial example: Keras MLP with Hugging Face-hosted data and model",
    packages=find_packages(),
    install_requires=[
        "tensorflow>=2.12",
        "scikit-learn>=1.0",
        "numpy>=1.22",
        "pandas>=1.3",
        "huggingface_hub>=0.20.0",
    ],
    python_requires=">=3.8",
    license="MIT",
    url="https://huggingface.co/RunyaoYu",
)
