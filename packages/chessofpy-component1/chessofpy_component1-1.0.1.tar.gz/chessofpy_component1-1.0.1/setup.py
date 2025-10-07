from setuptools import setup, find_packages

setup(
    name="chessofpy_component1",
    version="1.0.1",
    author="cocohungandyaya",
    author_email="dickilyyiu@gmail.com",
    packages=find_packages(),
    install_requires=[
        "chess",
        "python-chess"
    ],
    python_requires='>=3.6',
)