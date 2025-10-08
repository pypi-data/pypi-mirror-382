from setuptools import setup, find_packages

setup(
    name="proxies-tg-wrapper",
    version="1.0.7",
    packages=find_packages(),
    install_requires=["python-telegram==0.18.0"],
    author="Ilia Abolhasani",
    author_email="abolhasani.eliya@gmail.com",
    description="A package designed to facilitate interaction with the Telegram API, specifically for managing MTProto proxies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ilia-Abolhasani/proxies-tg-wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
