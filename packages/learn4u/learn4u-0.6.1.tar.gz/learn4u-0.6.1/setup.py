from setuptools import setup, find_packages
from pathlib import Path

# Leer README.md como descripción larga
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="learn4u",  # Nombre del paquete en PyPI
    version="0.6.1",  # Sube versión para publicar el nuevo build
    author="Álvaro Luján",
    description="Una biblioteca ligera para consultar cursos de Hack4U desde Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",  # (Alpha, Beta, Production/Stable)
        "Intended Audience :: Developers",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords="cursos hack4u educación hacking python biblioteca",
    license="MIT",
    python_requires=">=3.7",
)

