from setuptools import setup, find_packages

setup(
    name='autofuzzts',  # must be all lowercase on PyPI
    version='0.1.0',
    author='Jan Timko',
    author_email='jantimko16@gmail.com',  # avoid <at> for metadata
    description='Automated fuzzy time series forecasting library',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jtimko16/AutoFuzzTS',
    packages=find_packages(exclude=['tests*', 'notebooks*']),
    install_requires=[
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "scikit-learn>=1.5.0",
        "scipy>=1.15.0",
        "xgboost>=3.0.0",
        "lightgbm>=4.6.0",
        "tpot>=1.0.0",
        "optuna>=4.3.0",
        "matplotlib>=3.10.0",
        "seaborn>=0.13.0",
        "requests>=2.32.0",
        "PyYAML>=6.0.0",
        "joblib>=1.4.0",
        "tqdm>=4.67.0"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.11',
)