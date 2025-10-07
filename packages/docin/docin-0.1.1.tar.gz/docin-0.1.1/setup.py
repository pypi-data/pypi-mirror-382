from setuptools import setup

with open("README.md", "r") as f:
    description = f.read()

setup(
    name = "docin",
	version = "0.1.1",
	description = "A Python package for performing OCR and document indexing on legacy documents using the Mistral Ocr API.",
	author = ["Ime Inyang", "Chukwudi Asibe", "Oluwaseyi Akinbosola"],
	author_email = "alfiinyang@gmail.com",
	packages = ["ocr"],
    install_requires = ["mistralai","datauri"],
    long_description=description,
    long_description_content_type="text/markdown"
    )