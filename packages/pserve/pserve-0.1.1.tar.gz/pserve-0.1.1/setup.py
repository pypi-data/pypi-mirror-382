from setuptools import setup, find_packages

setup(
    name="pserve",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "cryptography"
    ],
    entry_points={
        "console_scripts": [
            "phttps = phttps.__main__:main",
            "phttp = phttp.__main__:main",
        ],
    },
    python_requires='>=3.12',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    
    # -----------------------------
    # Extra metadata for PyPI
    # -----------------------------
    author="Saimon",
    author_email="me@nextsaimon.com",
    description="A simple HTTP/HTTPS server package with self-signed certificates",
    url="https://github.com/nextsaimon/pserve",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Security :: Cryptography",
    ],
)
