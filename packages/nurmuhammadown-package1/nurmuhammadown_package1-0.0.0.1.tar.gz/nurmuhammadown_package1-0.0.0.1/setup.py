from setuptools import setup

setup(
    name="nurmuhammadown_package1",
    version="0.0.0.1",
    py_modules=["example"],
    author="Nurmuhammad Hasanov",
    author_email="youremail@example.com",
    description="A simple example package by Nurmuhammad",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/nurmuhammadown_package1/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
