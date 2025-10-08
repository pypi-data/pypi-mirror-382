from setuptools import setup, find_packages

setup(
    name="libmysoltest",
    version="0.1.0",
    author="Ваше Имя",
    author_email="your@email.com",
    description="Описание вашей библиотеки",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)