# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()

with open(os.path.join(here, "requirements.txt")) as f:
    requires = f.read()

with open(os.path.join(here, "CURRENT_VERSION")) as f:
    current_version = f.read().splitlines()[0].strip()


entry_points = {
    "paste.app_factory": [
        "worker = caerp_celery:worker",
        "scheduler = caerp_celery:scheduler",
    ]
}

setup(
    name="caerp_celery",
    version=current_version,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="GPLv3",
    description="caerp_celery",
    long_description=README,
    long_description_content_type="text/x-rst",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Coopérer Pour Entreprendre",
    author_email="contact@endi.coop",
    url="https://framagit.org/caerp/caerp_celery",
    keywords="web wsgi bfg pylons pyramid celery",
    zip_safe=False,
    install_requires=requires,
    entry_points=entry_points,
)
