# setup.py

from setuptools import setup, find_packages
from setuptools import  find_namespace_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='antifp2',
    version='1.1.0',
    description='AntiFP2: A tool for prediction of Antifungal Proteins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_files = ('LICENSE.txt',),
    author='Pratik Shinde',
    author_email='pratiks@iiitd.ac.in',
    url='https://github.com/patrik-ackerman/antifp2/',
    packages=find_namespace_packages(where="src"),
    package_dir={'':'src'},
    package_data={'antifp2.blast_db':['**/*'],
    'antifp2.MERCI':['*'],
    'antifp2.python_scripts':['envfile'],
    'antifp2.python_scripts':['antifp2_xgboost_PAAC.pkl']},
    entry_points={'console_scripts' : ['antifp2 = antifp2.python_scripts.antifp2:main']},
    include_package_data=True,
    python_requires='>=3.12',
    install_requires=[
        'fair-esm', 'huggingface-hub', 'pandas', 'torch','biopython', 'xgboost==3.0.4', 'pfeature', 'joblib' #Add any Python dependencies here
    ]
)

