from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="learn4u",
	version="0.6.0",
	packages=find_packages(),
	install_requires=[],
	author="Alvaro Lujan",
	description="Una biblio para consultar cursos de hack4u",
	long_description_content_type="text/markdown",
	url="https://hack4u.io",
)
