import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-epic",
    version="0.6.10",
    packages=find_packages(),
    # requirements for running just KiCad interfacing code (epic.kicad):
    install_requires=["egauge-python>=0.9.8", "sexpdata"],
    # additional requirements for running the EPIC server:
    extras_require={
        "server": [
            "django>=2.0.0",
            "django-autocomplete-light>=3",
            "django-bootstrap3-datetimepicker-2",
            "django-crispy-forms",
            "django-filter",
            "djangorestframework",
            "openpyxl",
            "tablib>=3.0.0",
        ]
    },
    include_package_data=True,
    license="MIT License",  # example license
    description="A Django app to manage electronic parts inventories "
    "for PCB manufacturing.",
    long_description=README,
    url="https://bitbucket.org/egauge/epic/",
    author="David Mosberger-Tang",
    author_email="davidm@egauge.net",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
)
