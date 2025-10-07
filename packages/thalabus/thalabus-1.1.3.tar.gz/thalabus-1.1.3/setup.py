from setuptools import setup, find_packages

setup(
    name='thalabus',
    version='1.1.3',
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "requests"
    ],
    author='Luca Strozzi',
    author_email='luca.strozzi@t2b.ch',
    description='An SDK for the thalabus AI chatbot platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.thalabus.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
