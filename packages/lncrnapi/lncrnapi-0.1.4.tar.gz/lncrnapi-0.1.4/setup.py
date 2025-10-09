from setuptools import setup, find_namespace_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lncrnapi",  # Replace with your desired package name
    version="0.1.4",
    author="Gajendra P.S. Raghava",
    author_email="raghava@iiitd.ac.in",
    description="A CLI tool for predicting lncRNA–Protein interactions using transformer embeddings and CatBoost",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raghavagps/lncrnapi",  # Replace with your repo URL
    packages=find_namespace_packages(where="src"),
    python_requires=">=3.9",
    package_dir={"":"src"},
    package_data={'lncrnapi.model':['*']},
    install_requires=[
        "torch>=2.6.0",
        "transformers>=4.40.0",
        "catboost>=1.2",
        "joblib>=1.2",
        "tqdm>=4.65",
        "numpy>=1.24",
        "pandas>=2.0",
	"safetensors>=0.6"
    ],
    entry_points={
        "console_scripts": [
            "lncrnapi=lncrnapi.python_scripts.lncrnapi:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    include_package_data=True,
    keywords="lncrna protein interaction prediction bioinformatics catboost transformers",
)

