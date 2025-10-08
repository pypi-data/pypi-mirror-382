from setuptools import setup, find_packages

setup(
    name='package',                # 👈 your package name
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'boto3',
        'sqlalchemy',
        'numpy',
        'matplotlib',
        'requests'
    ],
    description='A data processing utility for analytics and cloud operations',
    author='Sanidhya Agrawal',                     # 👈 your name
    python_requires='>=3.8',
)
