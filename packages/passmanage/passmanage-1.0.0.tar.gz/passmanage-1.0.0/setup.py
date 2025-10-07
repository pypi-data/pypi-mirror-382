from setuptools import find_packages, setup

setup(
    name="passmanage",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["cryptography", "bcrypt"],
    entry_points={
        "console_scripts": [
            "pass = passman.main:main",
        ],
    },
    author="Deepak kumar saini",
    author_email="ds954642@gmail.com",
    description="A simple CLI password manager with AES encryption",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/deepak-nkit/Password-Manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
