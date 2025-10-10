from setuptools import setup, find_packages

setup(
    name="saithonanen",
    version="0.1.0",
    packages=find_packages(),
    author="Manus AI",
    author_email="",
    install_requires=[
        'cryptography',
    ],
    description="A powerful and advanced encryption library.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/saithonanen",
    entry_points={
        'console_scripts': [
            'saithonanen=saithonanen.cli:main',
        ],
    },
)
