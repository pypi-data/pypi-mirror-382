from setuptools import setup, find_packages

setup(
    name='virus_py',
    version='0.0.7',
    packages=find_packages(),
    author='VIRUS',
    description='Bypass cookies and user agent protection',
    long_description='...',
    long_description_content_type='text/plain',
    install_requires=['requests'],
    python_requires='>=3.6',
)
