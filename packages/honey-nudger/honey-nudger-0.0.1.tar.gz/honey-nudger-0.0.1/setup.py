from setuptools import setup, find_packages

setup(
    name='honey-nudger',
    version='0.0.1',
    author='Daniel Carpenter',
    author_email='dan@honeynudger.ai',
    description='Reserving package name for the upcoming Honey Nudger OSS project.',
    long_description='Honey Nudger OSS Beta: Artificial Sweetener For Your LLM. Official release coming soon!',
    url='https://github.com/honeynudger/honey-nudger-oss', # Update if your repo URL is different
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)