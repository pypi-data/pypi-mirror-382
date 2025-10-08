import setuptools

with open("README_client.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements-client.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="LogQS",
    version="1.1.8",
    author="Nathan Margaglio",
    author_email="nmargaglio@carnegierobotics.com",
    description="A client for interacting with the LogQS Service.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carnegierobotics/LogQS",
    project_urls={
        "Bug Tracker": "https://github.com/carnegierobotics/LogQS/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(
        include=[
            "lqs",
            "lqs.client*",
            "lqs.interface*",
            "lqs.transcode*",
            "lqs.common*",
            "lqs.versions*",
        ]
    ),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "lqs=lqs.client.__main__:main",
            "lqs.client=lqs.client.__main__:main",
            "lqs.transcode=lqs.transcode.__main__:main",
        ],
    },
    install_requires=requirements,
)
