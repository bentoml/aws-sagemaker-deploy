import setuptools

install_requires = [
    "click",
    "bentoml>=0.10.0"
]

setuptools.setup(
    name="bentoml_sagemaker",
    author="bentoml.org",
    author_email="contact@bentoml.ai",
    description="BentoML sagemaker deployment plugin",
    license="Apache License 2.0",
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    url="https://github.com/bentoml/BentoML",
    packages=setuptools.find_packages(exclude=["tests*"]),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6.1",
    entry_points={
        "console_scripts": [
            "bentoml-sagemaker=bento_sagemaker:cli"
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/bentoml/BentoML/issues",
        "BentoML User Slack Group": "https://bit.ly/2N5IpbB",
        "Source Code": "https://github.com/bentoml/BentoML",
    },
)
