from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="layernet",  # Nome do pacote no PyPI
    version="0.0.5",
    author="Leonardo Nery",
    author_email="leonardonery@gmail.com",
    description="Biblioteca modular de Machine Learning em um único arquivo, inspirada em Keras/TensorFlow.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["LayerNet"],  # Apenas o arquivo único
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tensorflow>=2.9.0",
        "keras>=2.9.0",
        "numpy",
        "matplotlib",
        "pandas",
        "networkx",
        "sympy",
        "pyqt5",
    ],
    keywords="machine-learning deep-learning keras tensorflow neural-networks ai",
)
