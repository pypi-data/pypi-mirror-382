from setuptools import setup,find_packages

# print(find_packages())
with open("README",encoding="utf-8") as f:
    md = f.read()


setup(
    name="cdebug",
    version="0.0.1.1",
    author="wayne931121",
    author_email="",
    description="debug",
    long_description=md,
    long_description_content_type="text/markdown",
    license="CC-BY-NC 4.0",
    url="https://github.com/wayne931121",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",
)