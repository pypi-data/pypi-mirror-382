from setuptools import setup, find_packages

setup(
    name='mlinsightlab',
    version='0.0.36',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=open('requirements.txt').read().splitlines(),
    author='MLIL Team',
    description='Your Open Source Data Science and MLOps Platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MLInsightLab/MLInsightLab-Python-SDK',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
