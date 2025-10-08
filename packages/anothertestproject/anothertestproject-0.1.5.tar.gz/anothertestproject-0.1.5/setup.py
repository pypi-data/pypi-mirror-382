from setuptools import setup, find_packages

setup(
    name="anothertestproject",
    version="0.1.5",
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
    package_data={
        "anothertestproject": [
            "*.dll",
            "*.exe",
            "binaries/*.exe",
            "binaries/*.dll",
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
)