from setuptools import setup, find_packages

setup(
    name="buzuai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-socketio[client]>=5.0.0",
    ],
    python_requires=">=3.7",
)
