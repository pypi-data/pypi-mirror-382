from setuptools import setup, find_packages


with open("README.md", "r") as file:
    long_description = file.read()

dev_status = {
    "Alpha": "Development Status :: 3 - Alpha",
    "Beta": "Development Status :: 4 - Beta",
    "Pro": "Development Status :: 5 - Production/Stable",
    "Mature": "Development Status :: 6 - Mature",
}

setup(
    name="monsterlab",
    version="2.1.0",
    author="Robert Sharp",
    author_email="webmaster@sharpdesigndigital.com",
    description="Monster Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/BrokenShell/MonsterLab',
    license="Free for non-commercial use",
    install_requires=["pytz"],
    packages=find_packages(),
    platforms=["Darwin", "Linux"],
    classifiers=[
        dev_status["Pro"],
        "Programming Language :: Python :: 3.9",
    ],
    keywords=[
        "MonsterLab",
    ],
    python_requires=">=3.7",
)
