from setuptools import setup, find_packages

setup(
    name='pj_dev_helper',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'sqlalchemy==2.0.23',
        'psycopg2==2.9.9',
        'click==8.1.7',
        'networkx==3.2.1',
        'matplotlib==3.8.2',
    ],
    extras_require={
        'tests': [
            'pytest==7.4.3',
            'coverage==7.4.0',
        ],
    },
    author='ElCaptaine',
    author_email='',
    python_requires='>=3.10',
    description='A description of your project',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

