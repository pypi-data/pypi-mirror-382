from setuptools import setup, find_packages

requirements = [
    "httpx==0.28.1",
    "websocket-client==1.3.1", 
    "json_minify", 
    "six",
    "websockets"
]

with open("README.md", "r", encoding="utf-8") as stream:
    long_description = stream.read()

setup(
    name="ZAmino.fix",
    author="ZOOM",
    version="1.2.4",
    description="ZAmino.fix is a modern and optimized fork of amino.fix, designed for building Amino bots, automations, and custom clients with ease and performance in mind.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.6',
    keywords=[
        "ZAmino",
        "ZAmino.fix",
        "aminoapps",
        "ZAminofix",
        "amino",
        "amino-bot",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
