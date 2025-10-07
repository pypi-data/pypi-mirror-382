import os
from setuptools import find_namespace_packages, setup

base_path = os.path.abspath(os.path.dirname(__file__))

version = "6.0.0"

core = [
    "boto3==1.34.36",
    "python-jose==3.5.0",
]
dev = [
    "pytest==7.4.3",
    "coverage==7.3.2",
    "black<=25.1.0,<26.0.0",
]
bedrock = ["PyMuPDF==1.26.0"]
all = dev + core + bedrock

setup(
    name="my_aws_helpers",
    version=version,
    author="Jarrod McCarthy",
    description="AWS Helpers",
    url="https://github.com/JarrodMccarthy/aws_helpers.git",
    platforms="any",
    packages=[
        p
        for p in find_namespace_packages(where=base_path)
        if p.startswith("my_aws_helpers")
    ],
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=True,
    install_requires=core,
    include_package_data=True,
    extras_require={"bedrock": core + bedrock, "all": all},
)
