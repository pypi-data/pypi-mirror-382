
from setuptools import setup, find_packages

setup(
    name='autopretorch',
    version='0.1.0',
    description='AutoPreTorch - extended preprocessing library for PyTorch',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'torch',
        'pandas',
        'numpy',
        'scikit-learn',
        'joblib'
    ],
    python_requires='>=3.8',
)
