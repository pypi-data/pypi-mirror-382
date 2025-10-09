from setuptools import setup, find_packages

# Load the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ImtiazAnalysis',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
    ],
    # Metadata for PyPI
    author='Imtiaz (Your Name)',
    author_email='imtiazkarachi6@gmail.com',
    description='An automated library for comprehensive data preprocessing and Exploratory Data Analysis (EDA).',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.6',
)