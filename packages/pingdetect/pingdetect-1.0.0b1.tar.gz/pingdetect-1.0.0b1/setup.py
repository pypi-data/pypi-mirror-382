from setuptools import setup, find_packages
from pathlib import Path

DESCRIPTION = 'Utility to perform object detection on sonar imagery.'
LONG_DESCRIPTION = Path('README.md').read_text()
packageName = 'pingdetect'

exec(open(f'{packageName}/version.py').read())

setup(
    name=packageName,
    version=__version__,
    author="Cameron Bodine",
    author_email="bodine.cs@gmail.email",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    # data_files=[("pingmapper_config", ["pingmapper/default_params.json"])],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Oceanography",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Hydrology"
        ],
    keywords=[
        "pingmapper",
        "sonar",
        "ecology",
        "remotesensing",
        "sidescan",
        "sidescan-sonar",
        "aquatic",
        "humminbird",
        "lowrance",
        "gis",
        "oceanography",
        "limnology",],
    python_requires="<3.13",
    install_requires=['pinginstaller', 'pingwizard'],
    project_urls={
        "Issues": "https://github.com/PINGEcosystem/PINGDetect/issues",
        "GitHub":"https://github.com/PINGEcosystem/PINGDetect",
        # "Homepage":"https://PINGEcosystem.github.io/PINGDetect/",
    },
)