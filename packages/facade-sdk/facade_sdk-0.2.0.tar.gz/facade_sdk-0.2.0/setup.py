from setuptools import setup, find_packages

setup(
    name="facade-sdk",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["paho-mqtt>=1.6.1",],
    description="SDK for FACADE system API",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)