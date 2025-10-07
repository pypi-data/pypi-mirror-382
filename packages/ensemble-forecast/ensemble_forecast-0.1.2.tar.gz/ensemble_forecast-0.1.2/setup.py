from setuptools import setup, find_packages
from pathlib import Path

# Read README safely
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "Ensemble Forecasting library combining classical and ML models."

setup(
    name='ensemble_forecast',
    version='0.1.2',
    author='Ashay Thamankar',
    author_email='ashaytesting@gmail.com',
    description='A lightweight ensemble forecasting library combining classical and ML models.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    include_package_data=True, 
    install_requires=[
        'numpy==1.24.3',
        'pandas==2.0.3',
        'python-dateutil==2.8.2',
        'scipy==1.10.1',
        'Cython==0.29.36',
        'statsmodels==0.14.1',
        'scikit-learn==1.3.2',
        'pmdarima==2.0.4',
        'tbats==1.1.3',
        'statsforecast==1.6.0',
        'prophet==1.1.4',
        'tensorflow==2.13.0',
    ],
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='forecasting, ensemble, time series, machine learning, prophet, ARIMA, SARIMA, Croston, LSTM, neural network, ETS, TBATS',
)
