from setuptools import setup

setup(name = "docin",
	version = "0.1.0",
	description = "A Python package for performing OCR and document indexing on legacy documents using the Mistral Ocr API.",
	author = ["Ime Inyang", "Chukwudi Asibe", "Oluwaseyi Akinbosola"],
	author_email = "alfiinyang@gmail.com",
	packages = ["ocr"],
    install_requires = ["mistralai","datauri"])