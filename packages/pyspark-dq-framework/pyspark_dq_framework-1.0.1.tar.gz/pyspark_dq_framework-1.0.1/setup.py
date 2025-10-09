# setup.py
from setuptools import setup, find_packages

setup(
    name='pyspark-dq-framework',
    version='1.0.1',
    author='Nitin Chaudhari',
    author_email='nitinchaudhariofficial@gmail.com',
    description='A PySpark-based Data Quality Framework using YAML-configurable checks.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nitin-chaudhari/pyspark-dq-framework',
    packages=find_packages(),
    install_requires=[
        'pyyaml'
    ],
    extras_require={
        "pyspark": ["pyspark>=3.5.5"]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ],
    python_requires='>=3.7',
    include_package_data=True
)
